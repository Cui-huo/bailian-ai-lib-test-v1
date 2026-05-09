"""
text2text_chat - 

Author:仗剑天涯
Date:2026/4/22
"""
import os
from pprint import pprint

from dashscope import Generation

from config.settings import get_api_key

def chat_robot(messages: list ):
    completion = Generation.call(
        # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
        api_key=get_api_key(),
        model="deepseek-v3.2",
        messages=messages,
        result_format="message",  # 设置结果格式为 message
        enable_thinking=True,
        stream=True,              # 开启流式输出
        incremental_output=True,  # 开启增量输出
    )

    reasoning_content = ""  # 保存完整思考过程
    answer_content = ""     # 完整回复
    is_answering = False    # 是否进入回复阶段

    print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
    # completion是流式调用生成器generator，把服务器不断生成的文本块接收
    for chunk in completion:
        # 数据结构解包，访问字典被封装成属性调用，更方便
        message = chunk.output.choices[0].message
        # 只收集思考内容
        if "reasoning_content" in message:
            if not is_answering:
                print(message.reasoning_content, end="", flush=True)
            reasoning_content += message.reasoning_content

        # 收到 content，开始进行回复
        if message.content:
            if not is_answering:
                print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                is_answering = True
            print(message.content, end="", flush=True)
            answer_content += message.content

    print("\n" + "=" * 20 + "Token 消耗" + "=" * 20 + "\n")
    print(chunk.usage)

def chat_with_ai():
    while True:
        contents = input('请输入对话内容：')
        messages = [{"role": "user", "content": contents}]
        chat_robot(messages)


if __name__ == '__main__':
    chat_with_ai()
