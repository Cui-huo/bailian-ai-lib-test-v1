"""
image_to_text - 
可用。提取图片文字信息：以车票为例
Author:仗剑天涯
Date:2026/4/23
"""
import base64
import os
import dashscope
from config.settings import get_api_key, get_output_dir
from core.utils import base64_encode_by_name

# 以下为北京地域base_url，若使用弗吉尼亚地域模型，需要将base_url换成 https://dashscope-us.aliyuncs.com/api/v1
# 若使用新加坡地域的模型，需将base_url替换为：https://dashscope-intl.aliyuncs.com/api/v1
dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

PROMPT_TICKET_EXTRACTION = """
请提取车票图像中的发票号码、车次、起始站、终点站、发车日期和时间点、座位号、席别类型、票价、身份证号码、购票人姓名。
要求准确无误的提取上述关键信息、不要遗漏和捏造虚假信息，模糊或者强光遮挡的单个文字可以用英文问号?代替。
返回数据格式以json方式输出，格式为：{'发票号码'：'xxx', '车次'：'xxx', '起始站'：'xxx', '终点站'：'xxx', '发车日期和时间点'：'xxx', '座位号'：'xxx', '席别类型'：'xxx','票价':'xxx', '身份证号码'：'xxx', '购票人姓名'：'xxx'"},
"""

def get_text_by_image():
    print('示例：车票图片为666.jpg')
    # 在本地文件夹读取文件，编码成字符串
    base64_str = base64_encode_by_name()
    # 666.jpg为车票图片
    # 获得大模型需要的URI
    uri = f'data:img/jpeg;base64,{base64_str}' # 扩展名不可写成.jpg
    print(uri)

    try:
        response = dashscope.MultiModalConversation.call(
            model='qwen-vl-ocr-latest',
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            # 各地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
            api_key=get_api_key(),
            messages=[{
                'role': 'user',
                'content': [
                    {'image': uri
                     # # 输入图像的最小像素阈值，小于该值图像会放大，直到总像素大于min_pixels
                     # ,"min_pixels": 32 * 32 * 3,
                     # # 输入图像的最大像素阈值，超过该值图像会缩小，直到总像素低于max_pixels
                     # "max_pixels": 32 * 32 * 8192,
                     # # 是否开启图像自动转正功能
                     # "enable_rotate": False,
                    },
                    # 未设置内置任务时，支持在text字段中传入Prompt，若未传入则使用默认的Prompt：Please output only the text content from the image without any additional descriptions or formatting.
                    {'text': PROMPT_TICKET_EXTRACTION}
                ]
            }]
        )
        print(response.output.choices[0].message.content[0]['text'])
    except Exception as e:
        print(f"An error occurred: {e}")


    """
    输入图片URL，获取信息
    try:
        response = dashscope.MultiModalConversation.call(
            model='qwen-vl-ocr-latest',
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            # 各地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
            api_key=get_api_key(),
            messages=[{
                'role': 'user',
                'content': [
                    {'image': 'https://img.alicdn.com/imgextra/i2/O1CN01ktT8451iQutqReELT_!!6000000004408-0-tps-689-487.jpg',
                     # 输入图像的最小像素阈值，小于该值图像会放大，直到总像素大于min_pixels
                     "min_pixels": 32 * 32 * 3,
                     # 输入图像的最大像素阈值，超过该值图像会缩小，直到总像素低于max_pixels
                     "max_pixels": 32 * 32 * 8192,
                     # 是否开启图像自动转正功能
                     "enable_rotate": False,
                    },
                    # 未设置内置任务时，支持在text字段中传入Prompt，若未传入则使用默认的Prompt：Please output only the text content from the image without any additional descriptions or formatting.
                    {'text': PROMPT_TICKET_EXTRACTION}
                ]
            }]
        )
        print(response.output.choices[0].message.content[0]['text'])
    except Exception as e:
        print(f"An error occurred: {e}")"""