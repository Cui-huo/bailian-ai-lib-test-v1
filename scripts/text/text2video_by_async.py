"""
text2video_by_async - 

Author:仗剑天涯
Date:2026/4/22
"""
from http import HTTPStatus
from pathlib import Path
import requests
from dashscope import VideoSynthesis
import dashscope
import os, time
from config.settings import get_api_key, get_output_dir
from core.utils import base64_encode_by_name

prompt1 = """## 水墨动画风格提示词

镜头1：【惊喜】室内，广角固定镜头，一位身着素白长衫、束发未戴冠的年轻书生立于窗前，窗棂挂着晶莹雨珠。他推开窗户，雨后清新的空气与细腻雨沫轻拂在他脸上，远处动物公园的绿荫在晨雾中若隐若现。他闭上眼，深吸一口气，嘴角扬起惊喜的微笑，轻声吟诵诗句。宋代水墨动画风格，宣纸纹理，淡墨晕染，画面清新雅致。

镜头2：【潇洒】视角切至书生背部，镜头跟随他转身，他手持一把油纸伞（未撑开），大步流星推门走入雨中，雨滴在伞面上溅起细碎水花。他昂首阔步，衣袂飘飘，姿态豪迈，放声吟诵诗句。水墨风格，飞白笔触，强调衣物的飘逸感与人物潇洒的动态。

镜头3：【沉郁】镜头缓慢推进至书生面部特写，雨势渐大，天色转阴。雨水顺着他的发丝滴落，他低下头，眉心微蹙，若有所思，口中低吟诗句，神情略显沉郁。背景的动物公园景色在水雾中变得朦胧，色调转为淡雅的灰蓝，强化情绪氛围。

镜头4：【释然】镜头拉远，雨过天晴，阳光穿透云层。书生立于窗前，已收起愁容，他望向远方沐浴在金光下的城市与公园，眼神平静而释然。他再次轻声吟诵，脸上浮现豁达的微笑。水墨风格，画面留白三分，意境悠远"""

# 输出目录（桌面）
OUTPUT_DIR = get_output_dir()
OUTPUT_DIR.mkdir(exist_ok=True)


def sample_async_call_t2v(CONFIG:dict):
    # call async api, will return the task information
    # you can get task status with the returned task id.
    rsp = VideoSynthesis.async_call(
        api_key=CONFIG["api_key"],
        model=CONFIG["model"],
        prompt=CONFIG["prompt"],
        audio_url=CONFIG["audio_url"],
        resolution=CONFIG["resolution"],
        ratio=CONFIG["ratio"],
        duration=CONFIG['duration'],
        negative_prompt=CONFIG["negative_prompt"],
        prompt_extend=CONFIG["prompt_extend"],
        watermark=CONFIG["watermark"],
        seed=CONFIG["seed"])
    print(rsp)
    if rsp.status_code == HTTPStatus.OK:
        print("task_id: %s" % rsp.output.task_id)
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))

    # get the task information include the task status.
    status = VideoSynthesis.fetch(task=rsp, api_key=get_api_key())
    if status.status_code == HTTPStatus.OK:
        print(status.output.task_status)  # check the task status
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (status.status_code, status.code, status.message))

    # 调用fetch（）直到任务状态不再进行中为止。结束的可能性是成功或者失败
    rsp = VideoSynthesis.wait(task=rsp, api_key=get_api_key())
    print(rsp)
    if rsp.status_code == HTTPStatus.OK:
        print(rsp.output.video_url)
        return rsp.output.video_url
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))
        return None


def get_video(video_url, filename):
    path = OUTPUT_DIR
    print(path)
    try:
        resp = requests.get(video_url, timeout=30)
        resp.raise_for_status()
        # data = resp.json()# 如果返回的是json格式，要这么处理。现在返回的是链接对应的数据
        with open(path/filename, 'wb') as f:
            # 一次性写入完成，占内存较大
            # f.write(resp.content)
            # 分次写入，流式输出。占内存较小
            for chunk in resp.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)
        print('下载成功！')
    except requests.exceptions.RequestException as e:
        print(f'下载失败！抛出{e}异常')


def get_name_by_time():
    now_time = time.strftime('%Y%m%d_%H%M%S')
    print(now_time)
    return now_time+'.mp4'
    # datatime.

def get_name_by_url(url:str = None):
    try:
        print(url[url.rfind('/')+1:])
        filename = url[url.rfind('/')+1:].split('?')[0]
        return filename
    except Exception as e:
        print('解析文件名失败！')
        return None

def text_to_video_by_async():
    # 以下代码没用
    # 读取本地文件并编码
    # base64_str = base64_encode_by_name()
    # uri = f'data:audio/wav;base64,{base64_str}'
    # audio_url = 'https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250923/hbiayh/%E4%BB%8E%E5%86%9B%E8%A1%8C.mp3'
    # 视频生成参数配置,本质是字典
    CONFIG = {
        "model": "wan2.7-t2v",  # 视频生成模型
        "resolution": "720P",  # 分辨率：720p, 1080p
        "duration": 5,  # 视频时长（秒）
        "fps": 24,  # 帧率
        "api_key": get_api_key(),
        "prompt": prompt1,
        "audio_url": '',
        "ratio": '16:9',
        "negative_prompt": "",
        "prompt_extend": True,
        "watermark": False,
        "seed": 12345
    }

    url = sample_async_call_t2v(CONFIG)
    # get_video(url, get_name_by_url(url))
    get_video(url, get_name_by_time())


if __name__ == '__main__':
    text_to_video_by_async()