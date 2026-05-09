"""
to_text_and_audio - 
可用。提交文本，获取大模型的语音和文本回复

Author:仗剑天涯
Date:2026/4/22
"""
# 运行前的准备工作:
# 运行下列命令安装第三方依赖
# pip install numpy soundfile openai

import os
import base64
from pprint import pprint

import soundfile as sf
import numpy as np
from openai import OpenAI

from config.settings import get_api_key
from core.utils import get_file_path_by_time, get_voices_for_llm_version


def get_text_and_audio_by_chat():
    # 用户安全输入
    content = input('大模型会以文字和语音回复\n请输入文本：') or "你是谁"
    # 获取大模型版本对应的voices字典
    pprint(get_voices_for_llm_version("qwen3.5_omni_plus"))
    voice = input('请选择你喜欢的语音发言人：') or 'Theo Calm'
    print('正在请求数据')
    # 1. 初始化客户端
    client = OpenAI(
        api_key=get_api_key(),  # 确认已配置环境变量
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    # 2. 发起请求
    try:
        completion = client.chat.completions.create(
            model="qwen3.5-omni-plus",
            messages=[{"role": "user", "content": content}],
            modalities=["text", "audio"],  # 指定输出文本和音频
            audio={"voice": voice, "format": "wav"},
            stream=True,  # 必须设置为 True
            stream_options={"include_usage": True},
        )

        # 3. 处理流式响应并解码音频
        print("模型回复：")
        audio_base64_string = ""
        for chunk in completion:
            # 处理文本部分
            if chunk.choices and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="")

            # 收集音频部分.写and条件应该是为了加快判断速度，以及安全访问不崩溃
            if chunk.choices and hasattr(chunk.choices[0].delta, "audio") and chunk.choices[0].delta.audio:
                audio_base64_string += chunk.choices[0].delta.audio.get("data", "")

        # 4. 保存音频文件
        if audio_base64_string:
            print('\n正在解码音频中')
            # 1. Base64 解码 -> 原始字节数据
            wav_bytes = base64.b64decode(audio_base64_string)
            # 2. 字节数据 -> NumPy 音频数组（16位有符号整型，标准 WAV 位深）
            audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
            # 3. NumPy 数组 -> 写入 WAV 文件（采样率需与生成时一致）
            sf.write(f'{get_file_path_by_time()}.wav', audio_np, samplerate=24000)
            print(f'\n音频文件已保存至：{get_file_path_by_time()}.wav')

    except Exception as e:
        print(f"请求失败: {e}")


if __name__ == '__main__':
    get_text_and_audio_by_chat()