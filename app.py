"""
app.py - AI 工具箱 Gradio 前端

基于阿里云百炼平台的 AI 能力，提供 Web UI 交互界面。
不改动任何现有代码，复用 config/settings.py 和 core/utils.py 工具层。

Author: 仗剑天涯
Date: 2026/6/30
"""

# ==================== 标准库 ====================
import base64
import json
import os
import sys
import time

# console=False (Windows GUI) 时 sys.stdout/stderr 为 None，
# uvicorn 日志初始化 isatty() 会崩溃，必须提前重定向
# 重定向到日志文件而非丢弃，确保错误信息可追踪
if sys.stdout is None:
    _early_log = Path(sys.executable).parent / "gradio_debug.log"
    sys.stdout = open(str(_early_log), "a")
if sys.stderr is None:
    _early_log = Path(sys.executable).parent / "gradio_debug.log"
    sys.stderr = open(str(_early_log), "a")
import wave
from datetime import datetime
from pathlib import Path

# ==================== 第三方库 ====================
import gradio as gr
import dashscope
from dashscope import Generation, MultiModalConversation, VideoSynthesis
from dashscope.audio.tts_v2 import SpeechSynthesizer, VoiceEnrollmentService
from dashscope.aigc.image_generation import ImageGeneration
from dashscope.api_entities.dashscope_response import Message
from openai import OpenAI
import requests
import numpy as np
import soundfile as sf

# ==================== 项目模块 ====================
from config.settings import get_api_key, get_output_dir
from core.utils import (
    get_voices_for_llm_version,
    get_language_code,
    base64_encode_by_name_v2,
    get_file_path_by_time,
    get_timestamp_by_time,
    get_file_by_url,
)

# ==================== 启动诊断日志 ====================
import logging

