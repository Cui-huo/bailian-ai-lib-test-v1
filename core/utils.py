"""
utils.py - 
所有模块都可能用到的工具函数、通用函数

Author:仗剑天涯
Date:2026/4/21
"""
import base64
from datetime import datetime
from pathlib import Path

import numpy as np
import requests
import soundfile
from config.settings import get_output_dir, get_input_dir


def get_language_code():
    language_codes = {"英语": 'en', "中文": 'zh', "俄语": 'ru', "法语": 'fr', "德语": 'de', "葡萄牙语": 'pt',
                      "韩语": 'ko', "日语": 'ja', "粤语": 'yue'}
    return language_codes

def get_voices_for_llm_version(modle:str):
    modle.strip().lower()
    if modle in {'qwen3.5_omni_plus', 'qwen3.5-omni', 'qwen3.5-omni-realtime'}:
        voices = {'Sunnybobi': '大大咧咧的社恐邻家姑娘', 'Raymond': "声音清亮，爱吃外/卖的宅男",
          'Theo Calm': '在静默处传递理解，在言语间疗愈人心', 'Li Cassian': '话中三分留白、七分察言观色',
          'Qiao': '超关键！她不是普通可爱，而是表面甜妹，个性十足', 'Joseph Chen': '我是阿樸伯，本名陳志樸，南洋老華僑。',
          'Marina': '一个在多元文化城市中长大的女孩'}
        return voices
    elif modle == "qwen3-livetranslate-flash":
        voices2 = {"Kiki": {'skill': "粤语", 'content': '甜美的港妹闺蜜。'},
                  'Cherry': {'skill': ['中文', '英语', '法语', '德语', '俄语', '意大利语', '西班牙语', '葡萄牙语', '日语', '韩语'],
                            'content': '阳光积极、亲切自然小姐姐。'},
                  'Nofish': {'skill': ['中文', '英语', '法语', '德语', '俄语', '意大利语', '西班牙语', '葡萄牙语', '日语', '韩语'],
                            'content': '不会翘舌音的设计师。'},
                  "Jada": {'skill': "中文", 'content': '风风火火的沪上阿姐。'},
                  "Dylan": {'skill': "中文", 'content': '北京胡同里长大的少年。'},
                  "Sunny": {'skill': "中文", 'content': '甜到你心里的川妹子。'},
                  "Peter": {'skill': "中文", 'content': '天津相声，专业捧人。'},
                  "Eric": {'skill': "中文", 'content': '一个跳脱市井的四川成都男子。'}}
        return voices2
    elif modle == "qwen3-tts-flash":
        voices3 = {"Chelsie": {
            'skill': ['中文', '英语', '法语', '德语', '俄语', '意大利语', '西班牙语', '葡萄牙语', '日语', '韩语'],
            'content': '二次元虚拟女友（女性）'}, "Jennifer": {
            'skill': ['中文', '英语', '法语', '德语', '俄语', '意大利语', '西班牙语', '葡萄牙语', '日语', '韩语'],
            'content': '品牌级、电影质感般美语女声（女性）'}, "Marcus": {
            'skill': ['中文', '英语', '法语', '德语', '俄语', '意大利语', '西班牙语', '葡萄牙语', '日语', '韩语'],
            'content': '面宽话短，心实声沉——老陕的味道（男性）'}, 'Bunny': {
            'skill': ['中文', '英语', '法语', '德语', '俄语', '意大利语', '西班牙语', '葡萄牙语', '日语', '韩语'],
            'content': '“萌属性”爆棚的小萝莉（女性）'}, "Mia":{"skill":["中文"], "content":"以细腻声音，传递慢生活美学与日常治愈力量的生活艺术家-34"}}
        return voices3
    elif modle == "cosyvoice-v2":
        voices4 = {'longcheng_v2': '阳光男声-1', 'longhua_v2': '活泼女童-1', 'longshu_v2': '新闻男声-1',
                  'longwan_v2': '普通话女声-1', 'longxiaochun_v2': '温柔姐姐-1', 'longxiaoxia_v2': '温柔女声-1',
                  'loongbella_v2': '新闻女声-1', 'longhuhu': '天真烂漫女童（童声）-1', 'longanpei': '青少年教师女-1',
                  'longdaiyu': '娇率才女音-1', 'longgaoseng': '得道高僧音-1', 'longyingmu': '优雅知性女-1',
                  'longyingxun': '年轻青涩男-1', 'longyingxiao': '甜美销售女声-1', 'longyumi_v2': '严肃年轻女声-1',
                  'longyichen': '自由奔放男声-1', 'longxiu_v2': '博学故事家男声-1', 'longmiao_v2': '韵律感强女声-1',
                  'longyue_v2': '温暖磁性女声-1', 'longnan_v2': '智慧年轻男声-1', 'longyuan_v2': '温暖治愈女声-1',
                  'longanqin': '平易近人活泼女声-1', 'longqiang_v2': '浪漫迷人女声-1', 'longhan_v2': '温暖专注男声-1',
                  'longxing_v2': '温柔邻家女声-1', 'longfeifei_v2': '甜美精致女声-1',
                  'longxiaocheng_v2': '磁性男低音-1', 'longzhe_v2': '面冷心热男声-1'}
        return voices4
    else:
        print('无默认保存的音色列表')
        return None

