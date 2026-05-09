"""
local_audio_2_audio - 
可用。本地音频声音复刻。建议音频10-20秒
使用qwen3-tts-vc-2026-01-22模型克隆声音
功能：
    1. 使用本地音频文件（建议10-20秒）复刻专属音色
    2. 输入任意文本，用复刻的音色进行语音合成
    3. 下载生成的音频文件到本地

模型：
    - 声音复刻：qwen-voice-enrollment
    - 语音合成：qwen3-tts-vc-2026-01-22
Author:仗剑天涯
Date:2026/4/25
"""
from core.utils import get_file_path_by_time
import requests
import base64
import pathlib
import dashscope
from pathlib import Path

from config.settings import get_api_key, get_output_dir, get_input_dir

# ======= 常量配置 =======
DEFAULT_TARGET_MODEL = "qwen3-tts-vc-2026-01-22"  # 声音复刻、语音合成要使用相同的模型
DEFAULT_PREFERRED_NAME = "guanyu"
DEFAULT_AUDIO_MIME_TYPE = "audio/wav"  # 修正为wav格式，与源文件一致


def create_voice(local_file_path: str,
                 target_model: str = DEFAULT_TARGET_MODEL,
                 preferred_name: str = DEFAULT_PREFERRED_NAME,
                 audio_mime_type: str = DEFAULT_AUDIO_MIME_TYPE) -> str:
    """
    创建音色，并返回 voice 参数
    """
    api_key = get_api_key()

    file_path_obj = pathlib.Path(local_file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"音频文件不存在: {local_file_path}")

    # 将音频文件编码为 Base64
    base64_str = base64.b64encode(file_path_obj.read_bytes()).decode()
    data_uri = f"data:{audio_mime_type};base64,{base64_str}"

    # 声音复刻 API 地址
    url = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization"
    payload = {
        "model": "qwen-voice-enrollment",  # 固定值，不要修改
        "input": {
            "action": "create",
            "target_model": target_model,
            "preferred_name": preferred_name,
            "audio": {"data": data_uri}
        }
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f"创建 voice 失败: {resp.status_code}, {resp.text}")

    try:
        voice_id = resp.json()["output"]["voice"]
        print(f"✅ 音色创建成功，Voice ID: {voice_id}")
        return voice_id
    except (KeyError, ValueError) as e:
        raise RuntimeError(f"解析 voice 响应失败: {e}")


def local_audio_synthesis():
    # 输入文件名，获取源音频文件完整路径
    LOCAL_FILE_PATH = get_input_dir()
    # 设置 API 基础 URL
    dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

    text = input('请输入文本：\n').strip()
    if not text:
        print("❌ 文本不能为空")
        return

    # 1. 创建专属音色（使用本地音频文件）
    print("🎤 正在创建专属音色...")
    try:
        my_voice = create_voice(str(LOCAL_FILE_PATH))
    except Exception as e:
        print(f"❌ 音色创建失败: {e}")
        return

    # 2. 使用复刻音色进行语音合成
    print("🔊 正在合成语音...")
    response = dashscope.MultiModalConversation.call(
        model=DEFAULT_TARGET_MODEL,
        api_key=get_api_key(),
        text=text,
        voice=my_voice,  # 使用刚创建的专属音色
        stream=False
    )

    # 3. 提取音频 URL
    try:
        audio_url = response.output.audio.url
        print(f"音频 URL: {audio_url}")
    except AttributeError:
        print(f"❌ 语音合成失败: {response}")
        return

    # 4. 下载音频文件
    print("📥 正在下载音频...")
    try:
        resp = requests.get(audio_url, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ 下载失败: {e}")
        return

    # 5. 保存音频文件（使用时间戳保证文件名唯一）
    output_path = get_file_path_by_time()  # 假设返回不带后缀的路径，如 /output/20260425_120000
    output_file = f"{output_path}.wav"
    with open(output_file, 'wb') as f:
        f.write(resp.content)
    print(f"✅ 下载成功！文件保存为: {output_file}")


if __name__ == '__main__':
    local_audio_synthesis()

