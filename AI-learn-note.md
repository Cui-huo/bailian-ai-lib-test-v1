# AI 学习笔记 —— 阿里百炼 & Python 项目实战

记录我在开发 `bailian-ai-lib` 项目（语音合成、图像生成、视频理解等）过程中踩过的坑和最终的解决方案。

---

### 1. 打包成 exe 后闪退 / 提示 ModuleNotFoundError
**问题**：`pyinstaller -F main.py` 生成的 exe 双击闪退，命令行运行提示 `ModuleNotFoundError: No module named 'xxx'`。  
**根因**：PyInstaller 未能自动检测到自定义模块或隐式依赖。  
**解决**：
- 使用 `--hidden-import` 强制包含所有自定义模块。
- 添加 `--paths .` 确保当前目录在搜索路径中。
- 若仍有缺失，可用 `--collect-all 模块名` 收集全部子模块。

---

### 2. 打包后程序启动时卡在“请输入文件名”而非显示菜单
**问题**：打包成 exe 后一启动就提示输入文件名，而不是显示主菜单，且输入后报错找不到文件。  
**根因**：某个被导入的模块在**顶层代码**中直接执行了 `input()` 或类似的交互逻辑（如 `base64_encode_by_name` 函数在模块顶层直接被调用）。Python 导入该模块时就会执行这些代码。  
**解决**：
- 将所有交互式输入（`input()`）封装到函数内部，只在菜单触发时调用，不要放在模块顶层。
- 检查 `core\utils.py` 及各功能脚本，确保没有在 `if __name__ == "__main__":` 之外执行 `input()`。

---

### 3. 开发时路径正常，打包后找不到文件/下载的内容消失
**问题**：在 PyCharm 中运行正常，打包成 exe 后程序找不到 `assets` 文件夹或下载的文件不知去向。  
**根因**：开发时用 `Path(__file__).parent` 定位根目录，打包后 `__file__` 指向临时解压目录（`_MEIxxxx`），程序关闭后该目录被删除。  
**解决**：
- 使用 `sys.executable` 判断是否为打包环境，并以其所在目录作为基准路径。
- 封装路径函数（如 `get_output_dir`），自动适配开发/打包环境。

---

### 4. 语音合成接口报错 `apikey is required!`
**问题**：调用 `SpeechSynthesizer` 时提示 `InputRequired: apikey is required!`，但在其他地方 API Key 有效。  
**根因**：`SpeechSynthesizer` 内部依赖 `dashscope.api_key` 全局变量，我们只通过 `get_api_key()` 获取了字符串但没有赋值给 `dashscope.api_key`。  
**解决**：
- 在脚本开头或调用前执行：`dashscope.api_key = get_api_key()`

---

### 5. 使用 `cosyvoice-v3.5-plus` 合成语音时返回 `InvalidParameter: url error`
**问题**：用 `MultiModalConversation.call` 调用 cosyvoice-v3.5-plus 报 URL 错误。  
**根因**：cosyvoice-v3.5-plus 模型**必须使用 `SpeechSynthesizer`**，而不是 `MultiModalConversation`（后者用于 qwen-tts 等模型）。  
**解决**：
- 改用 `SpeechSynthesizer(model="cosyvoice-v3.5-plus", voice=voice_id)` 进行合成。
- 参考官方文档或示例，使用正确的 API 接口。

---

### 6. 音频翻译输出文件无法播放（只有咝咝声或极小）
**问题**：`qwen3-livetranslate-flash` 流式返回的音频保存后无法播放。  
**根因**：该模型返回的是**原始 PCM 数据**，不含 WAV 文件头，需要手动写入文件头。  
**解决**：
- 使用 Python 标准库 `wave` 为 PCM 数据添加 WAV 文件头（设置声道数、采样位深、采样率），然后再写入文件。
- 或者保存为 `.pcm` 后缀，再用 Audacity 等工具导入。

---

### 7. PyCharm 中导入 `send_email` 等模块报红线（Cannot find reference）
**问题**：`from send_email import send_email` 提示找不到引用，但代码能正常运行。  
**根因**：项目根目录存在同名 `send_email.py` 文件，导致 Python 模块搜索路径冲突。PyInstaller 也因同样的原因打包错误模块。  
**解决**：
- 删除多余的 `send_email.py` 文件（或将其移出项目目录）。
- 恢复简明导入语句：`from send_email import send_email`。

---

### 8. 免费额度耗尽（403 FreeTierQuotaExhausted）
**问题**：调用模型时返回 `Your free tier quota has been exhausted.`  
**根因**：该模型的免费调用次数已用完。**同一系列**下的不同版本（如 `qwen3-coder-plus` 与 `qwen3-coder-plus-0722`）共享额度。  
**解决**：
- 切换到不同系列的模型（如从 `qwen3-coder-plus` 切换到 `qwen-plus` 或 `glm-5`）。
- 在百炼控制台关闭“免费额度用完即停”开关（将产生费用）。

---

### 9. Settings.json 中配置模型后 /model 列表不更新
**问题**：在 `.qwen/settings.json` 中添加了新模型，但在 Qwen Code 中输入 `/model` 看不到。  
**根因**：Qwen Code 不会自动刷新配置文件，或配置中缺少必要字段。  
**解决**：
- 完全退出 Qwen Code，重新启动。
- 检查 settings.json 中每个模型条目是否正确，尤其是 `envKey` 与 `env` 中的键名对应。
- 必要时执行 `qwen /reset-settings` 强制刷新。

---

### 10. Base64 图片数据 URI 中写错 MIME 类型
**问题**：用 `f"data:image/jpg;base64,..."` 请求视觉模型时报错或图片无法识别。  
**根因**：标准 MIME 类型应为 `image/jpeg`，而非 `image/jpg`。  
**解决**：
- 使用正确的格式：`f"data:image/jpeg;base64,{base64_str}"` （JPEG 图片）。
- 建议根据实际图片格式动态生成 MIME 类型。

---

### 11. `input_language_control` 函数中验证目标语言时错误判断了 `source_lang`
**问题**：用户输入目标语言后，出现 “输入有误，请重新输入！”的死循环。  
**根因**：while 循环中错误地判断了 `source_lang` 而不是 `target_lang`。  
**解决**：
- 仔细检查函数逻辑，将验证条件中的变量名修正。

---

### 12. 重命名函数后其他文件中的导入未同步修改
**问题**：在 PyCharm 中修改了一个函数名，但其他脚本中的 `import` 语句没有自动更新。  
**解决**：
- 使用 PyCharm 的重构功能：将光标放在函数名上，按 `Shift+F6`，输入新名字后回车，PyCharm 会扫描整个项目并修改所有引用。
- 若快捷键无效，右键 → Refactor → Rename。

---

*笔记持续更新中，每解决一个新问题就补充一条，方便以后回顾。*