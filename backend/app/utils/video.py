import asyncio
import json
import uuid
from pathlib import Path
from typing import Any

from app.core.config import settings


async def extract_video_info(file_path: str) -> dict[str, Any]:
    """使用 ffprobe 提取视频元信息"""
    cmd = [
        settings.FFPROBE_PATH,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        file_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {file_path}")

    probe = json.loads(stdout)
    video_stream = None
    for s in probe.get("streams", []):
        if s.get("codec_type") == "video":
            video_stream = s
            break

    fmt = probe.get("format", {})
    duration = float(fmt.get("duration", 0))

    info = {
        "duration": duration,
        "width": None,
        "height": None,
        "fps": None,
        "format": fmt.get("format_name", "").split(",")[0],
    }

    if video_stream:
        info["width"] = video_stream.get("width")
        info["height"] = video_stream.get("height")
        r_frame_rate = video_stream.get("r_frame_rate", "0/1")
        try:
            num, den = r_frame_rate.split("/")
            info["fps"] = round(float(num) / float(den), 2) if float(den) != 0 else 0
        except (ValueError, ZeroDivisionError):
            info["fps"] = 0

    return info


def validate_file_extension(filename: str) -> bool:
    """校验文件扩展名是否在白名单中"""
    ext = Path(filename).suffix.lstrip(".").lower()
    allowed = settings.ALLOWED_FORMATS.split(",")
    return ext in allowed


def generate_storage_path(filename: str) -> tuple[str, str]:
    """生成唯一存储路径，返回 (相对路径, 完整路径)"""
    file_id = str(uuid.uuid4())
    ext = Path(filename).suffix
    relative = f"{file_id}{ext}"
    full = str(Path(settings.STORAGE_PATH) / relative)
    return relative, full
