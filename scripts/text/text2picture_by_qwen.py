"""
text2picture_by_qwen - 
可用。用千问文生图，同步调用。
Author:仗剑天涯
Date:2026/4/24
"""
import json
import os
import dashscope
from dashscope import MultiModalConversation

from config.settings import get_api_key, get_output_dir
from core.utils import get_file_path_by_time, get_file_by_url


def get_url_by_text():
    # 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
    dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
    text = "冬日北京的都市街景，青灰瓦顶、朱红色外墙的两间相邻中式商铺比肩而立，檐下悬挂印有剪纸马的暖光灯笼，在阴天漫射光中投下柔和光晕，映照湿润鹅卵石路面泛起细腻反光。左侧为书法店：靛蓝色老旧的牌匾上以遒劲行书刻着“文字渲染”。店门口的玻璃上挂着一幅字，自上而下，用田英章硬笔写着“专业幻灯片 中英文海报 高级信息图”，落款印章为“1k token”朱砂印。店内的墙上，可以模糊的辨认有三幅竖排的书法作品，第一幅写着着“阿里巴巴”，第二幅写着“通义千问”，第三福写着“图像生成”。一位白发苍苍的老人背对着镜头观赏。右侧为花店，牌匾上以鲜花做成文字“真实质感”；店内多层花架陈列红玫瑰、粉洋牡丹和绿植，门上贴了一个圆形花边标识，标识上写着“2k resolution”，门口摆放了一个彩色霓虹灯，上面写着“细腻刻画 人物 自然 建筑”。两家店中间堆放了一个雪人，举了一老式小黑板，上面用粉笔字写着“Qwen-Image-2.0 正式发布”。街道左侧，年轻情侣依偎在一起，女孩是瘦脸，身穿米白色羊绒大衣，肉色光腿神器。女孩举着心形透明气球，气球印有白色的字：“生图编辑二合一”。里面有一个毛茸茸的卡皮巴拉玩偶。男孩身着剪裁合体的深灰色呢子外套，内搭浅色高领毛衣。街道右侧，一个后背上写着“更小模型，更快速度”的骑手疾驰而过。整条街光影交织、动静相宜。"
    text = input('请输入图片描述文本：').strip() or text
    messages = [
        {
            "role": "user",
            "content": [
                {"text": text}
            ]
        }
    ]

    # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key = get_api_key()

    response = MultiModalConversation.call(
        api_key=api_key,
        model="qwen-image-2.0-pro",
        messages=messages,
        result_format='message',
        stream=False,
        watermark=False,
        prompt_extend=True,
        negative_prompt="低分辨率，低画质",
        size='2048*2048'
    )

    if response.status_code == 200:
        print(json.dumps(response, ensure_ascii=False))
        content = response.output.choices[0].message.content[0]
        url = content.get('image', '')
        if not url:
            print('图片链接获取失败！')
            return None
        else:
            return url
    else:
        print(f"HTTP返回码：{response.status_code}")
        print(f"错误码：{response.code}")
        print(f"错误信息：{response.message}")
        print("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code")


def get_picture():
    url = get_url_by_text()
    # 该大模型默认都是png格式图片
    get_file_by_url(url, 'png')

if __name__ == '__main__':
    get_picture()
