"""
parse_sse -
本脚本实现：
把大模型返回的base64编码过的音频数据（流式输出给请求方），
重新本地base64解码成2进制，然后写入音频文件中

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


def get_wav_from_sse_v1(sse_file_path: str, output_wav_path: str):
    """
    解析SSE流式响应文件，提取Base64音频数据并保存为WAV文件。

    Args:
        sse_file_path: curl生成的原始SSE文件路径
        output_wav_path: 期望输出的WAV文件路径
    """
    # 确保输出目录存在
    output_file = Path(output_wav_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"🔍 正在解析SSE文件: {sse_file_path}")
    audio_bytes = bytearray()
    block_count = 0
    # 读取文件
    project_root = Path(__file__).parent.parent.parent.resolve()
    assert_dir = project_root / 'assets'
    with open(assert_dir / sse_file_path, 'r', encoding='utf-8') as f:
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
        # 写入最终的WAV文件
        with open(assert_dir / output_wav_path, 'wb') as f:
            f.write(audio_bytes)
        print(f"🎉 成功！已保存 {len(audio_bytes)} 字节的WAV文件至: {output_wav_path}")
        print("💡 提示：现在可以直接用播放器打开这个文件了。")
    else:
        print("❌ 错误：未在文件中找到任何音频数据。")


def get_wav_from_sse():
    # 请将这里的文件名替换成你实际生成的那个超长文本文件
    input_file = "my_voice.wav"
    output_file = "my_voice_output.wav"
    get_wav_from_sse_v1(input_file, output_file)