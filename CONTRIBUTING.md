# 贡献指南

感谢你对本项目的关注！欢迎通过 Issue 和 Pull Request 的方式参与贡献。

## 📋 目录

- [行为准则](#行为准则)
- [开发环境设置](#开发环境设置)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)
- [问题反馈](#问题反馈)

## 行为准则

- 保持友好和尊重的沟通态度
- 对事不对人，专注于技术讨论
- 欢迎不同背景和能力水平的贡献者

## 开发环境设置

### 1. Fork 项目

点击 GitHub 页面右上角的 **Fork** 按钮，将项目复制到你自己的账户下。

### 2. 克隆到本地

```bash
git clone https://github.com/<your-username>/bailian-ai-lib-test-v1.git
cd bailian-ai-lib-test-v1
```

### 3. 创建虚拟环境

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置上游仓库（可选）

```bash
git remote add upstream https://github.com/<original-owner>/bailian-ai-lib-test-v1.git
```

## 提交规范

### Branch 命名

- `feature/xxx` - 新功能
- `fix/xxx` - Bug 修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 代码重构
- `test/xxx` - 测试相关

### Commit Message 格式

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档变更
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具链相关

**示例：**
```
feat(audio): 新增 SSE 音频解析功能

- 添加 parse_sse.py 模块
- 支持 Base64 流式数据解码为 WAV

Closes #12
```

## Pull Request 流程

### 1. 创建分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 进行修改

- 保持代码风格与现有代码一致
- 添加必要的注释
- 确保新功能有适当的错误处理

### 3. 测试验证

确保你的修改在本地可以正常运行：

```bash
python main.py
```

### 4. 提交更改

```bash
git add .
git commit -m "feat: 描述你的改动"
```

### 5. 同步上游代码（如有必要）

```bash
git fetch upstream
git rebase upstream/main
```

### 6. 推送分支

```bash
git push origin feature/your-feature-name
```

### 7. 创建 Pull Request

1. 访问你的 Fork 仓库
2. 点击 **Compare & pull request**
3. 填写 PR 描述：
   - 简要说明改动目的
   - 列出主要变更
   - 关联相关 Issue（如适用）

## 问题反馈

### 提交 Issue

在创建 Issue 前，请先搜索是否已有类似问题。

**Bug 报告模板：**
```markdown
### 问题描述
简要描述遇到的问题

### 复现步骤
1. 执行操作...
2. 出现错误...

### 预期行为
应该发生什么

### 实际行为
实际发生了什么

### 环境信息
- Python 版本：
- 操作系统：
- 相关依赖版本：

### 日志/截图
如有错误日志或截图，请附上
```

**功能建议模板：**
```markdown
### 功能描述
简要描述你希望添加的功能

### 使用场景
为什么需要这个功能？解决什么问题？

### 实现建议
如果有想法，可以描述你期望的实现方式

### 其他信息
任何相关的补充说明
```

## 代码风格

- 遵循 PEP 8 编码规范
- 使用 4 个空格缩进
- 函数和变量使用小写 + 下划线命名
- 类名使用大驼峰命名
- 重要函数需包含文档字符串

## 许可证

通过向本项目提交代码，你同意你的贡献采用与项目相同的 MIT 许可证。

---

再次感谢你的贡献！🎉
