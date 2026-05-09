"""
image2video - 
实现“视频续写”：   万相2.7-i2v”模型
（Video Continuation）的功能：根据一段视频和一张尾帧图片，
让AI生成、补充中间缺失的动态画面。
Author:仗剑天涯
Date:2026/4/24
"""
# -*- coding: utf-8 -*-
from dashscope import VideoSynthesis
import dashscope
import os
from http import HTTPStatus
import requests
from config.settings import get_api_key
from core.utils import get_file_path_by_time

dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
api_key = get_api_key()
model = "wan2.7-i2v"

def sample_sync_call():
    video_url = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20260414/cqcbkw/wan2.7-i2v-video-continuation.mp4"
    picture_url = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20260414/mrwahg/wan2.7-i2v-video-continuation.webp"
    prompt = "男人低头向下看到地上的木箱，他弯下腰，小心翼翼打开箱盖，他紧盯着箱内的东西，嘴唇颤抖的微微张开，皱着眉头，眼睛微微张大，露出惊恐的表情。"
    print('🎬 视频续写任务启动...')
    video_url = input('📹 请输入视频url（回车使用默认值）: ').strip() or video_url
    picture_url = input('🖼️ 请输入尾帧图片url（回车使用默认值）: ').strip() or picture_url
    prompt = input('📝 请输入提示词（回车使用默认值）: ').strip() or prompt
    media = [
        {"type": "first_clip", "url": video_url},
        {"type": "last_frame", "url": picture_url}
    ]

    # 1. 提交异步任务
    print("📤 正在提交任务...")
    rsp = VideoSynthesis.async_call(
        api_key=api_key,
        model=model,
        media=media,
        resolution="720P",
        duration=12,
        watermark=True,
        prompt=prompt,
    )

    if rsp.status_code != HTTPStatus.OK:
        print(f"❌ 任务提交失败: {rsp.code} - {rsp.message}")
        return

    task_id = rsp.output.task_id
    print(f"✅ 任务已提交，ID: {task_id}")

    # 2. 等待任务完成
    print("⏳ 正在等待任务完成（通常需要1-2分钟）...")
    rsp = VideoSynthesis.wait(task=rsp, api_key=api_key)

    if rsp.status_code != HTTPStatus.OK:
        print(f"❌ 任务失败: {rsp.code} - {rsp.message}")
        return

    # 3. 安全地提取视频链接
    final_video_url = rsp.output.get('video_url') or getattr(rsp.output, 'video_url', None)
    if not final_video_url:
        print(f"❌ 任务状态异常:{rsp.output.get('task_status', '')}。完整响应: {rsp}")
        return

    print(f"🎥 获取到视频链接: {final_video_url}")

    # 4. 下载视频
    print("📥 正在下载视频...")
    try:
        resp = requests.get(final_video_url, timeout=30)
        resp.raise_for_status()
        save_path = f'{get_file_path_by_time()}.mp4'
        with open(save_path, 'wb') as f:
            f.write(resp.content)
        print(f"✅ 视频下载成功！已保存至: {save_path}")
    except Exception as e:
        print(f"❌ 下载失败: {e}")

if __name__ == '__main__':
    sample_sync_call()