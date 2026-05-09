"""
image_to_answer.py - 图片问答（流式思考 + 美化答案）

功能：上传一张图片并提问，模型会实时输出思考过程，并在最后给出格式美观的答案。
      该脚本兼容命令行终端，支持 LaTeX 公式美化。

Author: 仗剑天涯
Date: 2026/4/23
"""
import os
import dashscope
from config.settings import get_api_key
from core.utils import base64_encode_by_name
from rich.console import Console            # <--- 新增，用于美观输出
from rich.markdown import Markdown          # <--- 新增，用于渲染 Markdown/LaTeX
from rich.panel import Panel                # <--- 新增，用于为输出添加方框

dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

def answer_by_image_and_text():
    console = Console()                     # 创建美化控制台对象

    # 1. 获取图片和用户问题
    print('16888.png中有数学题')
    base64_str = base64_encode_by_name()
    uri = f'data:image/png;base64,{base64_str}'
    text = input('请输入问题：').strip() or '请解答这道题？'

    messages = [{"role": "user", "content": [{"image": uri}, {"text": text}]}]

    # 2. 流式调用，实时展示思考过程，累积最终答案
    answer_content = ""                     # 用于完整累积最终答案
    print("=" * 20 + "思考过程" + "=" * 20)

    response = dashscope.MultiModalConversation.call(
        api_key=get_api_key(),
        model="qwen3.6-plus",
        messages=messages,
        stream=True,
        enable_thinking=True
    )

    for chunk in response:
        message = chunk.output.choices[0].message
        content_list = message.content
        reasoning_content_chunk = message.get("reasoning_content", None)

        # 如果有思考内容且没有正式回答，则实时打印思考过程
        if reasoning_content_chunk is not None and content_list == []:
            print(message.reasoning_content, end="", flush=True)

        # 如果有正式回答内容，则只累积，不实时打印
        elif content_list:
            text_chunk = content_list[0].get("text", "")
            answer_content += text_chunk

    # 3. 美化输出最终答案
    console.print(Panel.fit(
        Markdown(answer_content),
        title="[bold green]完整回复[/]",
        border_style="green"
    ))

if __name__ == '__main__':
    answer_by_image_and_text()