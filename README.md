# 🖥️ Screen Capture MCP Server

> **让 AI 长上眼睛，看见你屏幕上的一切**

一个开源的 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 服务器，为 AI Agent 提供**跨平台截图和录屏能力**，支持 Windows、macOS 和 Linux。

> *想象一下：对 AI 说"帮我看看这个按钮是不是歪了"，然后 AI 直接截图分析——这就是这座桥梁做的事。*

[![MCP Server](https://img.shields.io/badge/Protocol-MCP-blue?style=flat-square)](https://modelcontextprotocol.io/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green?style=flat-square)](https://www.python.org/)
[![ffmpeg](https://img.shields.io/badge/Backend-ffmpeg-orange?style=flat-square)](https://ffmpeg.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](./LICENSE)
[![Platform: Win/macOS/Linux](https://img.shields.io/badge/Platform-Win%2FmacOS%2FLinux-lightgrey?style=flat-square)](#-支持的平台)

---

## 🤔 痛点：AI 是个"盲人"

现在的 AI 编程助手代码写得溜，但**看不见**你的屏幕。

现有方案都很拧巴：

| 方案 | 问题 |
|---|---|
| 手动截图 → 粘贴到对话 | 工作流直接断掉，毫无丝滑可言 |
| pyautogui / pyside 截图 | 只能跑脚本、平台锁定、配置复杂、没法录视频流 |
| 系统原生截屏 API | AI 根本调不了 |
| 每个 AI 工具单独对接 | 换工具就得重来一遍 |

**Screen Capture MCP Server** 解决这些痛点：

- ✅ 实现了**标准 MCP 协议** — 任何兼容 MCP 的客户端都能用（Claude Desktop、Cursor、Windsurf、Goose、Open Interpreter…）
- ✅ 同时支持**截图和录屏**，作为结构化工具暴露给 AI
- ✅ **零配置依赖** — 自动检测并提示安装缺少的组件
- ✅ **Windows、macOS、Linux 全平台支持**，同一套接口

---

## ⚡ 快速上手

### 1. 安装 ffmpeg（唯一的外部依赖）

```bash
# macOS
brew install ffmpeg

# Windows（用 winget）
winget install ffmpeg

# Linux（Ubuntu/Debian）
sudo apt install ffmpeg

# Linux（CentOS/RHEL）
sudo yum install ffmpeg
```

> **小贴士：** 运行 `ffmpeg -version` 验证是否安装成功。已经装好了？直接跳到下一步。

### 2. 配置到你的 MCP 客户端

#### Claude Desktop

编辑 `claude_desktop_config.json`：
- **macOS**: `~/Library/Application Support/Claude/`
- **Windows**: `%APPDATA%\Claude\`
- **Linux**: `~/.config/Claude/`

```json
{
  "mcpServers": {
    "screen-capture": {
      "command": "python",
      "args": ["/absolute/path/to/screen-capture-mcp/server.py"]
    }
  }
}
```

#### Cursor / Windsurf / Goose

编辑 `mcp.json`：
- **macOS/Linux**: `~/.cursor/mcp.json`、`~/.windsurf/mcp.json` 等
- **Windows**: `%APPDATA%\Cursor\mcp.json`

```json
{
  "mcpServers": {
    "screen-capture": {
      "command": "python",
      "args": ["/absolute/path/to/screen-capture-mcp/server.py"]
    }
  }
}
```

### 3. 重启你的 AI 客户端

服务器会自动启动。AI 现在可以"看见"你的屏幕了。

---

## 🛠️ 可用工具

| 工具 | 功能 |
|---|---|
| `take_screenshot` | 截取当前屏幕 → 返回图片文件路径 |
| `start_recording` | 开始录屏 → 返回输出文件路径 |
| `stop_recording` | 停止录制，返回视频文件 |
| `get_recording_status` | 查看当前是否正在录制 |
| `check_dependencies` | 检查系统和依赖状态 |

---

## 💡 使用场景

### 1. 🤖 AI 辅助 UI 调试
```
你："登录页的按钮好像有点问题，帮我截个图看看？"
AI：→ take_screenshot → "提交按钮的文字被底部裁剪了，padding-bottom 需要加 4px。"
```
AI 可以视觉检查任何界面，给出精确的反馈——不用你来回切换窗口。

### 2. 🎥 自动录制演示视频
```
你："帮我录一个 30 秒的演示，展示我填写表单的过程。"
AI：→ start_recording → [你操作] → stop_recording → "这是你的演示.mp4"
```
AI 编排录制流程，你只管专注操作。

### 3. 🧪 可视化回归测试
```
你："帮我截一张改 CSS 前的图，再截一张改后的，对比一下。"
AI：→ take_screenshot → [你修改样式] → take_screenshot → 分析差异
```
自动捕捉意外的样式副作用。

### 4. 👀 远程屏幕查看
```
你："我的第二块显示器现在显示什么？"
AI：→ take_screenshot → "你的第二块显示器正在运行 pytest——3 个测试通过，1 个在 test_auth.py 失败"
```
AI 可以汇报任何屏幕的状态，方便远程协助场景。

### 5. 🖱️ AI + 视觉验证的流程自动化
```
你："点击那个'导出'按钮，等弹窗出来，截个图给我看。"
AI：→ (执行步骤) → take_screenshot → "弹窗显示了'No data to export'的警告"
```
配合 computer-use Agent，实现带视觉确认的闭环自动化。

---

## 🔌 支持的平台

| 平台 | 状态 | 后端 |
|---|---|---|
| 🪟 Windows | ✅ 稳定 | `ffmpeg -f gdigrab` |
| 🍎 macOS | ✅ 稳定 | `ffmpeg -f avfoundation` |
| 🐧 Linux | ✅ 稳定 | `ffmpeg -f x11grab` |

> **注意：** Linux 也支持 Wayland（通过 `wf-recorder`，可选），或使用 X11 的 `x11grab`。

---

## 📋 环境要求

| 依赖 | 版本 | 说明 |
|---|---|---|
| Python | ≥ 3.10 | 已测试 3.10、3.11、3.12 |
| ffmpeg | 任意新版 | 自动在 PATH 中查找 |
| mcp | ≥ 1.0.0 | `pip install mcp>=1.0.0` |
| MCP 客户端 | 任意 | Claude Desktop、Cursor 等 |

---

## 🔐 安全性

本服务器实现了多重安全措施防止滥用：

| 功能 | 限制 | 说明 |
|---|---|---|
| **路径限制** | 仅安全目录 | 所有文件保存到 `{TEMP}/screen-capture/` |
| **录制时长** | 最长 5 分钟 | 防止持续监控 |
| **截图频率** | 至少 3 秒间隔 | 防止高频监控 |
| **操作审计日志** | 100 条记录 | 所有操作带时间戳记录 |

### 为什么有这些限制？

屏幕录制工具可能被滥用：
- 🔴 **未授权监控** — 未经同意持续录屏
- 🔴 **数据泄露** — 捕获敏感信息到外部路径
- 🟡 **隐私侵犯** — 高频截图实现近乎实时的监控

这些限制同时保护用户和系统。

---

## 🔧 依赖安装

1. **安装 ffmpeg**（如果缺失，服务器会打印安装说明并退出）
2. **安装 mcp Python 包**：
```bash
pip install mcp>=1.0.0
```

服务器启动时会检查依赖，缺失时会给出清晰的提示。

---

## 📊 方案对比：为什么不选别的？

### 为什么不选 `pyautogui` 或 `mss`？
这些库抓取原始像素缓冲——跑脚本还行，做视频流根本不行。而且它们不暴露协议接口，给 AI 对接需要为每个工具单独写代码。

### 为什么不选系统原生 API（macOS ScreenCaptureKit、Windows Graphics Capture）？
- 平台专属——需要写三套实现
- 需要复杂的原生绑定
- 不支持任何 AI 友好的协议

### 为什么选 MCP？
MCP 是**新兴的标准**，用来连接 AI 助手和外部工具。只要这个服务器存在，**所有 MCP 兼容的客户端都能用**——无需为每个客户端单独对接。一套实现，到处运行。

---

## 🗺️ 未来规划

计划增加的功能：

- [ ] **`get_screen_info`** — 列出可用屏幕/显示器及尺寸
- [ ] **`select_region`** — 录制/截取指定屏幕区域（x, y, w, h）
- [ ] **音频捕获** — 录制时包含系统声音（平台相关）
- [ ] **多显示器选择** — 选择要捕获的显示器
- [ ] **Animated GIF 输出** — 轻量级替代 MP4，用于快速演示
- [ ] **WebSocket 传输** — 支持远程/无头服务器模式
- [ ] **`compare_screenshots`** — 内置视觉 diff 工具
- [ ] **OBS Studio 插件模式** — 利用 OBS 作为高级用户的捕获后端

---

## 🤝 贡献指南

欢迎贡献！参与方式：

### 开发环境配置

```bash
# 克隆仓库
git clone https://github.com/Alice202312/screen-capture-mcp.git
cd screen-capture-mcp

# 开发模式安装
pip install -e .

# 验证运行
python server.py
```

### 可以贡献什么

- 🐛 **Bug 报告** — 附上操作系统、Python 版本和错误输出
- 💡 **功能建议** — 开 issue 描述你的使用场景
- 🔧 **Pull Request** — 先开 issue 讨论；保持 PR 小而专注
- 📖 **文档** — 翻译、澄清和示例都欢迎

### 代码规范

- Python：遵循 [PEP 8](https://pep8.org/)
- 所有公共函数加文档字符串
- 尽可能使用类型提示

---

## 📜 开源许可

MIT License — 详见 [LICENSE](./LICENSE)。

---

<div align="center">

**用 ❤️ 为 AI Agent 打造**

*如果这个项目帮你省了时间，考虑给它点个 ⭐*

</div>

---

# 🖥️ Screen Capture MCP Server

> **Give Your AI Eyes — Let It See What's on Your Screen**

An open-source [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that equips AI agents with **real-time screen recording and screenshot capabilities** across Windows, macOS, and Linux.

> *If you've ever wanted your AI assistant to "look at this UI and tell me what's broken" — this is the bridge.*

[![MCP Server](https://img.shields.io/badge/Protocol-MCP-blue?style=flat-square)](https://modelcontextprotocol.io/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green?style=flat-square)](https://www.python.org/)
[![ffmpeg](https://img.shields.io/badge/Backend-ffmpeg-orange?style=flat-square)](https://ffmpeg.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](./LICENSE)
[![Platform: Win/macOS/Linux](https://img.shields.io/badge/Platform-Win%2FmacOS%2FLinux-lightgrey?style=flat-square)](#-supported-platforms)

---

## 🤔 Why This?

AI coding assistants are great at writing code — but **blind**. They can't see your UI, your app, or your screen.

Existing workarounds are painful:

| Approach | Problem |
|---|---|
| Manual screenshots → paste into chat | Breaks the AI workflow entirely |
| pyautogui / pyside GRABBERS | Platform-locked, complex setup, can't stream |
| Native OS screen capture | Not accessible to AI agents in real time |
| Custom integrations | Each AI tool needs its own fragile wiring |

**Screen Capture MCP Server** solves this by:
- ✅ Implementing the **standard MCP protocol** — works with **any MCP-compatible client** (Claude Desktop, Cursor, Windsurf, Goose, Open Interpreter…)
- ✅ Providing **both screenshots and video recording** as structured tools
- ✅ **Zero-config dependencies** — auto-checks and installs what it needs
- ✅ Running on **Windows, macOS, and Linux** with the same interface

---

## ⚡ Quick Start

### 1. Install ffmpeg (the only manual requirement)

```bash
# macOS
brew install ffmpeg

# Windows (with winget)
winget install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt install ffmpeg

# Linux (CentOS/RHEL)
sudo yum install ffmpeg
```

> **Tip:** Verify with `ffmpeg -version`. If already installed, you're done.

### 2. Add to your MCP client

#### Claude Desktop

Edit `claude_desktop_config.json`:
- **macOS**: `~/Library/Application Support/Claude/`
- **Windows**: `%APPDATA%\Claude\`
- **Linux**: `~/.config/Claude/`

```json
{
  "mcpServers": {
    "screen-capture": {
      "command": "python",
      "args": ["/absolute/path/to/screen-capture-mcp/server.py"]
    }
  }
}
```

#### Cursor / Windsurf / Goose

Edit `mcp.json`:
- **macOS/Linux**: `~/.cursor/mcp.json`, `~/.windsurf/mcp.json`, etc.
- **Windows**: `%APPDATA%\Cursor\mcp.json`

```json
{
  "mcpServers": {
    "screen-capture": {
      "command": "python",
      "args": ["/absolute/path/to/screen-capture-mcp/server.py"]
    }
  }
}
```

### 3. Restart your client

The server starts automatically. The AI can now see your screen.

---

## 🛠️ Available Tools

| Tool | Description |
|---|---|
| `take_screenshot` | Capture the current screen → returns image file path |
| `start_recording` | Begin screen recording → returns output file path |
| `stop_recording` | Stop recording and return the video file |
| `get_recording_status` | Check if recording is currently active |
| `check_dependencies` | Report system/dependency status |

---

## 💡 Use Cases

### 1. 🤖 AI-Assisted UI Debugging
```
You: "The button on my login page looks off. Can you screenshot it and tell me what's wrong?"
AI: → take_screenshot → "The submit button text is cut off at the bottom edge. The padding-bottom needs +4px."
```
AI can visually inspect any on-screen UI and give precise feedback — without you switching windows.

### 2. 🎥 Automated Demo / Tutorial Recording
```
You: "Record a 30-second demo of me filling out this form in the browser."
AI: → start_recording → [you interact] → stop_recording → "Here's your demo.mp4"
```
AI orchestrates the recording workflow while you focus on the action.

### 3. 🧪 Visual Regression Testing
```
You: "Take a screenshot before and after my CSS changes, then compare them."
AI: → take_screenshot → [you apply changes] → take_screenshot → analyze_diff
```
Catch unintended visual side effects automatically.

### 4. 👀 Remote Screen Inspection
```
You: "What does my second monitor show right now?"
AI: → take_screenshot → "Your second monitor shows a terminal running a pytest session — 3 tests passed, 1 failed in test_auth.py"
```
AI can report on any screen, enabling remote assistance scenarios.

### 5. 🖱️ AI-Powered Process Automation with Visual Verification
```
You: "Click the 'Export' button in the app, wait for the modal, then screenshot it."
AI: → (executes steps) → take_screenshot → "The modal appeared with a 'No data to export' warning"
```
Combine with computer-use agents for closed-loop automation with visual confirmation.

---

## 🔌 Supported Platforms

| Platform | Status | Backend |
|---|---|---|
| 🪟 Windows | ✅ Stable | `ffmpeg -f gdigrab` |
| 🍎 macOS | ✅ Stable | `ffmpeg -f avfoundation` |
| 🐧 Linux | ✅ Stable | `ffmpeg -f x11grab` |

> **Note:** Linux also supports Wayland via `wf-recorder` (optional), or X11 with `x11grab`.

---

## 📋 Requirements

| Requirement | Version | Notes |
|---|---|---|
| Python | ≥ 3.10 | Tested on 3.10, 3.11, 3.12 |
| ffmpeg | Any recent | Auto-detected in PATH |
| mcp | ≥ 1.0.0 | `pip install mcp>=1.0.0` |
| MCP Client | Any | Claude Desktop, Cursor, etc. |

---

## 🔐 Security

This server implements multiple security measures to prevent abuse:

| Feature | Limit | Description |
|---|---|---|
| **Path Restriction** | Safe directory only | All files are saved to `{TEMP}/screen-capture/` |
| **Recording Duration** | 5 minutes max | Prevents continuous surveillance |
| **Screenshot Rate** | 3 seconds min | Prevents high-frequency monitoring |
| **Operation Audit Log** | 100 entries | All operations are logged with timestamps |

### Why These Limits?

Screen capture tools can be abused for:
- 🔴 **Unauthorized surveillance** — continuous screen recording without consent
- 🔴 **Data exfiltration** — capturing sensitive information to external paths
- 🟡 **Privacy violation** — high-frequency screenshots enabling near-real-time monitoring

These limits protect both users and the systems they work with.

---

## 🔧 Dependency Installation

1. **Install ffmpeg** (if missing, server will print install instructions and exit)

2. **Install mcp Python package**:
```bash
pip install mcp>=1.0.0
```

On startup, the server checks for dependencies and prints clear instructions if anything is missing.

---

## 📊 Comparison: Why Not…?

### Why not `pyautogui` or `mss`?
Those libraries grab raw pixel buffers — great for a script, useless for streaming video. They also don't expose a protocol interface, so wiring them to AI agents requires custom code per tool.

### Why not OS-native APIs (macOS ScreenCaptureKit, Windows Graphics Capture)?
- They're platform-specific — you'd need 3 separate implementations
- They require complex native bindings
- They don't speak any AI-friendly protocol

### Why MCP?
MCP is the **emerging standard** for connecting AI assistants to external tools. Once this server exists, it works in **every MCP-compatible client** — no per-client wiring. You write the server once; every AI tool gets the capability.

---

## 🗺️ Roadmap

Planning to add:

- [ ] **`get_screen_info`** — List available screens/displays with dimensions
- [ ] **`select_region`** — Record/screenshot a specific screen area (x, y, w, h)
- [ ] **Audio capture** — Include system audio in recordings (platform-dependent)
- [ ] **Multi-monitor selection** — Choose which display to capture
- [ ] **Animated GIF output** — Lightweight alternative to MP4 for quick demos
- [ ] **WebSocket transport** — Support for remote/headless server mode
- [ ] **`compare_screenshots`** — Built-in visual diff tool
- [ ] **OBS Studio plugin mode** — Leverage OBS as a capture backend for advanced users

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

### Development Setup

```bash
# Clone the repo
git clone https://github.com/Alice202312/screen-capture-mcp.git
cd screen-capture-mcp

# Install in dev mode
pip install -e .

# Verify it works
python server.py
```

### What to Contribute

- 🐛 **Bug reports** — Include OS, Python version, and error output
- 💡 **Feature requests** — Open an issue describing the use case
- 🔧 **PRs** — Please open an issue first to discuss; keep PRs small and focused
- 📖 **Docs** — Translations, clarifications, and examples are always appreciated

### Code Style

- Python: follow [PEP 8](https://pep8.org/)
- Docstrings for all public functions
- Type hints where possible

---

## 📜 License

MIT License — see [LICENSE](./LICENSE) for details.

---

<div align="center">

**Made with ❤️ for AI Agents**

*If this project saves you time, consider giving it a ⭐*

</div>
