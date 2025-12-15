from pathlib import Path
from typing import Optional

from langchain_core.tools import tool


@tool
def echo(text: str) -> str:
    """简单回声工具：原样返回输入文本。"""

    return text


@tool
def read_file(path: str, offset: int = 0, limit: int = 4000) -> str:
    """读取指定文件的部分内容，用于快速查看文本文件。

    Args:
        path: 文件路径（绝对或相对）。
        offset: 跳过的字符数。
        limit: 读取的最大字符数，默认 4000。
    """

    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    if not file_path.is_file():
        raise IsADirectoryError(f"目标不是文件: {file_path}")

    content = file_path.read_text(encoding="utf-8", errors="ignore")
    start = min(max(offset, 0), len(content))
    end = min(start + max(limit, 0), len(content))
    return content[start:end]


@tool
def list_dir(path: str = ".") -> str:
    """列出目录内容，便于浏览项目结构。"""

    dir_path = Path(path).expanduser().resolve()
    if not dir_path.exists():
        raise FileNotFoundError(f"目录不存在: {dir_path}")
    if not dir_path.is_dir():
        raise NotADirectoryError(f"目标不是目录: {dir_path}")

    entries = sorted(p.name for p in dir_path.iterdir())
    return "\n".join(entries)


TOOLS = [echo, read_file, list_dir]
TOOL_REGISTRY = {tool.name: tool for tool in TOOLS}

__all__ = ["TOOLS", "TOOL_REGISTRY", "echo", "read_file", "list_dir"]

