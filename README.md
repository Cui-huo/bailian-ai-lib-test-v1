# 🚀 AI 工具箱

基于阿里云百炼平台（DashScope）的 AI 能力集成工具，菜单式交互界面，提供语音合成、声音复刻、图像理解、视频分析、文生图/视频等多种功能。

## ✨ 功能特性

### 🎵 音频功能
- **文字转语音** - 支持 CosyVoice-v2 模型，20+ 种预设音色（温柔姐姐、新闻男声、童声等）
- **语音翻译** - 支持上传 URL 或本地音频文件，自动翻译并输出
- **声音复刻** - 通过 URL 或本地音频文件复刻音色
- **声音设计** - 通过文字描述生成专属音色并合成
- **SSE 音频解析** - 将 Base64 流式数据解码为 WAV 文件

### 🖼️ 图像功能
- **图片理解** - 上传图片，AI 分析并回答相关问题
- **OCR 文字提取** - 从图片中提取文字（如车票、文档等）
- **拍照答题** - 上传题目图片，AI 提供解答

### 🎬 视频功能
- **视频理解** - 支持本地视频或在线 URL，AI 分析视频内容
- **视频理解（图片列表）** - 通过多张图片生成视频理解
- **视频续写** - 根据图 + 视频生成中间画面（需充足 Token）

### 🎨 生成功能
- **文生图（千问）** - 使用 qwen-image-2.0-pro 模型同步生成
- **文生图（万相）** - 使用 wan2.7-image-pro 模型异步生成
- **文生视频** - 使用 wan2.7-t2v 模型异步生成视频

### 💬 对话功能
- **纯文本对话** - 基于 DeepSeek-v3.2 的多轮对话
- **多模态对话** - 支持文本 + 音频回复的交互式聊天

## 📦 安装与使用

### 环境要求
- Python 3.8+
- Windows / Linux / macOS

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd bailian-ai-lib-test-v1
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置 API 密钥

在项目根目录创建 `.env` 文件，填入你的阿里云 DashScope API Key：

```env
DASHSCOPE_API_KEY=sk-your-api-key-here
```

> **获取 API Key**: [阿里云百炼控制台](https://help.aliyun.com/zh/model-studio/get-api-key)

### 5. 运行程序

#### 方式一：直接运行源码

```bash
python main.py
```

#### 方式二：打包为可执行文件

```bash
# 使用 PyInstaller 打包
pyinstaller main.spec

# 生成的可执行文件位于 dist/ 目录
./dist/main.exe  # Windows
./dist/main      # Linux/macOS
```

## 📁 项目结构

```
bailian-ai-lib-test-v1/
├── main.py                 # 主入口（命令行菜单）
├── requirements.txt        # Python 依赖
├── main.spec              # PyInstaller 打包配置
├── .env                   # 环境变量（API Key，需自行创建）
├── config/
│   └── settings.py        # 统一配置管理
├── core/
│   └── utils.py           # 通用工具函数
├── scripts/
│   ├── audio/             # 音频处理模块
│   ├── image/             # 图像处理模块
│   ├── video/             # 视频处理模块
│   ├── text/              # 文本处理模块
│   └── multimodal/        # 多模态功能模块
├── assets/                # 资源文件（测试图片/音频/视频）
└── output/                # 输出文件目录
```

## 🎯 使用示例

### 文字转语音

```bash
# 运行后选择：1 -> 选择音色 -> 输入文字 -> 生成 MP3
```

### 图片理解

```bash
# 将图片放入 assets/ 目录
# 运行后选择：2 -> 1 -> 输入图片名 -> 输入问题
```

### 文生图

```bash
# 运行后选择：4 -> 1/2 -> 输入描述文字 -> 等待生成
```

## ⚠️ 注意事项

1. **API 费用**：本工具调用阿里云百炼平台 API，会产生相应费用，请留意 Token 消耗
2. **网络要求**：需要稳定的网络连接以访问 DashScope 服务
3. **文件路径**：输入文件默认从 `assets/` 目录读取，输出文件保存在 `output/` 目录
4. **打包后运行**：打包成 exe 后，确保 `.env` 文件和资源文件在 exe 同目录下

## 🛠️ 技术栈

- **Python 3.x**
- **DashScope SDK** - 阿里云百炼平台官方 SDK
- **PyInstaller** - Python 打包工具
- **Flask** - Web 框架（部分功能使用）
- **OpenAI SDK** - 兼容接口调用

## 💡 常见问题

### 打包后闪退或找不到模块
```bash
# 使用 hidden-import 强制包含自定义模块
pyinstaller --hidden-import scripts.audio.xxx main.py
```

### API Key 配置问题
确保在 `.env` 文件中正确设置 `DASHSCOPE_API_KEY`，并在代码中赋值给 `dashscope.api_key`

### 免费额度耗尽
如遇到 `403 FreeTierQuotaExhausted`，请切换到其他模型或在百炼控制台调整配额设置

> 更多开发笔记详见 [AI 学习笔记](AI-learn-note.md)

## 📝 更新日志

### v1.0.0 (2026-04-27)
- 初始版本发布
- 支持音频、图像、视频、生成、对话五大类功能
- 提供命令行交互式菜单
- 支持打包为独立可执行文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！详见 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👤 作者

**仗剑天涯**

Date: 2026/04/27

## 🔗 相关链接

- [阿里云百炼平台文档](https://help.aliyun.com/zh/model-studio/)
- [DashScope SDK 文档](https://dashscope.aliyun.com/)
- [模型列表](https://help.aliyun.com/zh/model-studio/models)

---

<div align="center">

如果这个项目对你有帮助，请给一个 ⭐ Star 支持！

</div>
