"""
image_to_understand - 
可用。让大模型读取一张本地或者在线图片，然后描述图片上的信息

Author:仗剑天涯
Date:2026/4/23
"""
import base64
import os
from pathlib import Path

import dashscope

from config.settings import get_api_key, get_output_dir

# 各地域配置不同，请根据实际地域修改
dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

"""
把本地图片让大模型理解，并描述
# 将xxx/eagle.png替换为你本地图像的绝对路径
local_path = r"G:/Videototext/dog_and_girl.jpeg"
image_path = f"file://{local_path}"
messages = [
                {'role':'user',
                'content': [{'image': image_path},
                            {'text': '图中描绘的是什么景象?'}]}]
"""

"""
提交一张或者多张图片，让大模型理解并描述
messages = [
{
    "role": "user",
    "content": [
    {"image": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/tiger.png"},
    {"image": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg"},
    {"text": "图中描绘的是什么景象?"}]
}]"""

# 各地域配置不同，请根据实际地域修改
dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

#  编码函数： 将本地文件转换为 Base64 编码的字符串
def encode_image(image_name):
    # 调用settings.py中的配置函数，直接统一获取安全路径！
    output_dir = get_output_dir('assets')
    print(output_dir)
    print(output_dir/image_name)
    with open(output_dir/image_name, "rb") as image_file:
        data = image_file.read()
        print(data[0:50])
        print('1'*40)
        print(base64.b64encode(data)[0:50])
        print('2' * 40)
        return base64.b64encode(data).decode("utf-8")

def understand_image():
    print('示例图片：img.png')
    # 将xxxx/eagle.png替换为你本地图像的绝对路径
    img_name = input('请输入你的图片名：')
    base64_image = encode_image(img_name)
    print(base64_image[0:50])
    text = input('请输入文本：')
    if not text:
        text = "图中描绘的是什么景象?"
    messages = [
        {
            "role": "user",
            "content": [
                # 需要注意，传入Base64，图像格式（即image/{format}）需要与支持的图片列表中的Content Type保持一致。"f"是字符串格式化的方法。
                # PNG图像：  f"data:image/png;base64,{base64_image}"
                # JPEG图像： f"data:image/jpeg;base64,{base64_image}"
                # WEBP图像： f"data:image/webp;base64,{base64_image}"
                {"image": f"data:image/png;base64,{base64_image}"},
                {"text": text},
            ],
        },
    ]


    response = dashscope.MultiModalConversation.call(
        # 若没有配置环境变量， 请用百炼API Key将下行替换为： api_key ="sk-xxx"
        # 各地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
        api_key = get_api_key(),
        model = 'qwen3.6-plus',  # 此处以qwen3.6-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/models
        messages = messages
    )
    print(response.output.choices[0].message.content[0]["text"])


if __name__ == '__main__':
    understand_image()