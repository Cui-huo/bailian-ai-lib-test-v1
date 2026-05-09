"""
audio_translate_2_audio - 
可用。
把audio的在线url读取，翻译成指定语言
已增加上传本地音频功能，以及输入控制功能
交互式菜单。
支持自行输入URL（未测试）
代码兼容video_translate_2_video

Author:仗剑天涯
Date:2026/4/25
"""
import base64
from datetime import datetime
import wave
import base64
import os
from pathlib import Path
from typing import Any

from openai import OpenAI
from config.settings import get_api_key, get_output_dir, get_input_dir
from core.utils import get_voices_for_llm_version, get_language_code, base64_encode_by_name_v2

# ==================== 默认参数 ====================
model = "qwen3-livetranslate-flash"
# 设置字典调用
language_codes = get_language_code()
voices = get_voices_for_llm_version(model)
audio_format = "wav"        # 输出音频格式
voice = "Cherry"
audio_local_path = 'scripts/audio/assets/translated_en2ja_20260425_154454.wav'
audio_download_path = get_output_dir()  # 保存到输出目录，无文件夹自动创建

# 输入音频的 URL（也可以替换为本地文件 base64 编码后传入）
input_audio_url = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250211/tixcef/cherry.wav"

def get_uri_from_local_audio():
    # 上传本地音频（先读取，再编码，再拼凑uri）
    input_path = get_input_dir()
    # 编码
    base64_str = base64_encode_by_name_v2(input_path)
    # 拼凑uri
    uri = f'data:audio/wav;base64,{base64_str}'
    return uri

def input_language_control(language_codes: dict[str | Any, str | Any]) -> tuple[str, str]:
    # 用户输入控制：输入的内容必须同字典的键一致
    source_lang = input('\n回车默认输入英语\n请输入源文件语言：').strip() or '英语'  # 默认源语言
    while not language_codes.get(source_lang, ''):
        print('输入有误，请重新输入！\n回车默认输入英语')
        source_lang = input('\n请输入源文件语言：').strip() or '英语'  # 默认源语言

    target_lang = input('回车默认输入日语\n请输入目标语言：').strip() or '日语'  # 默认目标语言
    while not language_codes.get(target_lang, ''):
        print('输入有误，请重新输入！\n回车默认输入日语')
        target_lang = input('回车默认输入日语\n请输入目标语言：').strip() or '日语'  # 默认目标语言
    return source_lang, target_lang


def audio_translate_online_or_local():
    while True:
        print('上传本地音频，回复1')
        print('上传在线音频，回复2')
        menu = input('音频格式：.wav\n请输入：')
        if menu == '1':
            # 增加了本地音频上传功能
            url = get_uri_from_local_audio()
            break
        elif menu == '2':
            url = input('请输入url：').strip() or input_audio_url
            break
        else:
            print('输入错误，请重新输入！')
    # 获取下载路径
    audio_download_path = get_output_dir()
    print(audio_download_path)
    # 打印所有可翻译语言
    counter = 0
    for key, value in language_codes.items():
        # 　让显示更容易看
        counter += 1
        if counter % 5 != 0:
            print(key, end=' ')
        else:
            print(key)
    # 用户输入控制：输入的内容必须同字典的键一致（字典为选择语言的字典language）
    source_lang, target_lang = input_language_control(language_codes)

    print('设置已保存')
    # 选择音色（发言人）
    print(voices)
    for key, value in voices.items():
        print(key, value['content'], value['skill'])
    voice = input('人选必须有对应技能才能完成翻译任务\n请输入翻译人选：').strip().capitalize()

    client = OpenAI(
        # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
        # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=get_api_key(),
        # 以下是北京地域base_url，如果使用新加坡地域的模型，需要将base_url替换为：https://dashscope-intl.aliyuncs.com/compatible-mode/v1
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": url,  # 也可以传入 base64 数据 URI
                        "format": "wav",
                    },
                }
            ],
        }
    ]

    # ----------------视频输入(需取消注释)----------------
    # messages = [
    #     {
    #         "role": "user",
    #         "content": [
    #             {
    #                 "type": "video_url",
    #                 "video_url": {
    #                     "url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241115/cqqkru/1.mp4"
    #                 },
    #             }
    #         ],
    #     },
    # ]

    completion = client.chat.completions.create(
        model="qwen3-livetranslate-flash",
        messages=messages,
        modalities=["text", "audio"],
        audio={"voice": voice, "format": "wav"},
        stream=True,
        stream_options={"include_usage": True},
        extra_body={"translation_options": {"source_lang": language_codes[source_lang], "target_lang": language_codes[target_lang]}},
    )

    # ==================== 处理流式响应 ====================
    print("🔊 正在翻译并生成语音...")
    text_content = ""           # 累积文本翻译内容
    audio_base64_chunks = []    # 累积音频 Base64 数据块

    for chunk in completion:
        # 1. 处理文本部分
        if chunk.choices and chunk.choices[0].delta.content:
            text_piece = chunk.choices[0].delta.content
            text_content += text_piece
            print(text_piece, end="", flush=True)

        # 2. 处理音频部分
        if chunk.choices and hasattr(chunk.choices[0].delta, 'audio'):
            audio_info = chunk.choices[0].delta.audio
            if audio_info and isinstance(audio_info, dict):
                b64_data = audio_info.get("data", "")
                if b64_data:
                    audio_base64_chunks.append(b64_data)

    print("\n✅ 流式接收完成")


    # ==================== 保存音频文件 ====================
    if audio_base64_chunks:
        print("⚙️ 正在处理音频数据...")
        # 1. 拼接所有 Base64 片段并解码为二进制数据 (PCM)
        full_b64 = "".join(audio_base64_chunks)
        audio_bytes = base64.b64decode(full_b64)

        # 2. 生成带时间戳的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = audio_download_path / f"translated_{language_codes[source_lang]}2{language_codes[target_lang]}_{timestamp}.{audio_format}"

        # 3. 使用 wave 库写入正确的 WAV 文件头和数据
        try:
            with wave.open(str(output_path), 'wb') as wav_file:
                wav_file.setnchannels(1)          # 单声道
                wav_file.setsampwidth(2)          # 16位 = 2字节
                wav_file.setframerate(24000)      # 采样率 24000 Hz
                wav_file.writeframes(audio_bytes) # 写入音频数据

            print(f"💾 翻译音频已保存至：{output_path}")
            print(f"📊 文件大小：{os.path.getsize(output_path) / 1024:.2f} KB")
        except Exception as e:
            print(f"❌ 音频文件处理失败: {e}")
    else:
        print("⚠️ 未收到任何音频数据，请检查请求参数或音频源。")



if __name__ == '__main__':
    audio_translate_online_or_local()