# 强制行缓冲 —— 确保控制台实时输出，不会因缓冲区导致"无显示"
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 日志文件写入 exe 同目录（frozen）或项目根目录（开发）
_LOG_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
_LOG_FILE = _LOG_DIR / "gradio_debug.log"
logging.basicConfig(
    filename=str(_LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("=== 程序启动，Python %s ===", sys.version)
print(f"[LOG] 诊断日志写入: {_LOG_FILE}", flush=True)

# ==================== 预加载配置 ====================
VOICES_COSYVOICE = get_voices_for_llm_version("cosyvoice-v2")
VOICES_QWEN_TTS = get_voices_for_llm_version("qwen3-tts-flash")
VOICES_TRANSLATE = get_voices_for_llm_version("qwen3-livetranslate-flash")
VOICES_OMNI = get_voices_for_llm_version("qwen3.5_omni_plus")
LANGUAGES = list(get_language_code().keys())
LANG_CHOICES = [
    "中文", "英语", "德语", "意大利", "葡萄牙语",
    "西班牙语", "日语", "韩语", "法语", "俄语",
]

# ==================== 辅助函数 ====================

def _encode_file_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _make_cosyvoice_voice_choices():
    """cosyvoice-v2 的 value 是字符串，其他模型是 dict"""
    items = []
    for k, v in VOICES_COSYVOICE.items():
        label = v if isinstance(v, str) else v.get("content", str(v))
        items.append(f"{k} - {label}")
    return items


def _make_qwen_tts_voice_choices():
    """qwen3-tts-flash 的 value 是 dict，有 content 和 skill"""
    items = []
    for k, v in VOICES_QWEN_TTS.items():
        label = v["content"] if isinstance(v, dict) else v
        items.append(f"{k} - {label}")
    return items


def _make_translate_voice_choices():
    """qwen3-livetranslate-flash 的 value 是 dict"""
    items = []
    for k, v in VOICES_TRANSLATE.items():
        if isinstance(v, dict):
            skill = v.get("skill", "")
            if isinstance(skill, list):
                skill = ", ".join(skill[:3])
            skill_str = f" [{skill}]" if skill else ""
            items.append(f"{k} - {v['content']}{skill_str}")
        else:
            items.append(f"{k} - {v}")
    return items


def _make_omni_voice_choices():
    """qwen3.5_omni_plus 的 value 是字符串"""
    items = []
    for k, v in VOICES_OMNI.items():
        label = v if isinstance(v, str) else v.get("content", str(v))
        items.append(f"{k} - {label}")
    return items


# ==================== 🎵 音频功能 ====================

def cosyvoice_tts(text, voice_display, progress=gr.Progress()):
    """文字转语音 - CosyVoice-v2，自定义音色"""
    if not text.strip():
        raise gr.Error("请输入文本内容")
    voice = voice_display.split(" - ")[0].lower()
    dashscope.api_key = get_api_key()
    dashscope.base_websocket_api_url = "wss://dashscope.aliyuncs.com/api-ws/v1/inference"
    progress(0.3, desc="正在生成语音...")
    synthesizer = SpeechSynthesizer(model="cosyvoice-v2", voice=voice)
    audio = synthesizer.call(text)
    output_path = get_output_dir() / f"speech_{get_timestamp_by_time()}.mp3"
    with open(output_path, "wb") as f:
        f.write(audio)
    progress(1.0, desc="完成")
    return str(output_path)


def qwen_tts_flash(text, voice_display, language, progress=gr.Progress()):
    """文字转语音 - qwen3-tts-flash，系统默认音色"""
    if not text.strip():
        raise gr.Error("请输入文本内容")
    voice = voice_display.split(" - ")[0]
    lang_map = {
        "中文": "Chinese", "英语": "English", "德语": "German",
        "意大利": "Italian", "葡萄牙语": "Portuguese", "西班牙语": "Spanish",
        "日语": "Japanese", "韩语": "Korean", "法语": "French", "俄语": "Russian",
    }
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    progress(0.3, desc="正在生成语音...")
    response = MultiModalConversation.call(
        model="qwen3-tts-flash",
        api_key=get_api_key(),
        text=text,
        voice=voice,
        language_type=lang_map.get(language, "Chinese"),
        stream=False,
        format="wav",
    )
    url = response.output.audio.url
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    output_path = f"{get_file_path_by_time()}.wav"
    with open(output_path, "wb") as f:
        f.write(resp.content)
    progress(1.0, desc="完成")
    return str(output_path)


def audio_translate(audio_file, source_lang, target_lang, voice_display, progress=gr.Progress()):
    """语音翻译 - 上传音频，翻译并输出"""
    if audio_file is None:
        raise gr.Error("请上传音频文件")
    voice = voice_display.split(" - ")[0]
    language_codes = get_language_code()
    base64_str = base64_encode_by_name_v2(Path(audio_file))
    uri = f"data:audio/wav;base64,{base64_str}"
    client = OpenAI(
        api_key=get_api_key(),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    progress(0.2, desc="正在翻译...")
    completion = client.chat.completions.create(
        model="qwen3-livetranslate-flash",
        messages=[{
            "role": "user",
            "content": [{"type": "input_audio", "input_audio": {"data": uri, "format": "wav"}}],
        }],
        modalities=["text", "audio"],
        audio={"voice": voice, "format": "wav"},
        stream=True,
        stream_options={"include_usage": True},
        extra_body={
            "translation_options": {
                "source_lang": language_codes[source_lang],
                "target_lang": language_codes[target_lang],
            }
        },
    )
    audio_chunks = []
    text_content = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content:
            text_content += chunk.choices[0].delta.content
        if chunk.choices and hasattr(chunk.choices[0].delta, "audio"):
            info = chunk.choices[0].delta.audio
            if info and isinstance(info, dict) and info.get("data"):
                audio_chunks.append(info["data"])
    if not audio_chunks:
        raise gr.Error("未收到音频数据")
    progress(0.8, desc="正在保存音频...")
    full_b64 = "".join(audio_chunks)
    audio_bytes = base64.b64decode(full_b64)
    output_path = get_output_dir() / f"translated_{get_timestamp_by_time()}.wav"
    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_bytes)
    progress(1.0, desc="完成")
    return str(output_path), text_content


def voice_clone_url(audio_url, text, progress=gr.Progress()):
    """声音复刻 - 通过URL音频复刻音色"""
    if not text.strip():
        raise gr.Error("请输入文本内容")
    if not audio_url.strip():
        audio_url = "https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/cosyvoice/cosyvoice-zeroshot-sample.wav"
    dashscope.api_key = get_api_key()
    dashscope.base_websocket_api_url = "wss://dashscope.aliyuncs.com/api-ws/v1/inference"
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    target_model = "cosyvoice-v3-plus"
    progress(0.15, desc="正在创建音色...")
    service = VoiceEnrollmentService()
    voice_id = service.create_voice(target_model=target_model, prefix="myvoice", url=audio_url)
    progress(0.25, desc="等待音色就绪...")
    for attempt in range(30):
        info = service.query_voice(voice_id=voice_id)
        status = info.get("status")
        if status == "OK":
            break
        if status == "UNDEPLOYED":
            raise gr.Error("音色处理失败")
        time.sleep(10)
    else:
        raise gr.Error("音色创建超时（5分钟）")
    progress(0.6, desc="正在合成语音...")
    synthesizer = SpeechSynthesizer(model=target_model, voice=voice_id)
    audio_data = synthesizer.call(text)
    output_path = get_output_dir() / f"{get_timestamp_by_time()}.wav"
    with open(output_path, "wb") as f:
        f.write(audio_data)
    progress(1.0, desc="完成")
    return str(output_path)


def voice_clone_local(audio_file, text, progress=gr.Progress()):
    """声音复刻 - 通过本地音频复刻音色（建议10-20秒）"""
    if audio_file is None or not text.strip():
        raise gr.Error("请上传音频（建议10-20秒）并输入文本")
    progress(0.15, desc="正在创建音色...")
    file_path = Path(audio_file)
    base64_str = base64.b64encode(file_path.read_bytes()).decode()
    data_uri = f"data:audio/wav;base64,{base64_str}"
    resp = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization",
        json={
            "model": "qwen-voice-enrollment",
            "input": {
                "action": "create",
                "target_model": "qwen3-tts-vc-2026-01-22",
                "preferred_name": "gradio_voice",
                "audio": {"data": data_uri},
            },
        },
        headers={"Authorization": f"Bearer {get_api_key()}", "Content-Type": "application/json"},
        timeout=60,
    )
    if resp.status_code != 200:
        raise gr.Error(f"创建音色失败: {resp.text}")
    voice_id = resp.json()["output"]["voice"]
    progress(0.5, desc="正在合成语音...")
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    response = MultiModalConversation.call(
        model="qwen3-tts-vc-2026-01-22",
        api_key=get_api_key(),
        text=text,
        voice=voice_id,
        stream=False,
    )
    audio_url = response.output.audio.url
    resp2 = requests.get(audio_url, timeout=30)
    resp2.raise_for_status()
    output_path = f"{get_file_path_by_time()}.wav"
    with open(output_path, "wb") as f:
        f.write(resp2.content)
    progress(1.0, desc="完成")
    return str(output_path)


def voice_design(voice_prompt, synthesise_text, progress=gr.Progress()):
    """声音设计 - 通过文字描述生成专属音色并合成"""
    if not voice_prompt.strip() or not synthesise_text.strip():
        raise gr.Error("请输入声音描述和合成文本")
    api_key = get_api_key()
    preview_text = "各位听众朋友，大家好，欢迎收听晚间新闻。"
    progress(0.2, desc="正在设计音色...")
    resp = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization",
        json={
            "model": "voice-enrollment",
            "input": {
                "action": "create_voice",
                "target_model": "cosyvoice-v3.5-plus",
                "voice_prompt": voice_prompt,
                "preview_text": preview_text,
                "prefix": "designed",
            },
            "parameters": {"sample_rate": 24000, "response_format": "wav"},
        },
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=60,
    )
    if resp.status_code != 200:
        raise gr.Error(f"声音设计失败: {resp.text}")
    result = resp.json()
    voice_id = result["output"]["voice_id"]
    preview_path = get_output_dir() / f"{voice_id}_preview.wav"
    with open(preview_path, "wb") as f:
        f.write(base64.b64decode(result["output"]["preview_audio"]["data"]))
    progress(0.6, desc="正在合成正式语音...")
    dashscope.api_key = api_key
    synthesizer = SpeechSynthesizer(model="cosyvoice-v3.5-plus", voice=voice_id)
    audio = synthesizer.call(synthesise_text)
    output_path = get_output_dir() / f"{voice_id}_synthesized.wav"
    with open(output_path, "wb") as f:
        f.write(audio)
    progress(1.0, desc="完成")
    return str(preview_path), str(output_path)


