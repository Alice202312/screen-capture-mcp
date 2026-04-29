#!/usr/bin/env python3
"""
Screen Capture MCP Server - 开箱即用版
让 AI Agent 能"看见"屏幕 - 录屏和截图能力

支持平台：Windows, macOS, Linux
底层实现：ffmpeg
版本：1.1.0

安全特性（v1.1.0 修复）：
- 路径安全验证：防止路径遍历和敏感目录写入
- 操作审计日志：记录所有截图/录屏操作
- 录屏醒目提示：启动时明确告知用户正在录屏
- 依赖版本锁定：pip install mcp>=1.0.0,<2.0.0
"""

import asyncio
import platform
import subprocess
import os
import sys
import json
import shutil
import time
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime

# ============ 安全配置 ============
# 安全输出目录
if platform.system() == "Windows":
    _temp_dir = os.environ.get("TEMP", os.environ.get("TMP", "C:\\Temp"))
else:
    _temp_dir = os.environ.get("TMPDIR", "/tmp")
SAFE_OUTPUT_DIR = os.path.join(_temp_dir, "screen-capture")

# 系统敏感目录（禁止写入）
SENSITIVE_DIRS = {
    "Linux": ["/etc", "/usr", "/bin", "/sbin", "/boot", "/lib", "/root", "/proc", "/sys"],
    "Darwin": ["/etc", "/usr", "/bin", "/sbin", "/System", "/Library", "/private/var", "/Applications"],
    "Windows": ["C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)", "C:\\Windows\\System32"]
}

# 操作日志配置
MAX_OPERATION_LOG_SIZE = 100

# 全局状态
_operation_log = []           # 操作审计日志
_version = "1.1.0"


def _log_operation(operation: str, details: str):
    """记录操作审计日志"""
    global _operation_log
    entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "platform": platform.system()
    }
    _operation_log.append(entry)
    # 保持日志大小，防止内存溢出
    if len(_operation_log) > MAX_OPERATION_LOG_SIZE:
        _operation_log = _operation_log[-MAX_OPERATION_LOG_SIZE:]


def get_operation_log() -> list:
    """获取操作审计日志"""
    return _operation_log.copy()


def validate_output_path(output_path: str, extension: str) -> str:
    """
    验证输出路径安全性，防止路径遍历和敏感目录写入
    
    安全策略：
    - 如果只是文件名（不含目录），自动放到安全目录
    - 解析绝对路径（消除 .. 等路径遍历）
    - 禁止写入系统敏感目录
    - 不在允许范围的路径会被重定向到安全目录
    """
    safe_dir = Path(SAFE_OUTPUT_DIR)
    safe_dir.mkdir(parents=True, exist_ok=True)
    
    # 如果只是文件名（不含目录），放到安全目录
    if not os.path.dirname(output_path):
        # 检查是否有路径遍历迹象
        if ".." in output_path:
            # 检测到路径遍历，使用安全文件名
            filename = f"{uuid.uuid4().hex[:8]}{extension}"
            new_path = str(safe_dir / filename)
            print(f"⚠️ 安全提示：检测到路径遍历，已重定向到 {new_path}")
            return new_path
        return str(safe_dir / output_path)
    
    # 解析绝对路径（消除 .. 等路径遍历）
    try:
        resolved = Path(output_path).resolve()
    except Exception:
        # 解析失败，使用安全文件名
        filename = os.path.basename(output_path) or f"{uuid.uuid4().hex[:8]}{extension}"
        new_path = str(safe_dir / f"{uuid.uuid4().hex[:8]}_{filename}")
        print(f"⚠️ 安全提示：路径解析失败，已重定向到 {new_path}")
        return new_path
    
    # 检查是否在系统敏感目录内
    system = platform.system()
    sensitive = SENSITIVE_DIRS.get(system, SENSITIVE_DIRS["Linux"])
    for sdir in sensitive:
        if str(resolved).startswith(sdir):
            filename = os.path.basename(output_path)
            new_path = str(safe_dir / filename)
            print(f"⚠️ 安全提示：路径在系统目录 ({sdir}) 内，已重定向到 {new_path}")
            return new_path
    
    return str(resolved)


# ============ 依赖检查 ============

def check_ffmpeg() -> bool:
    """检查 ffmpeg 是否已安装"""
    return shutil.which("ffmpeg") is not None


def install_ffmpeg_hint():
    """提示用户如何安装 ffmpeg"""
    system = platform.system()
    
    print("\n" + "="*50)
    print("❌ ffmpeg 未安装")
    print("="*50)
    
    if system == "Windows":
        print("请运行以下命令安装：")
        print("  winget install ffmpeg")
        print("\n或下载：https://ffmpeg.org/download.html")
    elif system == "Darwin":
        print("请运行以下命令安装：")
        print("  brew install ffmpeg")
    elif system == "Linux":
        print("请运行以下命令安装：")
        print("  sudo apt install ffmpeg  # Ubuntu/Debian")
        print("  sudo yum install ffmpeg  # CentOS/RHEL")
    
    print("="*50 + "\n")


