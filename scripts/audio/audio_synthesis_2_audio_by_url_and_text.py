"""
audio_url_and_text_2_audio -
可用。通过提交自己的声音链接，和文本，合成属于自己的朗读文本声音
使用cosyvoice-v3-plus模型
Author:仗剑天涯
Date:2026/4/24
"""
import os
import time
from datetime import datetime
import dashscope
from dashscope.audio.tts_v2 import VoiceEnrollmentService, SpeechSynthesizer
from config.settings import get_api_key, get_output_dir


def audio_synthesis_by_url_and_text():
    # 1. 环境准备
    # 推荐通过环境变量配置API Key
    # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
    # 若没有配置环境变量，请用百炼API Key将下行替换为：dashscope.api_key = "sk-xxx"
    dashscope.api_key = get_api_key()
    if not dashscope.api_key:
        raise ValueError("DASHSCOPE_API_KEY environment variable not set.")

    # 以下为北京地域WebSocket url，若使用新加坡地域的模型，需将url替换为：wss://dashscope-intl.aliyuncs.com/api-ws/v1/inference
    dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'
    # 以下为北京地域HTTP url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
    dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

    # 2. 定义复刻参数
    TARGET_MODEL = "cosyvoice-v3-plus"
    # 为音色起一个有意义的前缀
    VOICE_PREFIX = "myvoice"  # 仅允许数字和小写字母，小于十个字符
    # 公网可访问音频URL
    AUDIO_URL = "https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/cosyvoice/cosyvoice-zeroshot-sample.wav"  # 示例URL，请替换为自己的

    # 3. 创建音色 (异步任务)
    print("--- Step 1: Creating voice enrollment ---")
    service = VoiceEnrollmentService()
    try:
        voice_id = service.create_voice(
            target_model=TARGET_MODEL,
            prefix=VOICE_PREFIX,
            url=AUDIO_URL
        )
        print(f"Voice enrollment submitted successfully. Request ID: {service.get_last_request_id()}")
        print(f"Generated Voice ID: {voice_id}")
    except Exception as e:
        print(f"Error during voice creation: {e}")
        raise e
    # 4. 轮询查询音色状态
    print("\n--- Step 2: Polling for voice status ---")
    max_attempts = 30
    poll_interval = 10  # 秒
    for attempt in range(max_attempts):
        try:
            voice_info = service.query_voice(voice_id=voice_id)
            status = voice_info.get("status")
            print(f"Attempt {attempt + 1}/{max_attempts}: Voice status is '{status}'")

            if status == "OK":
                print("Voice is ready for synthesis.")
                break
            elif status == "UNDEPLOYED":
                print(f"Voice processing failed with status: {status}. Please check audio quality or contact support.")
                raise RuntimeError(f"Voice processing failed with status: {status}")
            # 对于 "DEPLOYING" 等中间状态，继续等待
            time.sleep(poll_interval)
        except Exception as e:
            print(f"Error during status polling: {e}")
            time.sleep(poll_interval)
    else:
        print("Polling timed out. The voice is not ready after several attempts.")
        raise RuntimeError("Polling timed out. The voice is not ready after several attempts.")

    # 5. 使用复刻音色进行语音合成
    print("\n--- Step 3: Synthesizing speech with the new voice ---")
    try:
        synthesizer = SpeechSynthesizer(model=TARGET_MODEL, voice=voice_id)
        text_to_synthesize = input('请输入语音文本：').strip()

        # call()方法返回二进制音频数据
        audio_data = synthesizer.call(text_to_synthesize)
        print(f"Speech synthesis successful. Request ID: {synthesizer.get_last_request_id()}")

        # 6. 保存音频文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'{get_output_dir()}/{timestamp}.wav'
        with open(output_path, "wb") as f:
            f.write(audio_data)
        print(f"Audio saved to {output_path}")

    except Exception as e:
        print(f"Error during speech synthesis: {e}")


if __name__ == '__main__':
    audio_synthesis_by_url_and_text()