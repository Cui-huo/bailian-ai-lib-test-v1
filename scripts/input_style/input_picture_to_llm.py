"""
input_picture_to_llm - 

Author:仗剑天涯
Date:2026/4/22
"""
import json
import os
from pprint import pprint

from openai import OpenAI

from config.settings import get_api_key

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key=get_api_key(),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen-vl-plus",  # 此处以qwen-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[{"role": "user","content": [
            {"type": "image_url",
             "image_url": {"url": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"}},
            {"type": "text", "text": "这是什么"},
            ]}]
    )
# 错误示例：把json格式字符串转字典
# data = completion.model_dump_json().json()
# pprint(data)
# print('1='*30)
# 把json格式字符串转字典法二
data2 = json.loads(completion.model_dump_json())
pprint(data2)
print('2='*30)
# 把json格式字符串转字典法三
data3 = completion.model_dump()
pprint(data3)
print('3='*30)
content = data2["choices"][0]["message"]["content"]
content2 = completion.choices[0].message.content
pprint(content)
print('4='*30)
pprint(content2)
