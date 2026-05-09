"""
text2picture - 
用wan2.7文生图，异步调用
Author:仗剑天涯
Date:2026/4/24
"""
import os
from pathlib import Path

import dashscope
import requests
from dashscope.aigc.image_generation import ImageGeneration
from dashscope.api_entities.dashscope_response import Message
from config.settings import get_api_key, get_output_dir, get_input_dir
from core.utils import get_timestamp_by_time, get_file_by_url

def get_img_by_text_v2():

    # 以下为北京地域base_url，各地域的base_url不同
    dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    # 各地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
    api_key = get_api_key()
    format = 'png'
    text = "超高清，农村田园风格，小村子里一户人家，后面是生机勃勃的菜园，西侧近处是养的鸡圈和鸭圈，里面是刚刚长出绒毛的黄色的小鹅，黑中带黄的小鸭子，还有小鸡仔。西侧更远处是长方形约半亩的地，种的玉米和花生种子。期中玉米已经有小小的绿色叶子了。爸爸在修鸭舍，妈妈在给菜园浇水，儿子在屋里学习AI。一副忙碌而有序，富有生命力的和谐画卷"
    text = input('请输入图片描述：').strip() or text

    message = Message(role="user",content=[{"text": text}])

    # 提交异步任务
    print("提交异步任务...")
    response = ImageGeneration.async_call(
        model="wan2.7-image-pro",
        api_key=api_key,
        messages=[message],
        enable_sequential=False,
        n=1,
        format = format,
        size="2K"
    )

    if response.status_code == 200:
        print(f"任务提交成功，任务ID: {response.output.task_id}")

        # 等待任务完成
        status = ImageGeneration.wait(task=response, api_key=api_key)

        if status.output.task_status == "SUCCEEDED":
            print("任务完成!")
            print(f"结果:")
            print(status)
            url = status.output.choices[0].message.content[0].get("image", '')
            # 公用函数，负责通过URL下载文件到默认文件夹
            get_file_by_url(url, format)

        else:
            print(f"任务失败，状态: {status.output.task_status}")
    else:
        print(f"任务创建失败: {response.code} - {response.message}")



if __name__ == "__main__":
    try:
        get_img_by_text_v2()
    except Exception as e:
        print(f"错误: {e}")