# 选择默认输出路径，时间戳做文件名（缺格式后缀），获取路径
def get_file_path_by_time():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'{get_output_dir()}/{timestamp}'

# 直接返回时间戳
def get_timestamp_by_time():
    return datetime.now().strftime('%Y%m%d_%H%M%S')


# 读取专属文件夹assets里的本地文件，转码成utf-8字符串
def base64_encode_by_name():
    file_path = get_input_dir()
    while True:
        if not file_path.exists():
            print('文件不存在！请重新输入！')
        else:
            with open(file_path, 'rb') as file:
                data = file.read()
            return base64.b64encode(data).decode('utf-8')

# 读取专属文件夹assets里的本地文件，转码成utf-8字符串
def base64_encode_by_name_v2(input_path:Path):
    if not input_path.exists():
        print('文件不存在！请检查输入')
        return None
    with open(input_path, 'rb') as file:
        data = file.read()
    return base64.b64encode(data).decode('utf-8')

def get_file_by_url(url, format):
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        # 文件写入
        with open(f'{get_output_dir()}/{get_timestamp_by_time()}.{format}', 'wb') as f:
            f.write(resp.content)
        print(f'{get_output_dir()}/{get_timestamp_by_time()}.{format}')
        print('文件保存成功！')
    except:
        print('文件获取失败！')

# 3. 处理流式响应并解码音频
def deal_with_stream_flow(completion):
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
def save_audio_form_llm(audio_base64_string):
    # 1. Base64 解码 -> 原始字节数据
    wav_bytes = base64.b64decode(audio_base64_string)
    # 2. 字节数据 -> NumPy 音频数组（16位有符号整型，标准 WAV 位深）
    audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
    # 3. NumPy 数组 -> 写入 WAV 文件（采样率需与生成时一致）
    soundfile.write("audio_assistant.wav", audio_np, samplerate=24000)
    print("\n音频文件已保存至：audio_assistant.wav")

# 只针对国内大模型，png为默认格式。国外个别不是
def download_and_save_image(image_url: str, output_dir: Path) -> str:
    """
    从URL下载图片，并自动根据响应头识别格式并保存。
    Args:
        image_url: 图片的URL
        output_dir: 保存的目录
    Returns:
        保存的文件路径，若失败返回None
    """
    try:
        # 流式下载
        response = requests.get(image_url, stream=True, timeout=30)
        response.raise_for_status()
        # 1. 从响应头获取内容类型，例如 'image/png'
        content_type = response.headers.get('Content-Type', 'image/png')
        # 2. 从内容类型提取文件后缀，例如 'png'
        extension = content_type.split('/')[-1] if '/' in content_type else 'png'
        # 3. 生成文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qwen_img_{timestamp}.{extension}"
        save_path = output_dir / filename
        # 4. 保存文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ 图片保存为: {save_path}")
        return str(save_path)
    except Exception as e:
        print(f"❌ 下载图片失败: {e}")
        return None