def parse_sse(sse_file):
    """SSE 音频解析 - 将Base64流式数据解码为WAV"""
    if sse_file is None:
        raise gr.Error("请上传SSE文件")
    audio_bytes = bytearray()
    with open(sse_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("data:"):
                continue
            json_str = line[5:].strip()
            if not json_str:
                continue
            try:
                data = json.loads(json_str)
                b64_data = data.get("output", {}).get("audio", {}).get("data", "")
                if b64_data:
                    audio_bytes.extend(base64.b64decode(b64_data))
            except json.JSONDecodeError:
                continue
    if not audio_bytes:
        raise gr.Error("未在文件中找到音频数据")
    output_path = get_output_dir() / f"{get_timestamp_by_time()}.wav"
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    return str(output_path)


# ==================== 🖼️ 图像功能 ====================

def image_understand(image, question):
    """图片理解 - 上传图片，AI 分析并回答"""
    if image is None:
        raise gr.Error("请上传图片")
    base64_image = _encode_file_to_base64(image)
    if not question.strip():
        question = "图中描绘的是什么景象?"
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    response = MultiModalConversation.call(
        api_key=get_api_key(),
        model="qwen3.6-plus",
        messages=[{
            "role": "user",
            "content": [
                {"image": f"data:image/png;base64,{base64_image}"},
                {"text": question},
            ],
        }],
    )
    return response.output.choices[0].message.content[0]["text"]


def image_ocr(image):
    """OCR 文字提取 - 从车票等图片中提取结构化信息"""
    if image is None:
        raise gr.Error("请上传图片（支持车票等）")
    base64_str = _encode_file_to_base64(image)
    prompt = (
        "请提取车票图像中的发票号码、车次、起始站、终点站、发车日期和时间点、"
        "座位号、席别类型、票价、身份证号码、购票人姓名。"
        "要求准确无误的提取上述关键信息、不要遗漏和捏造虚假信息，"
        "模糊或者强光遮挡的单个文字可以用英文问号?代替。"
        "返回数据格式以json方式输出。"
    )
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    response = MultiModalConversation.call(
        model="qwen-vl-ocr-latest",
        api_key=get_api_key(),
        messages=[{
            "role": "user",
            "content": [
                {"image": f"data:img/jpeg;base64,{base64_str}"},
                {"text": prompt},
            ],
        }],
    )
    return response.output.choices[0].message.content[0]["text"]


def image_answer(image, question):
    """拍照答题 - 上传题目图片，AI 解答（流式思考+答案）"""
    if image is None:
        raise gr.Error("请上传题目图片")
    base64_str = _encode_file_to_base64(image)
    if not question.strip():
        question = "请解答这道题？"
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    response = MultiModalConversation.call(
        api_key=get_api_key(),
        model="qwen3.6-plus",
        messages=[{
            "role": "user",
            "content": [
                {"image": f"data:image/png;base64,{base64_str}"},
                {"text": question},
            ],
        }],
        stream=True,
        enable_thinking=True,
    )
    reasoning = ""
    answer = ""
    for chunk in response:
        msg = chunk.output.choices[0].message
        content_list = msg.content
        reasoning_chunk = msg.get("reasoning_content", None)
        if reasoning_chunk is not None and content_list == []:
            reasoning += msg.reasoning_content
        elif content_list:
            answer += content_list[0].get("text", "")
    return reasoning, answer


# ==================== 🎬 视频功能 ====================

def video_understand_online(video_url, question):
    """视频理解 - 在线URL"""
    if not video_url.strip():
        video_url = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241115/cqqkru/1.mp4"
    if not question.strip():
        question = "这段视频的内容是什么?"
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    response = MultiModalConversation.call(
        api_key=get_api_key(),
        model="qwen3.6-plus",
        messages=[{
            "role": "user",
            "content": [
                {"video": video_url, "fps": 2},
                {"text": question},
            ],
        }],
    )
    return response.output.choices[0].message.content[0]["text"]


def video_understand_local(video_file, question):
    """视频理解 - 本地上传"""
    if video_file is None:
        raise gr.Error("请上传视频文件")
    base64_video = _encode_file_to_base64(video_file)
    if not question.strip():
        question = "这段视频描绘的是什么景象？"
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    response = MultiModalConversation.call(
        api_key=get_api_key(),
        model="qwen3.6-plus",
        messages=[{
            "role": "user",
            "content": [
                {"video": f"data:video/mp4;base64,{base64_video}", "fps": 2},
                {"text": question},
            ],
        }],
    )
    return response.output.choices[0].message.content[0]["text"]


def video_understand_pictures(images, question):
    """视频理解 - 通过图片列表"""
    if images is None or len(images) == 0:
        raise gr.Error("请至少上传一张图片")
    if not question.strip():
        question = "描述这个视频的具体过程"
    base64_images = []
    for img_path in images:
        b64 = _encode_file_to_base64(img_path)
        base64_images.append(f"data:image/jpeg;base64,{b64}")
    client = OpenAI(
        api_key=get_api_key(),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model="qwen3.6-plus",
        messages=[{
            "role": "user",
            "content": [
                {"type": "video", "video": base64_images},
                {"type": "text", "text": question},
            ],
        }],
    )
    return completion.choices[0].message.content


# ==================== 🎨 生成功能 ====================

def text2image_qwen(prompt, size, progress=gr.Progress()):
    """文生图 - 千问 qwen-image-2.0-pro"""
    if not prompt.strip():
        raise gr.Error("请输入图片描述")
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    size_map = {"1024x1024": "1024*1024", "2048x2048": "2048*2048"}
    progress(0.3, desc="正在生成图片...")
    response = MultiModalConversation.call(
        api_key=get_api_key(),
        model="qwen-image-2.0-pro",
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        result_format="message",
        stream=False,
        watermark=False,
        prompt_extend=True,
        negative_prompt="低分辨率，低画质",
        size=size_map.get(size, "1024*1024"),
    )
    if response.status_code != 200:
        raise gr.Error(f"生成失败: {response.code} - {response.message}")
    url = response.output.choices[0].message.content[0].get("image", "")
    if not url:
        raise gr.Error("图片链接获取失败")
    progress(0.7, desc="正在下载图片...")
    output_path = get_output_dir() / f"qwen_img_{get_timestamp_by_time()}.png"
    get_file_by_url(url, "png")
    # get_file_by_url downloads to output dir with url filename, find it
    import glob
    png_files = sorted(Path(get_output_dir()).glob("*.png"), key=os.path.getmtime, reverse=True)
    if png_files:
        progress(1.0, desc="完成")
        return str(png_files[0])
    raise gr.Error("图片下载失败")


def text2image_wan(prompt, progress=gr.Progress()):
    """文生图 - 万相 wan2.7-image-pro（异步）"""
    if not prompt.strip():
        raise gr.Error("请输入图片描述")
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    progress(0.1, desc="提交异步任务...")
    response = ImageGeneration.async_call(
        model="wan2.7-image-pro",
        api_key=get_api_key(),
        messages=[Message(role="user", content=[{"text": prompt}])],
        enable_sequential=False,
        n=1,
        format="png",
        size="2K",
    )
    if response.status_code != 200:
        raise gr.Error(f"任务创建失败: {response.code} - {response.message}")
    progress(0.2, desc="等待任务完成（约1-2分钟）...")
    status = ImageGeneration.wait(task=response, api_key=get_api_key())
    if status.output.task_status != "SUCCEEDED":
        raise gr.Error(f"任务失败: {status.output.task_status}")
    progress(0.7, desc="正在下载图片...")
    url = status.output.choices[0].message.content[0].get("image", "")
    if not url:
        raise gr.Error("图片链接获取失败")
    get_file_by_url(url, "png")
    import glob
    png_files = sorted(Path(get_output_dir()).glob("*.png"), key=os.path.getmtime, reverse=True)
    if png_files:
        progress(1.0, desc="完成")
        return str(png_files[0])
    raise gr.Error("图片下载失败")


def text2video(prompt, duration, progress=gr.Progress()):
    """文生视频 - 万相 wan2.7-t2v（异步，约2-5分钟）"""
    if not prompt.strip():
        raise gr.Error("请输入视频描述")
    progress(0.05, desc="提交异步任务...")
    rsp = VideoSynthesis.async_call(
        api_key=get_api_key(),
        model="wan2.7-t2v",
        prompt=prompt,
        resolution="720P",
        duration=int(duration),
        ratio="16:9",
        negative_prompt="",
        prompt_extend=True,
        watermark=False,
        seed=12345,
    )
    if rsp.status_code != 200:
        raise gr.Error(f"任务提交失败: {rsp.code} - {rsp.message}")
    progress(0.1, desc="等待任务完成（约2-5分钟）...")
    rsp = VideoSynthesis.wait(task=rsp, api_key=get_api_key())
    if rsp.status_code != 200:
        raise gr.Error(f"任务失败: {rsp.code} - {rsp.message}")
    video_url = rsp.output.video_url
    progress(0.8, desc="正在下载视频...")
    output_path = get_output_dir() / f"video_{get_timestamp_by_time()}.mp4"
    resp = requests.get(video_url, timeout=60)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)
    progress(1.0, desc="完成")
    return str(output_path)


