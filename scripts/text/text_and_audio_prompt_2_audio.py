"""
text_and_audio_prompt_2audio.py - 声音设计与语音合成

功能说明：
    1. 通过文字描述（voice_prompt）让 AI 生成一个专属音色，并试听预览音频。
    2. 试听满意后，输入正式文本，用刚才生成的音色合成完整语音并下载。

模型：cosyvoice-v3.5-plus

Author: 仗剑天涯
Date: 2026/4/24
"""

import base64
import os
import requests
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer
from pathlib import Path
from config.settings import get_api_key, get_output_dir

# ==================== 配置 ====================
# 输出目录
OUTPUT_DIR = get_output_dir()

# 音色设计参数（可修改）
DEFAULT_VOICE_PROMPT = "沉稳的中年男性播音员，音色低沉浑厚，富有磁性，语速平稳，吐字清晰，适合用于新闻播报或纪录片解说。"
PREVIEW_TEXT = "各位听众朋友，大家好，欢迎收听晚间新闻。"


def create_voice_and_preview(voice_prompt: str, preview_text: str) -> dict | None:
    """
    第一步：根据文字描述设计音色，并获取试听音频。

    Args:
        voice_prompt: 音色描述词，告诉 AI 想要什么样的声音。
        preview_text: 试听文本，用于生成预览音频。

    Returns:
        成功时返回 API 的完整响应 JSON，包含 voice_id 和预览音频数据。
        失败时返回 None。
    """
    api_key = get_api_key()
    if not api_key:
        print("❌ 未找到 API Key，请检查 .env 或环境变量。")
        return None

    url = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization"
    payload = {
        "model": "voice-enrollment",
        "input": {
            "action": "create_voice",
            "target_model": "cosyvoice-v3.5-plus",
            "voice_prompt": voice_prompt,
            "preview_text": preview_text,
            "prefix": "designed"
        },
        "parameters": {
            "sample_rate": 24000,
            "response_format": "wav"
        }
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        print("🎤 正在提交声音设计请求...")
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        if resp.status_code == 200:
            result = resp.json()
            voice_id = result["output"]["voice_id"]
            print(f"✅ 音色创建成功！Voice ID: {voice_id}")

            # 保存试听音频
            base64_audio = result["output"]["preview_audio"]["data"]
            audio_bytes = base64.b64decode(base64_audio)
            preview_path = OUTPUT_DIR / f"{voice_id}_preview.wav"
            with open(preview_path, "wb") as f:
                f.write(audio_bytes)
            print(f"📁 试听音频已保存至: {preview_path}")
            print("🔊 请播放试听音频，确认音色效果。")
            return result
        else:
            print(f"❌ 声音设计失败 (状态码 {resp.status_code}): {resp.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None


def synthesize_with_voice_v2(voice_id: str, text: str):
    """
    使用 SpeechSynthesizer 调用 cosyvoice-v3.5-plus 模型进行语音合成
    """
    # 这里不需要再设置 dashscope.base_http_api_url
    # 因为 SpeechSynthesizer 内部使用 WebSocket 连接
    # 2个函数，2次访问大模型，2次api。
    dashscope.api_key = get_api_key()

    print(f"🎙️ 正在使用音色 {voice_id} 合成完整语音...")

    # 实例化 SpeechSynthesizer，传入模型和音色
    synthesizer = SpeechSynthesizer(
        model="cosyvoice-v3.5-plus",
        voice=voice_id
    )

    # 调用 call 方法获取二进制音频数据
    audio = synthesizer.call(text)

    if audio:
        # 保存音频文件
        output_path = OUTPUT_DIR / f"{voice_id}_synthesized.wav"
        with open(output_path, "wb") as f:
            f.write(audio)
        print(f"✅ 正式语音已保存至: {output_path}")
        print(f"📊 文件大小: {output_path.stat().st_size / 1024:.2f} KB")
    else:
        print(f"❌ 语音合成失败：未获取到音频数据")


def audio_synthesis_by_text_and_prompt():
    print("=" * 50)
    print("🎛️  声音设计 + 语音合成工具")
    print("=" * 50)

    # 第一步：创建音色并试听
    print(f'提示词示例：{DEFAULT_VOICE_PROMPT}')
    voice_prompt = input('请输入声音提示词文本：').strip() or DEFAULT_VOICE_PROMPT
    result = create_voice_and_preview(voice_prompt, PREVIEW_TEXT)
    if result is None:
        return

    # 用户确认
    voice_id = result["output"]["voice_id"]
    confirm = input(f"\n是否使用音色 {voice_id} 继续合成正式语音？(y/n): ").strip().lower()
    if confirm != 'y':
        print("👋 已取消，再见！")
        return

    # 第二步：输入正式文本并合成
    text = input("请输入要合成的文本内容：").strip()
    if not text:
        print("❌ 文本不能为空")
        return

    synthesize_with_voice_v2(voice_id, text)
    print("\n🎉 全部完成！")


if __name__ == '__main__':
    audio_synthesis_by_text_and_prompt()