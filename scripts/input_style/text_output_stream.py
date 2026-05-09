"""
output_stream - 

Author:仗剑天涯
Date:2026/4/22
"""
import os
from openai import OpenAI

from config.settings import get_api_key

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key=get_api_key(),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen-plus",  # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': '你是谁？'}],
    stream=True,
    stream_options={"include_usage": True}
    )
for chunk in completion:
    print(chunk.model_dump_json())