def video_continuation(video_url, picture_url, prompt, progress=gr.Progress()):
    """视频续写 - 万相 wan2.7-i2v"""
    if not prompt.strip():
        raise gr.Error("请输入提示词")
    if not video_url.strip():
        video_url = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20260414/cqcbkw/wan2.7-i2v-video-continuation.mp4"
    if not picture_url.strip():
        picture_url = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20260414/mrwahg/wan2.7-i2v-video-continuation.webp"
    dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
    progress(0.1, desc="提交任务...")
    rsp = VideoSynthesis.async_call(
        api_key=get_api_key(),
        model="wan2.7-i2v",
        media=[
            {"type": "first_clip", "url": video_url},
            {"type": "last_frame", "url": picture_url},
        ],
        resolution="720P",
        duration=12,
        watermark=True,
        prompt=prompt,
    )
    if rsp.status_code != 200:
        raise gr.Error(f"任务提交失败: {rsp.code} - {rsp.message}")
    progress(0.2, desc="等待任务完成（约1-2分钟）...")
    rsp = VideoSynthesis.wait(task=rsp, api_key=get_api_key())
    if rsp.status_code != 200:
        raise gr.Error(f"任务失败: {rsp.code} - {rsp.message}")
    final_url = rsp.output.get("video_url") or getattr(rsp.output, "video_url", None)
    if not final_url:
        raise gr.Error("未能获取视频链接")
    progress(0.8, desc="正在下载视频...")
    output_path = get_output_dir() / f"continuation_{get_timestamp_by_time()}.mp4"
    resp = requests.get(final_url, timeout=60)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)
    progress(1.0, desc="完成")
    return str(output_path)


