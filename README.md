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
| MCP Client | Any | Claude Desktop, Cursor, etc. |

The `mcp` Python package is installed **automatically** on first run.

---

## 🔧 Auto Dependency Handling

On startup, the server automatically:

1. **Checks for ffmpeg** — if missing, prints platform-specific install instructions and exits
2. **Installs `mcp` Python package** — silent background install via pip, zero manual steps

You only need to install ffmpeg. Everything else Just Works™.

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
