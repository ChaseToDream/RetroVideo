import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Task
from app.services.ffmpeg_engine import build_ffmpeg_command, run_ffmpeg
from app.services.storage import storage


async def create_task(video_id, preset: str, params: dict, db: AsyncSession) -> Task:
    task = Task(
        id=str(uuid.uuid4()),
        video_id=video_id,
        preset=preset,
        params=params,
        status="queued",
        progress=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def process_video_task(task_id, db_session_factory):
    from app.core.database import async_session

    async with async_session() as db:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            return

        await _update_task(db, task.id, status="processing", progress=0)

        from app.models.models import Video
        video_result = await db.execute(select(Video).where(Video.id == task.video_id))
        video = video_result.scalar_one_or_none()
        if not video:
            await _update_task(db, task.id, status="failed", error_msg="源视频不存在")
            return

        source_full = storage.get_full_path(video.storage_path)
        if not storage.exists(video.storage_path):
            await _update_task(db, task.id, status="failed", error_msg="源文件不存在")
            return

        output_id = str(uuid.uuid4())
        output_format = task.params.get("output", {}).get("format", "mp4") if isinstance(task.params, dict) else "mp4"
        output_ext = "3gp" if output_format == "3gp" else "mp4"
        output_relative = f"results/{output_id}.{output_ext}"
        output_full = storage.get_full_path(output_relative)

        cmd = build_ffmpeg_command(
            input_path=source_full,
            output_path=output_full,
            preset_name=task.preset,
            params=task.params if task.params else None,
        )

        success, output = await run_ffmpeg(cmd)

        if success and storage.exists(output_relative):
            file_size = storage.get_file_size(output_relative)
            await _update_task(
                db, task.id,
                status="completed",
                progress=100,
                output_path=output_relative,
                output_size=file_size,
                completed_at=datetime.now(timezone.utc),
            )
        else:
            await _update_task(
                db, task.id,
                status="failed",
                error_msg=f"FFmpeg 处理失败: {output[-500:] if output else 'unknown error'}",
            )


async def _update_task(db: AsyncSession, task_id, **kwargs):
    kwargs["updated_at"] = datetime.now(timezone.utc)
    await db.execute(update(Task).where(Task.id == task_id).values(**kwargs))
    await db.commit()


async def get_task(task_id, db: AsyncSession) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()
