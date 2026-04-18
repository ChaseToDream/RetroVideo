import uuid
from datetime import datetime, timezone, timedelta

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.models import Video
from app.services.storage import storage
from app.utils.video import extract_video_info, validate_file_extension, generate_storage_path


async def upload_video(file: UploadFile, db: AsyncSession) -> Video:
    if not validate_file_extension(file.filename):
        raise ValueError(f"不支持的文件格式: {file.filename}")

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise ValueError(f"文件大小超过限制 ({settings.MAX_FILE_SIZE // 1024 // 1024}MB)")

    relative_path, full_path = generate_storage_path(file.filename)
    async with aiofiles.open(full_path, "wb") as f:
        await f.write(content)

    try:
        info = await extract_video_info(full_path)
    except Exception:
        info = {"duration": 0, "width": None, "height": None, "fps": None, "format": None}

    now = datetime.now(timezone.utc)
    video = Video(
        id=str(uuid.uuid4()),
        filename=file.filename,
        file_size=len(content),
        duration=info.get("duration"),
        width=info.get("width"),
        height=info.get("height"),
        fps=info.get("fps"),
        format=info.get("format"),
        storage_path=relative_path,
        created_at=now,
        expires_at=now + timedelta(hours=settings.UPLOAD_EXPIRE_HOURS),
    )

    db.add(video)
    await db.commit()
    await db.refresh(video)
    return video