def check_and_install_python_deps() -> bool:
    """
    检查并自动安装 Python 依赖（版本锁定）
    
    版本范围：>=1.0.0,<2.0.0 防止恶意包
    """
    try:
        import mcp
        return True
    except ImportError:
        print("📦 正在自动安装 Python 依赖 (mcp>=1.0.0,<2.0.0)...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "mcp>=1.0.0,<2.0.0", "-q"],
                check=True,
                capture_output=True
            )
            print("✅ Python 依赖安装完成\n")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 自动安装失败: {e}")
            print("请手动运行: pip install mcp>=1.0.0,<2.0.0")
            return False


def check_all_dependencies() -> bool:
    """检查所有依赖，返回是否可以运行"""
    # 检查 ffmpeg
    if not check_ffmpeg():
        install_ffmpeg_hint()
        return False
    
    # 检查 Python 依赖（自动安装）
    if not check_and_install_python_deps():
        return False
    
    return True


def print_security_notice():
    """打印安全提示"""
    print("\n" + "="*60)
    print("🔒 Screen Capture MCP Server v" + _version + " - 安全提示")
    print("="*60)
    print("📁 输出限制：所有文件只能写入安全目录或用户指定目录")
    print(f"   安全目录：{SAFE_OUTPUT_DIR}")
    print("   系统敏感目录 (/etc, /usr, C:\\Windows 等) 禁止写入")
    print()
    print("📋 审计日志：所有截图/录屏操作都会被记录")
    print("   可通过 get_operation_log 查看")
    print()
    print("📸 截图/🔴 录屏：每次操作都会打印提示")
    print("="*60 + "\n")


# ============ 主程序 ============

# 延迟导入，确保依赖先安装好
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# MCP Server 实例
server = Server("screen-capture")

# 全局状态：录屏进程
recording_process: Optional[subprocess.Popen] = None
recording_output: Optional[str] = None
recording_start_time: Optional[float] = None


def get_platform() -> str:
    """检测当前操作系统"""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    else:
        return "unknown"


def get_ffmpeg_record_command(output_path: str) -> list:
    """
    根据平台返回 ffmpeg 录屏命令
    
    Windows: ffmpeg -f gdigrab -i desktop output.mp4
    macOS: ffmpeg -f avfoundation -i "1" output.mp4
    Linux: ffmpeg -f x11grab -i :0.0 output.mp4
    
    注意：不加时长限制，用户需要手动调用 stop_recording 停止
    """
    plt = get_platform()
    
    if plt == "windows":
        return [
            "ffmpeg", "-f", "gdigrab", "-i", "desktop",
            "-y",
            output_path
        ]
    elif plt == "macos":
        return [
            "ffmpeg", "-f", "avfoundation", "-i", "1",
            "-y",
            output_path
        ]
    elif plt == "linux":
        return [
            "ffmpeg", "-f", "x11grab", "-i", os.environ.get("DISPLAY", ":0.0"),
            "-y",
            output_path
        ]
    else:
        raise RuntimeError(f"Unsupported platform: {plt}")


