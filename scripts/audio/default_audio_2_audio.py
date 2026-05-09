"""
default_audio_2_audio - 
可用。使用系统默认音色,可指定音频语言。qwen3-tts-flash模型
Author:仗剑天涯
Date:2026/4/25
"""
import json
import os
from pprint import pprint

import dashscope
import requests

from config.settings import get_api_key, get_output_dir
from core.utils import get_file_path_by_time, get_voices_for_llm_version

model = "qwen3-tts-flash"
voices = get_voices_for_llm_version(model)
languages = {'中文':'Chinese', '英语':'English', '德语':'German', '意大利':'Italian', '葡萄牙语':'Portuguese', '西班牙语':'Spanish', '日语':'Japanese', '韩语':'Korean', '法语':'French', '俄语':'Russian'}
def default_audio_synthesis():
    # 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
    dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
    # 界面功能实现：输出声音可选项
    for key, value in voices.items():
        print(key, value['content'], value['skill'])
    counter = 0
    # 界面功能实现：输出语言可选项
    for key, value in languages.items():
        # 　让显示更容易看
        counter += 1
        if counter % 5 != 0:
            print(key, end=' ')
        else:
            print(key)
    # 选择声音，语言和输入文本
    language_type = languages[input('你想用什么语言读：').strip()]
    voice = input('你想要谁帮你朗读：').strip().capitalize()
    text = '晨起春风来探看，雨沫飞窗吻我唇.喜看弹珠扑面来，何妨吟啸且徐行.天阴时雨亦时停，浮生悲喜意难平.唯愿仗剑天涯去，激扬浊清留美名'
    text = input('请输入文本\n文本语言最好和朗读语言一致：').strip() or text
    # SpeechSynthesizer接口使用方法：dashscope.audio.qwen_tts.SpeechSynthesizer.call(...)
    response = dashscope.MultiModalConversation.call(
        # 如需使用指令控制功能，请将model替换为qwen3-tts-instruct-flash
        model=model,
        # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key = "sk-xxx"
        api_key=get_api_key(),
        text=text,
        voice=voice,
        language_type=language_type, # 建议与文本语种一致，以获得正确的发音和自然的语调。
        # 如需使用指令控制功能，请取消下方注释，并将model替换为qwen3-tts-instruct-flash
        # instructions='语速较快，带有明显的上扬语调，适合介绍时尚产品。',
        # optimize_instructions=True,
        stream=False,
        format='wav'

    )
    print(response)
    # 数据解包，用属性调用
    url = response.output.audio.url
    # resp对象获得的是二进制数据，而非json数据。所以接下来不需要
    # 转化为字典才能访问，直接用resp.content访问里面的数据即可
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    # 下面为错误操作，转化字典
    # data2 = resp.json()
    with open(f'{get_file_path_by_time()}.wav', 'wb') as f:
        f.write(resp.content)
    print(f'下载成功！文件名为：{get_file_path_by_time()}.wav')


if __name__ == '__main__':
    default_audio_synthesis()