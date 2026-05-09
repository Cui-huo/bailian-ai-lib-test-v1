"""
video_to_understand_by_link -

Author:仗剑天涯
Date:2026/4/23
"""
import base64
from pathlib import Path

import dashscope
import os

from config.settings import get_api_key
from core.utils import base64_encode_by_name

# 各地域配置不同，请根据实际地域修改
dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

"""
# 本地图像列表提交大模型，理解并描述
root_project = Path(__file__).parent.parent.parent
local_path = root_project / 'assets'
# print(image_path/image_name)
local_path1 = local_path/"img_1.png"
local_path2 = local_path/"img_2.png"
local_path3 = local_path/"img_4.png"
local_path4 = local_path/"img_6.png"

image_path1 = f"file://{local_path1}"
image_path2 = f"file://{local_path2}"
image_path3 = f"file://{local_path3}"
image_path4 = f"file://{local_path4}"

messages = [{'role':'user',
              #  传入图像列表时，fps 参数适用于Qwen3.6、Qwen3-VL 和 Qwen2.5-VL系列模型
             'content': [{'video': [image_path1,image_path2,image_path3,image_path4],"fps":2},
                            {'text': '这段视频描绘的是什么景象?'}]}]
"""

"""
# 本地视频提交大模型
# 将xxxx/test.mp4替换为你本地视频的绝对路径
local_path = "G:\\Videototext\\1.mp4"
# 大模型能接受的URL，标志资源+位置
video_path = f"file://{local_path}"
messages = [
                {'role':'user',
                # fps参数控制视频抽帧数量，表示每隔1/fps 秒抽取一帧
                'content': [{'video': video_path,"fps":2},
                            {'text': '这段视频描绘的是什么景象？'}]}]
"""

"""
在线视频链接提交大模型
messages = [
    {"role": "user",
        "content": [
            # fps 可参数控制视频抽帧频率，表示每隔 1/fps 秒抽取一帧，完整用法请参见：https://help.aliyun.com/zh/model-studio/use-qwen-by-calling-api?#2ed5ee7377fum
            {"video": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241115/cqqkru/1.mp4","fps":2},
            {"text": "这段视频的内容是什么?"}
        ]
    }
]"""


def local_video_understand():
    # 将xxxx/test.mp4替换为你本地视频的绝对路径
    # 参考值video_name = "1.mp4"
    print('请输入mp4格式的视频名称:如1.mp4')
    # 编码函数： 将本地文件转换为 Base64 编码的字符串
    base64_video = base64_encode_by_name()

    messages = [{'role': 'user',
                 # fps参数控制视频抽帧数量，表示每隔1/fps 秒抽取一帧
                 'content': [{'video': f"data:video/mp4;base64,{base64_video}", "fps": 2},
                             {'text': '这段视频描绘的是什么景象？'}]}]

    response = dashscope.MultiModalConversation.call(
        # 若没有配置环境变量， 请用百炼API Key将下行替换为： api_key ="sk-xxx"
        api_key=get_api_key(),
        model='qwen3.6-plus',
        messages=messages
    )

    print(response.output.choices[0].message.content[0]["text"])


def online_video_understand():
    """
    在线视频链接提交大模型
    """
    video_url = input('请输入在线视频链接：').strip()
    if not video_url:
        # 默认示例链接
        video_url = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241115/cqqkru/1.mp4"

    messages = [
        {"role": "user",
         "content": [
             # fps 可参数控制视频抽帧频率，表示每隔 1/fps 秒抽取一帧，完整用法请参见：https://help.aliyun.com/zh/model-studio/use-qwen-by-calling-api?#2ed5ee7377fum
             {"video": video_url, "fps": 2},
             {"text": "这段视频的内容是什么?"}
         ]
         }
    ]

    response = dashscope.MultiModalConversation.call(
        # 若没有配置环境变量， 请用百炼API Key将下行替换为： api_key ="sk-xxx"
        api_key=get_api_key(),
        model='qwen3.6-plus',
        messages=messages
    )

    print(response.output.choices[0].message.content[0]["text"])


def video_understand():
    print("=" * 50)
    print("🎬 视频理解工具")
    print("=" * 50)
    print("1. 在线视频链接理解")
    print("2. 本地视频理解")
    choice = input("请选择 (1/2): ").strip()

    if choice == '1':
        online_video_understand()
    elif choice == '2':
        local_video_understand()
    else:
        print("❌ 无效选择，程序退出。")

if __name__ == '__main__':
    video_understand()