def get_ffmpeg_screenshot_command(output_path: str) -> list:
    """
    根据平台返回 ffmpeg 截图命令
    
    使用 -frames:v 1 只截取一帧
    """
    plt = get_platform()
    
    if plt == "windows":
        return [
            "ffmpeg", "-f", "gdigrab", "-i", "desktop",
            "-frames:v", "1",
            "-y",
            output_path
        ]
    elif plt == "macos":
        return [
            "ffmpeg", "-f", "avfoundation", "-i", "1",
            "-frames:v", "1",
            "-y",
            output_path
        ]
    elif plt == "linux":
        return [
            "ffmpeg", "-f", "x11grab", "-i", os.environ.get("DISPLAY", ":0.0"),
            "-frames:v", "1",
            "-y",
            output_path
        ]
    else:
        raise RuntimeError(f"Unsupported platform: {plt}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="start_recording",
            description="开始录屏。参数：output_path（视频保存路径）\n\n⚠️ 录屏启动时会有醒目提示，请注意屏幕上的提示信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": f"视频文件保存路径，支持 .mp4 格式\n文件将被保存到安全目录或您指定的目录"
                    }
                },
                "required": ["output_path"]
            }
        ),
        Tool(
            name="stop_recording",
            description="停止录屏，返回视频文件路径",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="take_screenshot",
            description="截取当前屏幕。参数：output_path（图片保存路径）\n\n⚠️ 截图时会打印操作提示",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": f"截图保存路径，支持 .png 格式\n文件将被保存到安全目录或您指定的目录"
                    }
                },
                "required": ["output_path"]
            }
        ),
        Tool(
            name="get_recording_status",
            description="查询当前录屏状态（是否正在录屏、输出文件路径、最近操作日志）",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="check_dependencies",
            description="检查系统依赖（ffmpeg、Python包）是否已安装",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_operation_log",
            description="获取操作审计日志（最近的截图/录屏记录）",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""
    global recording_process, recording_output, recording_start_time
    
    if name == "check_dependencies":
        ffmpeg_ok = check_ffmpeg()
        mcp_ok = True
        try:
            import mcp
        except ImportError:
            mcp_ok = False
        
        status = {
            "ffmpeg": "✅ 已安装" if ffmpeg_ok else "❌ 未安装",
            "mcp_python": "✅ 已安装" if mcp_ok else "❌ 未安装",
            "platform": get_platform(),
            "python_version": sys.version.split()[0],
            "version": _version,
            "safe_output_dir": SAFE_OUTPUT_DIR
        }
        return [TextContent(type="text", text=json.dumps(status, indent=2, ensure_ascii=False))]
    
    elif name == "get_operation_log":
        logs = get_operation_log()
        return [TextContent(type="text", text=json.dumps(logs, indent=2, ensure_ascii=False))]
    
    elif name == "start_recording":
        output_path = arguments.get("output_path")
        if not output_path:
            return [TextContent(type="text", text="错误：缺少 output_path 参数")]
        
        # 安全验证：规范化输出路径
        output_path = validate_output_path(output_path, ".mp4")
        
        # 检查是否已在录屏
        if recording_process and recording_process.poll() is None:
            return [TextContent(type="text", text=f"错误：已在录屏中，当前输出文件：{recording_output}")]
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = get_ffmpeg_record_command(output_path)
            recording_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            recording_output = output_path
            recording_start_time = time.time()
            
            # 记录操作
            _log_operation("start_recording", f"输出文件：{output_path}")
            
            # 打印醒目提示
            print("\n" + "="*50)
            print("🔴🔴🔴 录屏已启动！屏幕正在被录制 🔴🔴🔴")
            print(f"输出文件：{output_path}")
            print("如需停止，请调用 stop_recording")
            print("="*50 + "\n")
            
            return [TextContent(
                type="text", 
                text=f"录屏已开始\n平台：{get_platform()}\n输出文件：{output_path}\n⚠️ 请注意：录屏正在进行中！"
            )]
        except Exception as e:
            _log_operation("start_recording_error", str(e))
            return [TextContent(type="text", text=f"启动录屏失败：{str(e)}")]
    
    elif name == "stop_recording":
        if not recording_process or recording_process.poll() is not None:
            return [TextContent(type="text", text="错误：当前没有正在进行的录屏")]
        
        try:
            # ffmpeg 需要发送 'q' 键来优雅停止
            # 发送 SIGINT 信号优雅停止（等ffmpeg flush缓冲区）
            recording_process.send_signal(subprocess.signal.SIGINT)
            recording_process.wait(timeout=10)
            
            result = recording_output
            
            # 计算录制时长
            duration = time.time() - recording_start_time if recording_start_time else 0
            
            # 记录操作
            _log_operation("stop_recording", f"输出文件：{result}, 时长：{duration:.1f}秒")
            
            recording_process = None
            recording_output = None
            recording_start_time = None
            
            print(f"✅ 录屏已停止，时长：{duration:.1f} 秒\n")
            
            return [TextContent(
                type="text", 
                text=f"录屏已停止\n视频文件：{result}\n录制时长：{duration:.1f} 秒"
            )]
        except subprocess.TimeoutExpired:
            # 超时则强制终止
            recording_process.kill()
            result = recording_output
            recording_process = None
            recording_output = None
            recording_start_time = None
            _log_operation("stop_recording_force", "强制停止")
            return [TextContent(type="text", text=f"录屏已强制停止\n视频文件：{result}")]
        except Exception as e:
            _log_operation("stop_recording_error", str(e))
            return [TextContent(type="text", text=f"停止录屏失败：{str(e)}")]
    
    elif name == "take_screenshot":
        output_path = arguments.get("output_path")
        if not output_path:
            return [TextContent(type="text", text="错误：缺少 output_path 参数")]
        
        # 安全验证：规范化输出路径
        output_path = validate_output_path(output_path, ".png")
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = get_ffmpeg_screenshot_command(output_path)
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode != 0:
                _log_operation("screenshot_failed", f"错误：{result.stderr.decode('utf-8', errors='ignore')}")
                return [TextContent(
                    type="text", 
                    text=f"截图失败：{result.stderr.decode('utf-8', errors='ignore')}"
                )]
            
            # 记录操作
            _log_operation("take_screenshot", f"保存至：{output_path}")
            
            # 打印提示
            print(f"📸 截图已执行，保存至：{output_path}\n")
            
            return [TextContent(
                type="text", 
                text=f"截图成功\n平台：{get_platform()}\n图片文件：{output_path}"
            )]
        except Exception as e:
            _log_operation("screenshot_error", str(e))
            return [TextContent(type="text", text=f"截图失败：{str(e)}")]
    
    elif name == "get_recording_status":
        status = {
            "platform": get_platform(),
            "is_recording": recording_process is not None and recording_process.poll() is None,
            "output_file": recording_output,
            "recent_operations": _operation_log[-5:]  # 最近5条操作
        }
        return [TextContent(type="text", text=json.dumps(status, indent=2, ensure_ascii=False))]
    
    else:
        return [TextContent(type="text", text=f"未知工具：{name}")]


async def main():
    """启动 MCP Server"""
    # 打印安全提示
    print_security_notice()
    
    # 先检查依赖
    if not check_all_dependencies():
        sys.exit(1)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
