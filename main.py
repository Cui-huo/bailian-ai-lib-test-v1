"""
main.py - AI 工具箱主入口（命令行交互式菜单）

功能说明：
    整合了阿里云百炼平台的多种 AI 能力，包括：
    - 语音合成（多种模型和方式）
    - 语音翻译
    - 声音复刻与设计
    - 图片理解与文字提取
    - 拍照答题
    - 视频理解
    - 视频生成与续写
    - 文生图
    - 多轮对话
    - SSE 音频解析

Author: 仗剑天涯
Date: 2026/4/27
"""

import sys
from pathlib import Path

from scripts.text.text2text_chat import chat_with_ai

# 如果打包成 exe，确保能导入同目录下的模块
if getattr(sys, 'frozen', False):
    exe_dir = Path(sys.executable).parent
    if str(exe_dir) not in sys.path:
        sys.path.insert(0, str(exe_dir))

# ==================== 导入所有功能模块 ====================

# ---------- 音频相关 ----------
from scripts.audio.audio_synthesis_2_audio_by_url_and_text import audio_synthesis_by_url_and_text
from scripts.audio.audio_translate_with_menu_2_audio import audio_translate_online_or_local
from scripts.audio.default_audio_2_audio import default_audio_synthesis
from scripts.audio.local_audio_2_audio import local_audio_synthesis
# ---------- 图像相关 ----------
from scripts.image.image_to_answer import answer_by_image_and_text
from scripts.image.image_to_text import get_text_by_image
from scripts.image.image_to_understand import understand_image
# ---------- 多模态 ----------
from scripts.multimodal.text_to_text_and_audio import get_text_and_audio_by_chat
from scripts.multimodal.video_synthesis_by_video_and_image import sample_sync_call
# ---------- 文本相关 ----------
from scripts.text.parse_sse import parse_sse_to_wav
from scripts.text.text2picture_by_qwen import get_url_by_text, get_picture
from scripts.text.text2video_by_async import text_to_video_by_async
from scripts.text.text_and_audio_prompt_2_audio import audio_synthesis_by_text_and_prompt
from scripts.text.text_to_speech_synthesis import speech_synthesis_by_text
from scripts.text.text2picture_by_wan import get_img_by_text_v2
# ---------- 视频相关 ----------
from scripts.video.video_to_understand_with_menu import local_video_understand, video_understand
from scripts.video.video_to_understand_by_pictures_list import video_understand_by_pictures


# ==================== 子菜单函数 ====================

def menu_audio():
    """音频功能子菜单"""
    while True:
        print("\n" + "-" * 40)
        print("🎵 音频功能")
        print("-" * 40)
        print("1. 文字转语音 (CosyVoice-v2，自定义音色)")
        print("2. 文字转语音 (系统默认音色 qwen3-tts-flash)")
        print("3. 语音翻译 (上传URL或本地音频，翻译并输出)")
        print("4. 声音复刻 (通过URL音频复刻音色)")
        print("5. 声音复刻 (通过本地音频复刻音色)")
        print("6. 声音设计 (通过文字描述生成专属音色并合成)")
        print("7. SSE 音频解析 (将Base64流式数据解码为WAV)")
        print("8. 返回主菜单")
        choice = input("请选择: ").strip()

        if choice == "1":
            speech_synthesis_by_text()
        elif choice == "2":
            default_audio_synthesis()
        elif choice == "3":
            audio_translate_online_or_local()
        elif choice == "4":
            audio_synthesis_by_url_and_text()
        elif choice == "5":
            local_audio_synthesis()
        elif choice == "6":
            audio_synthesis_by_text_and_prompt()
        elif choice == "7":
            parse_sse_to_wav()
        elif choice == "8":
            break
        else:


            print("❌ 无效选项，请重新输入")


def menu_image():
    """图像功能子菜单"""
    while True:
        print("\n" + "-" * 40)
        print("🖼️ 图像功能")
        print("-" * 40)
        print("1. 图片理解 (上传图片，AI 回答相关问题)")
        print("2. 图片文字提取 (OCR，以车票为例)")
        print("3. 拍照答题 (上传题目图片，AI 解答)")
        print("4. 返回主菜单")
        choice = input("请选择: ").strip()

        if choice == "1":
            understand_image()
        elif choice == "2":
            get_text_by_image()
        elif choice == "3":
            answer_by_image_and_text()
        elif choice == "4":
            break
        else:
            print("❌ 无效选项，请重新输入")


def menu_video():
    """视频功能子菜单"""
    while True:
        print("\n" + "-" * 40)
        print("🎬 视频功能")
        print("-" * 40)
        print("1. 视频理解 (本地视频或在线URL)")
        print("2. 视频理解 (通过图片列表)")
        print("3. 视频续写 (图+视频生成中间画面，Token已耗尽)")
        print("4. 返回主菜单")
        choice = input("请选择: ").strip()

        if choice == "1":
            video_understand()
        elif choice == "2":
            video_understand_by_pictures()
        elif choice == "3":
            print("⚠️ 该功能 Token 额度已耗尽，暂时无法使用。")
            sample_sync_call()
        elif choice == "4":
            break
        else:
            print("❌ 无效选项，请重新输入")


def menu_generation():
    """生成类功能子菜单（文生图、文生视频）"""
    while True:
        print("\n" + "-" * 40)
        print("🎨 生成功能")
        print("-" * 40)
        print("1. 文生图 (千问 qwen-image-2.0-pro，同步)")
        print("2. 文生图 (万相 wan2.7-image-pro，异步)")
        print("3. 文生视频 (万相 wan2.7-t2v，异步)")
        print("4. 返回主菜单")
        choice = input("请选择: ").strip()

        if choice == "1":
            get_picture()
        elif choice == "2":
            get_img_by_text_v2()
        elif choice == "3":
            text_to_video_by_async()
        elif choice == "4":
            break
        else:
            print("❌ 无效选项，请重新输入")


def menu_chat():
    """对话功能子菜单"""
    while True:
        print("\n" + "-" * 40)
        print("💬 对话功能")
        print("-" * 40)
        print("1. 纯文本多轮对话 (DeepSeek-v3.2)")
        print("2. 多模态对话 (文本+音频回复)")
        print("3. 返回主菜单")
        choice = input("请选择: ").strip()

        if choice == "1":
            chat_with_ai()
        elif choice == "2":
            get_text_and_audio_by_chat()
        elif choice == "3":
            break
        else:
            print("❌ 无效选项，请重新输入")


# ==================== 主菜单 ====================

def main():
    while True:
        print("\n" + "=" * 50)
        print("   🚀 AI 工具箱")
        print("=" * 50)
        print("1. 音频功能 (语音合成、翻译、声音复刻)")
        print("2. 图像功能 (图片理解、文字提取、拍照答题)")
        print("3. 视频功能 (视频理解、视频续写)")
        print("4. 生成功能 (文生图、文生视频)")
        print("5. 对话功能 (多轮对话、多模态聊天)")
        print("6. 退出程序")
        choice = input("请输入选项 (1/2/3/4/5/6): ").strip()

        if choice == "1":
            menu_audio()
        elif choice == "2":
            menu_image()
        elif choice == "3":
            menu_video()
        elif choice == "4":
            menu_generation()
        elif choice == "5":
            menu_chat()
        elif choice == "6":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选项，请重新输入")


if __name__ == "__main__":
    main()