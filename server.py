#!/usr/bin/env python3
"""
Screen Capture MCP Server - 开箱即用版
让 AI Agent 能"看见"屏幕 - 录屏和截图能力

支持平台：Windows, macOS, Linux
底层实现：ffmpeg
"""

import asyncio
import platform
import subprocess
import os
import sys
import json
import shutil
from pathlib import Path
from typing import Optional

# ============ 依赖检查与自动安装 ============

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


def check_and_install_python_deps():
    """检查并自动安装 Python 依赖"""
    try:
        import mcp
        return True
    except ImportError:
        print("📦 正在自动安装 Python 依赖 (mcp)...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "mcp", "-q"],
                check=True
            )
            print("✅ Python 依赖安装完成\n")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 自动安装失败: {e}")
            print("请手动运行: pip install mcp")
            return False


def check_all_dependencies() -> bool:
    """检查所有依赖，返回是否可以运行"""
    # 检查 ffmpeg
    if not check_ffmpeg():
        install_ffmpeg_hint()
        return False
    
    # 检查并安装 Python 依赖
    if not check_and_install_python_deps():
        return False
    
    return True


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
    """
    plt = get_platform()
    
    if plt == "windows":
        return [
            "ffmpeg", "-f", "gdigrab", "-i", "desktop",
            "-y",  # 覆盖已存在文件
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
            "ffmpeg", "-f", "x11grab", "-i", ":0.0",
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
            "ffmpeg", "-f", "x11grab", "-i", ":0.0",
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
            description="开始录屏。参数：output_path（视频保存路径，如 /tmp/screen.mp4）",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": "视频文件保存路径，支持 .mp4 格式"
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
            description="截取当前屏幕。参数：output_path（图片保存路径，如 /tmp/screen.png）",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": "截图保存路径，支持 .png 格式"
                    }
                },
                "required": ["output_path"]
            }
        ),
        Tool(
            name="get_recording_status",
            description="查询当前录屏状态（是否正在录屏、输出文件路径）",
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
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""
    global recording_process, recording_output
    
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
            "python_version": sys.version.split()[0]
        }
        return [TextContent(type="text", text=json.dumps(status, indent=2, ensure_ascii=False))]
    
    elif name == "start_recording":
        output_path = arguments.get("output_path")
        if not output_path:
            return [TextContent(type="text", text="错误：缺少 output_path 参数")]
        
        # 检查是否已在录屏
        if recording_process and recording_process.poll() is None:
            return [TextContent(type="text", text=f"错误：已在录屏中，当前输出文件：{recording_output}")]
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = get_ffmpeg_record_command(output_path)
            recording_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            recording_output = output_path
            
            return [TextContent(
                type="text", 
                text=f"录屏已开始\n平台：{get_platform()}\n输出文件：{output_path}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"启动录屏失败：{str(e)}")]
    
    elif name == "stop_recording":
        if not recording_process or recording_process.poll() is not None:
            return [TextContent(type="text", text="错误：当前没有正在进行的录屏")]
        
        try:
            # ffmpeg 需要发送 'q' 键来优雅停止
            recording_process.communicate(input=b'q', timeout=5)
            recording_process.wait(timeout=5)
            
            result = recording_output
            recording_process = None
            recording_output = None
            
            return [TextContent(
                type="text", 
                text=f"录屏已停止\n视频文件：{result}"
            )]
        except subprocess.TimeoutExpired:
            # 超时则强制终止
            recording_process.kill()
            result = recording_output
            recording_process = None
            recording_output = None
            return [TextContent(type="text", text=f"录屏已强制停止\n视频文件：{result}")]
        except Exception as e:
            return [TextContent(type="text", text=f"停止录屏失败：{str(e)}")]
    
    elif name == "take_screenshot":
        output_path = arguments.get("output_path")
        if not output_path:
            return [TextContent(type="text", text="错误：缺少 output_path 参数")]
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = get_ffmpeg_screenshot_command(output_path)
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode != 0:
                return [TextContent(
                    type="text", 
                    text=f"截图失败：{result.stderr.decode('utf-8', errors='ignore')}"
                )]
            
            return [TextContent(
                type="text", 
                text=f"截图成功\n平台：{get_platform()}\n图片文件：{output_path}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"截图失败：{str(e)}")]
    
    elif name == "get_recording_status":
        status = {
            "platform": get_platform(),
            "is_recording": recording_process is not None and recording_process.poll() is None,
            "output_file": recording_output
        }
        return [TextContent(type="text", text=json.dumps(status, indent=2, ensure_ascii=False))]
    
    else:
        return [TextContent(type="text", text=f"未知工具：{name}")]


async def main():
    """启动 MCP Server"""
    # 先检查依赖
    if not check_all_dependencies():
        sys.exit(1)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
