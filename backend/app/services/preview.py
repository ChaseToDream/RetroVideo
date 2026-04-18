import uuid
from pathlib import Path

from app.core.config import settings
from app.services.ffmpeg_engine import build_ffmpeg_command, run_ffmpeg
from app.services.storage import storage


async def generate_preview(
    source_storage_path: str,
    preset_name: str,
    params: dict | None = None,
) -> str:
    """生成预览视频，返回存储的相对路径"""
    source_full = storage.get_full_path(source_storage_path)
    if not storage.exists(source_storage_path):
        raise FileNotFoundError(f"源文件不存在: {source_storage_path}")

    preview_id = str(uuid.uuid4())
    output_format = "mp4"
    relative_path = f"previews/{preview_id}.{output_format}"
    output_full = storage.get_full_path(relative_path)

    cmd = build_ffmpeg_command(
        input_path=source_full,
        output_path=output_full,
        preset_name=preset_name,
        params=params,
        is_preview=True,
    )

    success, _ = await run_ffmpeg(cmd)
    if not success:
        raise RuntimeError("预览生成失败")

    return relative_path
