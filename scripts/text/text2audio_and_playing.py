"""
text2audio_and_playing - 文字转语音并实时播放
第三方库安装失败，不值得继续投入时间。放弃
Author: 仗剑天涯
Date: 2026/4/24
"""
# coding=utf-8

import os
from io import BytesIO
import pygame  # 1. 替换 pyaudio 为 pygame
import dashscope
from dashscope.audio.tts_v2 import (
    SpeechSynthesizer,
    ResultCallback,
    AudioFormat,
)
from http import HTTPStatus
from dashscope import Generation
from config.settings import get_api_key

# 设置 API Key
dashscope.api_key = get_api_key()
# 以下为北京地域url
dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'

# 模型与音色
model = "cosyvoice-v3-plus"
voice = "longanyang"

# 2. 初始化 pygame 混音器
pygame.mixer.quit()  # 确保清理
pygame.mixer.init(frequency=22050, size=-16, channels=1)  # PCM_22050HZ_MONO_16BIT

# 3. 创建一个内存文件对象，用于缓冲音频流
audio_buffer = BytesIO()

class PygameStreamCallback(ResultCallback):
    """使用pygame处理实时音频流的回调类"""
    def on_open(self):
        print("WebSocket连接已建立。")

    def on_complete(self):
        print("语音合成任务完成。")

    def on_error(self, message: str):
        print(f"语音合成任务失败: {message}")

    def on_close(self):
        print("WebSocket连接已关闭。")

    def on_event(self, message):
        pass  # 可以忽略中间事件

    def on_data(self, data: bytes) -> None:
        """
        pygame流式播放的核心逻辑：
        每当DashScope返回一个音频数据块时，就将其送入播放队列。
        """
        print(f"收到音频数据块，长度: {len(data)}")
        # 将音频数据块送入内存缓冲区
        audio_buffer.write(data)
        # 重置缓冲区位置到开始，并加载到mixer播放
        audio_buffer.seek(0)
        try:
            # 使用mixer.music进行流式播放
            pygame.mixer.music.load(audio_buffer)
            # 如果没在播放，则开始播放
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()
        except pygame.error as e:
            print(f"播放音频时出错: {e}")
        finally:
            # 清空并重置缓冲区，准备接收下一个数据块
            audio_buffer.truncate(0)
            audio_buffer.seek(0)


def synthesizer_with_llm():
    """让大模型生成自我介绍文本，并实时合成语音播放。"""
    master_callback = PygameStreamCallback()

    # 初始化合成器，传入回调
    synthesizer = SpeechSynthesizer(
        model=model,
        voice=voice,
        format=AudioFormat.PCM_22050HZ_MONO_16BIT,
        callback=master_callback,
    )

    messages = [{"role": "user", "content": "请介绍一下你自己"}]
    responses = Generation.call(
        model="qwen-turbo",
        messages=messages,
        result_format="message",
        stream=True,
        incremental_output=True,
    )

    print("🤖 大模型回复：")
    for response in responses:
        if response.status_code == HTTPStatus.OK:
            content = response.output.choices[0]["message"]["content"]
            print(content, end="", flush=True)
            # 将LLM生成的文本片段实时送入语音合成器
            synthesizer.streaming_call(content)
        else:
            print(f"\n错误: {response.message}")
            return

    # 结束流式合成，等待所有音频播放完毕
    synthesizer.streaming_complete()


if __name__ == "__main__":
    try:
        synthesizer_with_llm()
    except KeyboardInterrupt:
        print("\n用户中断程序。")
    finally:
        pygame.mixer.quit() # 确保释放pygame资源