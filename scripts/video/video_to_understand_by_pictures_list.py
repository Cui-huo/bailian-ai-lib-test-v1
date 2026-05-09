"""
video_to_understand - 

Author:仗剑天涯
Date:2026/4/23
"""
import os
from pathlib import Path

from openai import OpenAI
from config.settings import get_api_key
import base64

# 编码函数： 将本地文件转换为 Base64 编码的字符串
def encode_image(image_name):
    root_project = Path(__file__).parent.parent.parent
    image_path = root_project / 'assets'
    print(image_path/image_name)
    with open(image_path/image_name, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def video_understand_by_pictures():
    base64_image1 = encode_image("img_2.png")
    base64_image2 = encode_image("img_3.png")
    base64_image3 = encode_image("img_5.png")
    base64_image4 = encode_image("img_6.png")

    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        # 各地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
        api_key=get_api_key(),
        # 各地域配置不同，请根据实际地域修改
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen3.6-plus", # 此处以qwen3.6-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/models
        # 通过图片列表理解视频
        # messages=[{"role": "user","content": [
        #     # 传入图像列表时，用户消息中的"type"参数为"video"
        #      {"type": "video","video": [
        #      "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/xzsgiz/football1.jpg",
        #      "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/tdescd/football2.jpg",
        #      "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/zefdja/football3.jpg",
        #      "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/aedbqh/football4.jpg"],
        #      "fps":2},
        #      {"type": "text","text": "描述这个视频的具体过程"},
        # ]}]

        messages=[
        {"role": "user","content": [
            {"type": "video","video": [
                f"data:image/jpeg;base64,{base64_image1}",
                f"data:image/jpeg;base64,{base64_image2}",
                f"data:image/jpeg;base64,{base64_image3}",
                f"data:image/jpeg;base64,{base64_image4}",]},
            {"type": "text","text": "描述这个视频的具体过程"},
        ]}]

    )

    print(completion.choices[0].message.content)


if __name__ == '__main__':
    video_understand_by_pictures()