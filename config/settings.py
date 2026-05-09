"""
settings.py - 
提供统一配置接口管理

Author:仗剑天涯
Date:2026/4/21
"""
import base64
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
# 自动读取 .env 文件并加载到环境变量
load_dotenv()
def get_api_key():
    api_key_value = os.getenv("DASHSCOPE_API_KEY")
    if not api_key_value:
        print('请在.env文件中设置api密钥,即DASHSCOPE_API_KEY的值')
    return api_key_value

# ==================== 本地上传目录配置 ====================
def get_input_dir(sub_dir: str = 'assets') -> Path:
    """
    输入文件名，获取完整本地文件路径，并确保文件存在。
    """
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent.parent

    while True:
        filename = input('请输入文件名：').strip()
        input_path = base_dir / sub_dir / filename
        if input_path.exists():
            return input_path
        else:
            print(f"❌ 文件 '{input_path}' 不存在，请重新输入。")

# ==================== 输出目录配置 ====================
def get_output_dir(sub_dir: str = "output") -> Path:
    """
    获取输出目录，开发环境和打包后环境均适用。
    """
    if getattr(sys, 'frozen', False):
        # 打包后：使用 exe 所在目录作为基准
        base_dir = Path(sys.executable).parent
    else:
        # 开发环境：使用项目根目录（settings.py 在 config 子目录下）
        # config/settings.py -> config -> 项目根目录
        base_dir = Path(__file__).parent.parent

    output_dir = base_dir / sub_dir
    # 确保输出文件夹存在
    output_dir.mkdir(exist_ok=True)
    return output_dir

