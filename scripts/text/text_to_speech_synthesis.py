"""
text2speech - 
文字生成语音。使用阿里云 DashScope 语音合成服务 (TTS) 生成语音
采用 WebSocket 方式调用 cosyvoice-v2 模型

Author:仗剑天涯
Date:2026/4/21
"""

import os
import sys
import time
from pathlib import Path
from dashscope.audio.tts_v2 import SpeechSynthesizer
import dashscope
# 导入配置文件，搞定API密钥
from config.settings import get_api_key, get_output_dir
from core.utils import get_voices_for_llm_version
from scripts.audio.default_audio_2_audio import voices

# ==================== 配置 ====================

# 设置 DashScope API 密钥
dashscope.api_key = get_api_key()
# 设置 WebSocket API URL (北京地域)
dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'
voices = get_voices_for_llm_version("cosyvoice-v2")
model = "cosyvoice-v2"

# 输出目录（桌面）
OUTPUT_DIR = get_output_dir()


def generate_speech(text: str, output_filename: str = None, config: dict = None) -> str:
    print(text)
    if config is None:
        raise ValueError("配置字典不能为空，请传入 model, voice 等信息。")
    # 后续逻辑使用 config["model"], config["voice"], config["format"] ...
    else:
        # 确保配置包含必需字段
        DEFAULT_CONFIG = config
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value

    # 生成输出文件名
    if output_filename is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"speech_{timestamp}"

    # 确保文件名不包含扩展名（以防用户输入包含扩展名的文件名）
    if '.' in output_filename:
        output_filename = output_filename.split('.')[0]

    output_path = OUTPUT_DIR / f"{output_filename}.{config['format']}"

    print(f"正在生成语音...")
    print(f"文字内容：{text[:50]}{'...' if len(text) > 50 else ''}")
    print(f"输出路径：{str(output_path)}")

    try:
        # 实例化 SpeechSynthesizer
        synthesizer = SpeechSynthesizer(
            model=config["model"],
            voice=config["voice"]
        )

        # 调用语音合成 API
        audio = synthesizer.call(text)
        if not audio:
            print('获取语音数据失败')

        # 保存音频文件
        with open(output_path, "wb") as f:
            f.write(audio)

        print(f"\n✅ 语音生成成功！")
        print(f"📁 文件已保存到：{str(output_path)}")

        # 检查文件是否存在后再获取大小
        if output_path.exists():
            print(f"📊 文件大小：{output_path.stat().st_size / 1024:.2f} KB")
            # 输出请求ID和首包延迟信息
            print(f'[Metric] requestId为：{synthesizer.get_last_request_id()}')
            print(f'[Metric] 首包延迟为：{synthesizer.get_first_package_delay()}毫秒')
        else:
            print("⚠️ 文件可能尚未完全保存")

        return str(output_path)

    except Exception as e:
        print(f"\n❌ 语音生成失败！")
        print(f"错误信息：{str(e)}")
        raise e


def speech_synthesis_by_text():
    """通过文字进行语音合成"""
    print("=" * 60)
    print("🎵 阿里云语音合成 (TTS) 工具")
    print("=" * 60)

    # 更友好的界面打印
    counter = 0
    for key, vaule in voices.items():
        counter += 1
        if counter % 3 != 0:
            print(key, vaule, end=' ')
        else:
            print(key, vaule)
    # 选择音色
    voice = input('\n请选择音色发言人：').strip().lower() or 'longhuhu'
    # 默认配置
    DEFAULT_CONFIG = {
        "model": model,  # 模型名称
        "voice": voice,  # 音色
        "format": "mp3"  # 输出格式
    }

    # 显示当前配置
    print(f"\n当前配置：")
    print(f"  模型：{DEFAULT_CONFIG['model']}")
    print(f"  语音：{DEFAULT_CONFIG['voice']}")
    print(f"  格式：{DEFAULT_CONFIG['format']}")
    print(f"  输出目录：{str(OUTPUT_DIR)}")

    # 获取用户输入
    print("\n" + "-" * 50)
    print("请输入要转换的文字（输入完成后，请在新的一行输入 'END' 并按回车来结束输入）：")
    lines = []
    while True:
        line = input().upper()
        if line.strip() == "END":
            break
        lines.append(line)
    text = "\n".join(lines)

    if not text.strip():
        print("❌ 输入为空，程序退出。")
        return
    # 可选：自定义文件名
    custom_name = input("\n请输入自定义文件名（直接回车使用时间戳）：\n> ")
    if custom_name.strip():
        # 移除用户输入中可能包含的扩展名
        filename = custom_name.strip().split('.')[0]
    else:
        filename = None

    print("\n" + "-" * 50)

    try:
        # 生成语音，记得传入配置
        output_path = generate_speech(text, output_filename=filename, config=DEFAULT_CONFIG)
        print(f"\n🎉 任务完成！")
    except KeyboardInterrupt:
        print(f"\n\n⚠️ 用户取消操作")
    except Exception as e:
        print(f"\n💥 发生错误：{str(e)}")
        print("💡 请检查 API 密钥是否正确，以及网络连接是否正常")

if __name__ == "__main__":
    speech_synthesis_by_text()