# ==================== 💬 对话功能 ====================

def chat_stream(message, history):
    """纯文本多轮对话 - DeepSeek-v3.2（流式输出，含思考过程）"""
    messages = []
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        if h[1]:
            messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})
    completion = Generation.call(
        api_key=get_api_key(),
        model="deepseek-v3.2",
        messages=messages,
        result_format="message",
        enable_thinking=True,
        stream=True,
        incremental_output=True,
    )
    reasoning = ""
    answer = ""
    is_answering = False
    for chunk in completion:
        msg = chunk.output.choices[0].message
        if "reasoning_content" in msg and not is_answering:
            reasoning += msg.reasoning_content
            yield f"🧠 **思考过程**\n\n{reasoning}"
        if msg.content:
            if not is_answering:
                is_answering = True
            answer += msg.content
            yield f"🧠 **思考过程**\n\n{reasoning}\n\n---\n\n💬 **回复**\n\n{answer}"


def multimodal_chat(text, voice_display, progress=gr.Progress()):
    """多模态对话 - 文本输入，文本+音频回复"""
    if not text.strip():
        raise gr.Error("请输入对话内容")
    voice = voice_display.split(" - ")[0]
    client = OpenAI(
        api_key=get_api_key(),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    progress(0.3, desc="正在请求...")
    completion = client.chat.completions.create(
        model="qwen3.5-omni-plus",
        messages=[{"role": "user", "content": text}],
        modalities=["text", "audio"],
        audio={"voice": voice, "format": "wav"},
        stream=True,
        stream_options={"include_usage": True},
    )
    text_content = ""
    audio_b64 = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content:
            text_content += chunk.choices[0].delta.content
        if chunk.choices and hasattr(chunk.choices[0].delta, "audio") and chunk.choices[0].delta.audio:
            audio_b64 += chunk.choices[0].delta.audio.get("data", "")
    audio_path = None
    if audio_b64:
        progress(0.8, desc="正在保存音频...")
        wav_bytes = base64.b64decode(audio_b64)
        audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
        audio_path = f"{get_file_path_by_time()}.wav"
        sf.write(audio_path, audio_np, samplerate=24000)
    progress(1.0, desc="完成")
    return text_content, audio_path


# ==================== 🔑 API 密钥管理 ====================

def _get_env_path() -> Path:
    """获取 .env 文件路径，兼容开发环境和 PyInstaller 打包环境"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / ".env"
    return Path(__file__).parent / ".env"


def _load_api_key() -> str:
    """读取已保存的 API 密钥，用于初始化显示"""
    env_path = _get_env_path()
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DASHSCOPE_API_KEY="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    return val
    return ""


def save_api_key(api_key: str) -> str:
    """保存 API 密钥到 .env 文件，同时设置到当前进程环境变量"""
    key = api_key.strip()
    if not key:
        return "⚠️ 请输入有效的 API 密钥"
    env_path = _get_env_path()
    lines = []
    found = False
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("DASHSCOPE_API_KEY="):
                lines.append(f'DASHSCOPE_API_KEY="{key}"')
                found = True
            else:
                lines.append(line)
    if not found:
        lines.append(f'DASHSCOPE_API_KEY="{key}"')
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.environ["DASHSCOPE_API_KEY"] = key
    return f"✅ 密钥已保存到 {env_path.name}"


# ==================== 🏗️ 构建 Gradio 界面 ====================

CSS = """
footer {display: none !important;}
.gradio-container {max-width: 1000px !important; margin: auto !important;}
"""


def build_ui():
    with gr.Blocks(title="AI 工具箱") as demo:
        gr.Markdown(
            """# 🚀 AI 工具箱
            基于**阿里云百炼平台（DashScope）**，提供语音合成、图像理解、视频分析、文生图/视频、多轮对话等 AI 能力。
            """
        )

        # ========== API 密钥设置 ==========
        with gr.Row():
            api_key_box = gr.Textbox(
                label="🔑 API 密钥（DashScope）",
                placeholder="sk-...  填入后点击保存，自动写入 .env 文件",
                type="password",
                scale=4,
                value=_load_api_key(),
            )
            with gr.Column(scale=1, min_width=100):
                api_key_save_btn = gr.Button("💾 保存密钥", variant="secondary")
                api_key_status = gr.Markdown("", elem_id="api-status")
        api_key_save_btn.click(
            fn=save_api_key,
            inputs=api_key_box,
            outputs=api_key_status,
        )

        # ========== 🎵 音频功能 ==========
        with gr.Accordion("🎵 音频功能", open=False):
            with gr.Tabs():
                # 文字转语音 (CosyVoice-v2)
                with gr.TabItem("文字转语音 · CosyVoice-v2"):
                    gr.Markdown("使用 **CosyVoice-v2** 模型，20+ 种预设音色。")
                    with gr.Row():
                        with gr.Column(scale=2):
                            tts_cosy_text = gr.Textbox(
                                label="输入文字",
                                placeholder="请输入要合成语音的文字...",
                                lines=4,
                            )
                            tts_cosy_voice = gr.Dropdown(
                                label="选择音色",
                                choices=_make_cosyvoice_voice_choices(),
                                value=_make_cosyvoice_voice_choices()[0] if _make_cosyvoice_voice_choices() else None,
                            )
                            tts_cosy_btn = gr.Button("🎙️ 生成语音", variant="primary")
                        with gr.Column(scale=1):
                            tts_cosy_output = gr.Audio(label="生成的语音", type="filepath")
                    tts_cosy_btn.click(
                        fn=cosyvoice_tts,
                        inputs=[tts_cosy_text, tts_cosy_voice],
                        outputs=tts_cosy_output,
                    )

                # 文字转语音 (qwen3-tts-flash)
                with gr.TabItem("文字转语音 · qwen3-tts-flash"):
                    gr.Markdown("使用 **qwen3-tts-flash** 模型，系统默认音色，支持多语言。")
                    with gr.Row():
                        with gr.Column(scale=2):
                            tts_qwen_text = gr.Textbox(
                                label="输入文字",
                                placeholder="请输入要合成语音的文字...",
                                lines=4,
                            )
                            tts_qwen_voice = gr.Dropdown(
                                label="选择音色",
                                choices=_make_qwen_tts_voice_choices(),
                                value=_make_qwen_tts_voice_choices()[0] if _make_qwen_tts_voice_choices() else None,
                            )
                            tts_qwen_lang = gr.Dropdown(
                                label="语言",
                                choices=LANG_CHOICES,
                                value="中文",
                            )
                            tts_qwen_btn = gr.Button("🎙️ 生成语音", variant="primary")
                        with gr.Column(scale=1):
                            tts_qwen_output = gr.Audio(label="生成的语音", type="filepath")
                    tts_qwen_btn.click(
                        fn=qwen_tts_flash,
                        inputs=[tts_qwen_text, tts_qwen_voice, tts_qwen_lang],
                        outputs=tts_qwen_output,
                    )

                # 语音翻译
                with gr.TabItem("语音翻译"):
                    gr.Markdown("上传 **WAV 格式**音频文件，选择源语言和目标语言，AI 自动翻译并输出音频。")
                    with gr.Row():
                        with gr.Column(scale=2):
                            translate_audio = gr.File(label="上传音频 (.wav)", file_types=[".wav"])
                            translate_src = gr.Dropdown(label="源语言", choices=LANGUAGES, value="英语")
                            translate_tgt = gr.Dropdown(label="目标语言", choices=LANGUAGES, value="日语")
                            translate_voice = gr.Dropdown(
                                label="翻译发言人",
                                choices=_make_translate_voice_choices(),
                                value=_make_translate_voice_choices()[0] if _make_translate_voice_choices() else None,
                            )
                            translate_btn = gr.Button("🌐 开始翻译", variant="primary")
                        with gr.Column(scale=1):
                            translate_audio_out = gr.Audio(label="翻译后的音频", type="filepath")
                            translate_text_out = gr.Textbox(label="翻译文本", lines=4)
                    translate_btn.click(
                        fn=audio_translate,
                        inputs=[translate_audio, translate_src, translate_tgt, translate_voice],
                        outputs=[translate_audio_out, translate_text_out],
                    )

                # 声音复刻 - URL
                with gr.TabItem("声音复刻 · URL"):
                    gr.Markdown("通过**在线音频 URL** 复刻音色，输入文本即可用该音色朗读。")
                    with gr.Row():
                        with gr.Column(scale=2):
                            clone_url_input = gr.Textbox(
                                label="音频 URL",
                                placeholder="https://...  (留空使用默认示例)",
                            )
                            clone_url_text = gr.Textbox(
                                label="合成文本",
                                placeholder="请输入要合成的文字...",
                                lines=3,
                            )
                            clone_url_btn = gr.Button("🎤 复刻并合成", variant="primary")
                        with gr.Column(scale=1):
                            clone_url_output = gr.Audio(label="合成的语音", type="filepath")
                    clone_url_btn.click(
                        fn=voice_clone_url,
                        inputs=[clone_url_input, clone_url_text],
                        outputs=clone_url_output,
                    )

                # 声音复刻 - 本地
                with gr.TabItem("声音复刻 · 本地"):
                    gr.Markdown("上传**本地音频文件**（建议 10-20 秒），复刻音色后合成任意文字。")
                    with gr.Row():
                        with gr.Column(scale=2):
                            clone_local_audio = gr.File(label="上传音频 (.wav)", file_types=[".wav"])
                            clone_local_text = gr.Textbox(
                                label="合成文本",
                                placeholder="请输入要合成的文字...",
                                lines=3,
                            )
                            clone_local_btn = gr.Button("🎤 复刻并合成", variant="primary")
                        with gr.Column(scale=1):
                            clone_local_output = gr.Audio(label="合成的语音", type="filepath")
                    clone_local_btn.click(
                        fn=voice_clone_local,
                        inputs=[clone_local_audio, clone_local_text],
                        outputs=clone_local_output,
                    )

                # 声音设计
                with gr.TabItem("声音设计"):
                    gr.Markdown("通过**文字描述**让 AI 生成专属音色，试听后合成正式语音。")
                    with gr.Row():
                        with gr.Column(scale=2):
                            design_prompt = gr.Textbox(
                                label="声音描述",
                                placeholder="沉稳的中年男性播音员，音色低沉浑厚，富有磁性...",
                                lines=3,
                            )
                            design_text = gr.Textbox(
                                label="合成文本",
                                placeholder="请输入要正式合成的文字...",
                                lines=3,
                            )
                            design_btn = gr.Button("🎛️ 设计并合成", variant="primary")
                        with gr.Column(scale=1):
                            design_preview = gr.Audio(label="试听音频", type="filepath")
                            design_output = gr.Audio(label="正式合成音频", type="filepath")
                    design_btn.click(
                        fn=voice_design,
                        inputs=[design_prompt, design_text],
                        outputs=[design_preview, design_output],
                    )

                # SSE 解析
                with gr.TabItem("SSE 音频解析"):
                    gr.Markdown("上传 SSE 流式响应文件，提取其中的 Base64 音频数据并解码为 WAV。")
                    sse_file = gr.File(label="SSE 文件", file_types=[".wav", ".txt"])
                    sse_btn = gr.Button("🔍 解析", variant="primary")
                    sse_output = gr.Audio(label="解析出的音频", type="filepath")
                    sse_btn.click(fn=parse_sse, inputs=sse_file, outputs=sse_output)

        # ========== 🖼️ 图像功能 ==========
        with gr.Accordion("🖼️ 图像功能", open=False):
            with gr.Tabs():
                with gr.TabItem("图片理解"):
                    gr.Markdown("上传图片，AI 分析并回答你的问题。")
                    with gr.Row():
                        with gr.Column(scale=1):
                            img_understand_img = gr.Image(label="上传图片", type="filepath")
                            img_understand_q = gr.Textbox(label="问题", placeholder="图中描绘的是什么景象?", value="图中描绘的是什么景象?")
                            img_understand_btn = gr.Button("🔍 分析", variant="primary")
                        with gr.Column(scale=1):
                            img_understand_out = gr.Textbox(label="分析结果", lines=10)
                    img_understand_btn.click(
                        fn=image_understand,
                        inputs=[img_understand_img, img_understand_q],
                        outputs=img_understand_out,
                    )

                with gr.TabItem("OCR 文字提取"):
                    gr.Markdown("上传图片（如车票、文档等），AI 提取关键信息。")
                    with gr.Row():
                        with gr.Column(scale=1):
                            img_ocr_img = gr.Image(label="上传图片", type="filepath")
                            img_ocr_btn = gr.Button("📝 提取文字", variant="primary")
                        with gr.Column(scale=1):
                            img_ocr_out = gr.Textbox(label="提取结果", lines=12)
                    img_ocr_btn.click(
                        fn=image_ocr,
                        inputs=img_ocr_img,
                        outputs=img_ocr_out,
                    )

                with gr.TabItem("拍照答题"):
                    gr.Markdown("上传题目图片，AI 展示思考过程并给出解答。")
                    with gr.Row():
                        with gr.Column(scale=1):
                            img_answer_img = gr.Image(label="上传题目图片", type="filepath")
                            img_answer_q = gr.Textbox(label="问题", placeholder="请解答这道题？", value="请解答这道题？")
                            img_answer_btn = gr.Button("💡 解答", variant="primary")
                        with gr.Column(scale=1):
                            img_answer_reasoning = gr.Textbox(label="思考过程", lines=8)
                            img_answer_out = gr.Textbox(label="最终答案", lines=8)
                    img_answer_btn.click(
                        fn=image_answer,
                        inputs=[img_answer_img, img_answer_q],
                        outputs=[img_answer_reasoning, img_answer_out],
                    )

        # ========== 🎬 视频功能 ==========
        with gr.Accordion("🎬 视频功能", open=False):
            with gr.Tabs():
                with gr.TabItem("视频理解 · 在线"):
                    gr.Markdown("输入在线视频 URL，AI 分析内容。")
                    with gr.Row():
                        with gr.Column(scale=1):
                            video_online_url = gr.Textbox(
                                label="视频 URL",
                                placeholder="https://... (留空使用默认示例)",
                            )
                            video_online_q = gr.Textbox(label="问题", value="这段视频的内容是什么?")
                            video_online_btn = gr.Button("🎬 分析", variant="primary")
                        with gr.Column(scale=1):
                            video_online_out = gr.Textbox(label="分析结果", lines=10)
                    video_online_btn.click(
                        fn=video_understand_online,
                        inputs=[video_online_url, video_online_q],
                        outputs=video_online_out,
                    )

                with gr.TabItem("视频理解 · 本地"):
                    gr.Markdown("上传本地视频文件（MP4），AI 分析内容。")
                    with gr.Row():
                        with gr.Column(scale=1):
                            video_local_file = gr.File(label="上传视频 (.mp4)", file_types=[".mp4"])
                            video_local_q = gr.Textbox(label="问题", value="这段视频描绘的是什么景象？")
                            video_local_btn = gr.Button("🎬 分析", variant="primary")
                        with gr.Column(scale=1):
                            video_local_out = gr.Textbox(label="分析结果", lines=10)
                    video_local_btn.click(
                        fn=video_understand_local,
                        inputs=[video_local_file, video_local_q],
                        outputs=video_local_out,
                    )

                with gr.TabItem("视频理解 · 图片列表"):
                    gr.Markdown("上传多张图片，AI 将其作为视频帧序列进行理解。")
                    with gr.Row():
                        with gr.Column(scale=1):
                            video_pics_files = gr.File(
                                label="上传图片（可多选）",
                                file_types=["image"],
                                file_count="multiple",
                            )
                            video_pics_q = gr.Textbox(label="问题", value="描述这个视频的具体过程")
                            video_pics_btn = gr.Button("🎬 分析", variant="primary")
                        with gr.Column(scale=1):
                            video_pics_out = gr.Textbox(label="分析结果", lines=10)
                    video_pics_btn.click(
                        fn=video_understand_pictures,
                        inputs=[video_pics_files, video_pics_q],
                        outputs=video_pics_out,
                    )

        # ========== 🎨 生成功能 ==========
        with gr.Accordion("🎨 生成功能", open=False):
            with gr.Tabs():
                with gr.TabItem("文生图 · 千问"):
                    gr.Markdown("使用 **qwen-image-2.0-pro** 模型同步生成图片。")
                    with gr.Row():
                        with gr.Column(scale=2):
                            gen_qwen_prompt = gr.Textbox(
                                label="图片描述",
                                placeholder="冬日北京的都市街景，青灰瓦顶...",
                                lines=4,
                            )
                            gen_qwen_size = gr.Dropdown(
                                label="分辨率",
                                choices=["1024x1024", "2048x2048"],
                                value="1024x1024",
                            )
                            gen_qwen_btn = gr.Button("🖼️ 生成图片", variant="primary")
                        with gr.Column(scale=1):
                            gen_qwen_output = gr.Image(label="生成的图片", type="filepath")
                    gen_qwen_btn.click(
                        fn=text2image_qwen,
                        inputs=[gen_qwen_prompt, gen_qwen_size],
                        outputs=gen_qwen_output,
                    )

                with gr.TabItem("文生图 · 万相"):
                    gr.Markdown("使用 **wan2.7-image-pro** 模型异步生成图片（约 1-2 分钟）。")
                    with gr.Row():
                        with gr.Column(scale=2):
                            gen_wan_prompt = gr.Textbox(
                                label="图片描述",
                                placeholder="超高清，农村田园风格，小村子里一户人家...",
                                lines=4,
                            )
                            gen_wan_btn = gr.Button("🖼️ 生成图片", variant="primary")
                        with gr.Column(scale=1):
                            gen_wan_output = gr.Image(label="生成的图片", type="filepath")
                    gen_wan_btn.click(
                        fn=text2image_wan,
                        inputs=gen_wan_prompt,
                        outputs=gen_wan_output,
                    )

                with gr.TabItem("文生视频"):
                    gr.Markdown("使用 **wan2.7-t2v** 模型异步生成视频（约 2-5 分钟）。")
                    with gr.Row():
                        with gr.Column(scale=2):
                            gen_video_prompt = gr.Textbox(
                                label="视频描述",
                                placeholder="水墨动画风格，一位年轻书生立于窗前...",
                                lines=4,
                            )
                            gen_video_duration = gr.Dropdown(
                                label="时长（秒）",
                                choices=["5", "10"],
                                value="5",
                            )
                            gen_video_btn = gr.Button("🎥 生成视频", variant="primary")
                        with gr.Column(scale=1):
                            gen_video_output = gr.Video(label="生成的视频")
                    gen_video_btn.click(
                        fn=text2video,
                        inputs=[gen_video_prompt, gen_video_duration],
                        outputs=gen_video_output,
                    )

                with gr.TabItem("视频续写"):
                    gr.Markdown("使用 **wan2.7-i2v** 模型，根据首段视频 + 尾帧图片生成中间过渡。")
                    with gr.Row():
                        with gr.Column(scale=2):
                            gen_cont_video = gr.Textbox(
                                label="首段视频 URL",
                                placeholder="https://... (留空使用默认示例)",
                            )
                            gen_cont_pic = gr.Textbox(
                                label="尾帧图片 URL",
                                placeholder="https://... (留空使用默认示例)",
                            )
                            gen_cont_prompt = gr.Textbox(
                                label="提示词",
                                placeholder="男人低头向下看到地上的木箱...",
                                lines=3,
                            )
                            gen_cont_btn = gr.Button("🎬 生成续写视频", variant="primary")
                        with gr.Column(scale=1):
                            gen_cont_output = gr.Video(label="生成的视频")
                    gen_cont_btn.click(
                        fn=video_continuation,
                        inputs=[gen_cont_video, gen_cont_pic, gen_cont_prompt],
                        outputs=gen_cont_output,
                    )

        # ========== 💬 对话功能 ==========
        with gr.Accordion("💬 对话功能", open=True):
            with gr.Tabs():
                with gr.TabItem("纯文本多轮对话"):
                    gr.Markdown("基于 **DeepSeek-v3.2** 的多轮对话，流式输出思考过程和回复。")
                    chat_iface = gr.ChatInterface(
                        fn=chat_stream,
                        chatbot=gr.Chatbot(height=500, label="对话"),
                        textbox=gr.Textbox(placeholder="请输入你的问题...", container=False),
                        title="",
                        description="",
                    )

                with gr.TabItem("多模态对话"):
                    gr.Markdown("基于 **qwen3.5-omni-plus**，文本输入，文本 + 音频回复。")
                    with gr.Row():
                        with gr.Column(scale=2):
                            mm_text = gr.Textbox(label="输入文本", placeholder="你是谁？", lines=3)
                            mm_voice = gr.Dropdown(
                                label="回复音色",
                                choices=_make_omni_voice_choices(),
                                value=_make_omni_voice_choices()[0] if _make_omni_voice_choices() else None,
                            )
                            mm_btn = gr.Button("💬 发送", variant="primary")
                        with gr.Column(scale=1):
                            mm_text_out = gr.Textbox(label="文本回复", lines=6)
                            mm_audio_out = gr.Audio(label="音频回复", type="filepath")
                    mm_btn.click(
                        fn=multimodal_chat,
                        inputs=[mm_text, mm_voice],
                        outputs=[mm_text_out, mm_audio_out],
                    )

        gr.Markdown("---\n*AI 工具箱 · 基于阿里云百炼 DashScope · 仗剑天涯*")

    return demo


# ==================== 入口 ====================

if __name__ == "__main__":
    import traceback
    try:
        print("=" * 50, flush=True)
        print("  AI 工具箱 v1.0 - 正在启动...", flush=True)
        print("=" * 50, flush=True)

        # console=False 时 sys.stdout/stderr 为 None，uvicorn 日志初始化会崩溃
        # 改为写入日志文件而非丢弃到 /dev/null，确保错误信息可追踪
        if sys.stdout is None:
            sys.stdout = open(str(_LOG_FILE), "a")
        if sys.stderr is None:
            sys.stderr = open(str(_LOG_FILE), "a")

        logging.info("开始构建 Gradio 界面...")
        print("[启动] 正在构建界面...", flush=True)
        demo = build_ui()
        logging.info("界面构建完成，准备启动服务器")

        print("[启动] 正在启动 Web 服务器...", flush=True)
        demo.queue(default_concurrency_limit=5).launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            quiet=False,
            inbrowser=True,
            theme=gr.themes.Soft(),
            css=CSS,
        )
    except Exception:
        err_msg = traceback.format_exc()
        err_log = _get_env_path().parent / "error.log"
        err_log.write_text(err_msg, encoding="utf-8")
        logging.critical("程序崩溃:\n%s", err_msg)
        print(f"\n❌ 程序发生错误，详情见: {err_log}", flush=True)
        print(err_msg, flush=True)
        input("按回车键关闭...")
        raise
