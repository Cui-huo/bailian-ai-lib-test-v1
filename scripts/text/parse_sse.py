"""
parse_sse -
本脚本实现：
把大模型返回的base64编码过的音频数据（流式输出给请求方），
重新本地base64解码成2进制，然后写入音频文件中
sse文件是通过cul命令获取的。

**cmd->curl命令获取非流式输出数据时，大模型一次性返回json数据（含可下载的URL链接）
**解析SSE流式响应文件，提取Base64音频数据并保存为WAV文件。
**获取的音频数据来自cmd->curl命令获取.
获取方式：流式输出   使用模型：千问cosyvoice-v3-flash
cmd设置环境变量：set DASHSCOPE_API_KEY=sk-***
查看环境变量是否成功：echo %DASHSCOPE_API_KEY%
{获取命令代码：curl.exe -o my_voice.wav -X POST https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer ^
More? -H "Authorization: Bearer %DASHSCOPE_API_KEY%" ^
More? -H "Content-Type: application/json" ^
More? -H "X-DashScope-SSE: enable" ^
More? -d "{\"model\": \"cosyvoice-v3-flash\", \"input\": {\"text\": \"我家的后面有一个很大的园子。\", \"voice\": \"longanyang\", \"format\": \"wav\", \"sample_rate\": 24000}}"
}**
Author:仗剑天涯
Date:2026/4/21
"""
import base64
import json
from pathlib import Path

from config.settings import get_input_dir, get_output_dir
from core.utils import get_file_path_by_time, get_timestamp_by_time
def parse_sse_to_wav():
    """
    解析SSE流式响应文件，提取Base64音频数据并保存为WAV文件。
    """
    audio_bytes = bytearray()
    block_count = 0
    # 输入文件名，读取文件
    print('示例sse文件：my_voice.wav')
    input_path = get_input_dir()
    # project_root = Path(__file__).parent.parent.parent.resolve()
    # assert_dir = project_root / 'assets'

    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 只处理以 "data:" 开头的行
            if not line.startswith('data:'):
                continue

            # 提取JSON部分
            json_str = line[5:].strip()
            if not json_str:
                continue

            try:
                data = json.loads(json_str)
                # 检查是否包含音频数据
                audio_info = data.get('output', {}).get('audio', {})
                b64_data = audio_info.get('data', '')

                if b64_data:
                    # Base64解码并添加到音频数据
                    audio_chunk = base64.b64decode(b64_data)
                    audio_bytes.extend(audio_chunk)
                    block_count += 1
                    print(f"  ✅ 已处理第 {block_count} 个音频块，大小: {len(audio_chunk)} 字节")

            except json.JSONDecodeError as e:
                print(f"  ⚠️ 跳过无效的JSON行: {e}")
                continue

    if audio_bytes:
        # 获取时间戳
        timestemp = get_timestamp_by_time()
        # 拼接路径和文件名，写入文件
        print(f'{get_output_dir()}/{timestemp}.wav')
        with open(f'{get_output_dir()}/{timestemp}.wav', 'wb') as f:
            f.write(audio_bytes)
        print(f"🎉 成功！已保存 {len(audio_bytes)} 字节的WAV文件至: {timestemp}.wav")
        print("💡 提示：现在可以直接用播放器打开这个文件了。")
    else:
        print("❌ 错误：未在文件中找到任何音频数据。")


if __name__ == "__main__":
    # 'assets'文件夹里有个my_voice.wav，实际是大模型返回的sse数据
    parse_sse_to_wav()