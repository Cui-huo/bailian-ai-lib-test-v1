"""
excel_to_dict.py - 从WPS/Excel表格中提取指定列生成字典
这种简单的小工具脚本，AI可以直接生成，实用性非常强！
功能：读取表格文件，取第2列（Voice ID）为键，第3列（类型/描述）为值，输出字典。
使用前请安装依赖：pip install openpyxl
使用方法：
将你的 WPS 表格文件（比如 voices.xlsx）和脚本放在同一目录。
在终端中运行：python excel_to_dict.py，然后输入表格文件路径（或直接将文件拖拽到终端窗口）。
脚本会立即打印出形如 {'longcheng_v2': '阳光男声-1', 'longhua_v2': '活泼女童-1', ...} 的字典。
"""

import sys
from pathlib import Path
import openpyxl

def excel_to_dict(file_path: str, key_col: int = 2, value_col: int = 3) -> dict:
    """
    读取Excel表格，将指定列配对为字典。

    Args:
        file_path: Excel文件路径（支持相对路径或拖拽文件到脚本窗口）
        key_col: 作为键的列序号（从1开始，默认第2列）
        value_col: 作为值的列序号（默认第3列）

    Returns:
        dict: 键值对组成的字典
    """
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active  # 默认取第一个工作表

    result = {}
    # 从第2行开始，跳过表头（假设第1行是标题）
    for row in ws.iter_rows(min_row=2, values_only=True):
        key = row[key_col - 1]  # 转换到0-based索引
        value = row[value_col - 1]
        if key and value:  # 跳过空行
            result[str(key).strip()] = str(value).strip()
    wb.close()
    return result

def main():
    # 支持拖拽文件或输入路径
    if len(sys.argv) > 1:
        file_path = sys.argv[1]  # 拖拽文件到脚本上
    else:
        file_path = input("请输入Excel文件路径（或拖拽文件到此处）: ").strip().strip('"')

    if not Path(file_path).exists():
        print(f"❌ 文件不存在: {file_path}")
        return

    try:
        data = excel_to_dict(file_path)
        print("\n✅ 提取结果：")
        print(data)  # 直接输出字典
        # 如果需要保存为JSON文件：
        # import json
        # with open("output.json", "w", encoding="utf-8") as f:
        #     json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ 读取失败: {e}")

if __name__ == "__main__":
    main()