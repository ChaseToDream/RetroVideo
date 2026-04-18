from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import Video, Task
from app.services.upload import upload_video
from app.services.preview import generate_preview
from app.services.storage import storage
from app.tasks.task_manager import create_task, process_video_task, get_task
from app.utils.presets import list_presets, load_preset

router = APIRouter(prefix="/api/v1")


@router.post("/videos/upload", status_code=201)
async def api_upload_video(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    try:
        video = await upload_video(file, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

    return {
        "id": str(video.id),
        "filename": video.filename,
        "file_size": video.file_size,
        "duration": video.duration,
        "resolution": f"{video.width}x{video.height}" if video.width and video.height else None,
        "fps": video.fps,
        "format": video.format,
        "created_at": video.created_at.isoformat(),
        "preview_url": f"/api/v1/videos/{video.id}/preview",
        "expires_at": video.expires_at.isoformat(),
    }


@router.get("/videos/{video_id}")
async def api_get_video(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    return {
        "id": str(video.id),
        "filename": video.filename,
        "file_size": video.file_size,
        "duration": video.duration,
        "resolution": f"{video.width}x{video.height}" if video.width and video.height else None,
        "fps": video.fps,
        "format": video.format,
        "created_at": video.created_at.isoformat(),
        "expires_at": video.expires_at.isoformat(),
    }


@router.get("/videos/{video_id}/preview")
async def api_get_preview(video_id: str, preset: str = "nokia_6600", db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    try:
        preview_path = await generate_preview(video.storage_path, preset)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览生成失败: {str(e)}")

    full_path = storage.get_full_path(preview_path)
    return FileResponse(full_path, media_type="video/mp4", filename=f"preview_{preset}.mp4")


@router.post("/videos/{video_id}/process", status_code=202)
async def api_process_video(video_id: str, body: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    preset = body.get("preset", "nokia_6600")
    params = body.get("params", {})

    task = await create_task(video_id, preset, params, db)

    import asyncio
    asyncio.create_task(process_video_task(task.id, None))

    return {
        "task_id": str(task.id),
        "video_id": str(video.id),
        "status": task.status,
        "estimated_time": 25,
        "created_at": task.created_at.isoformat(),
    }


@router.get("/tasks/{task_id}")
async def api_get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    task = await get_task(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    resp = {
        "task_id": str(task.id),
        "video_id": str(task.video_id),
        "preset": task.preset,
        "status": task.status,
        "progress": task.progress,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }
    if task.output_path:
        resp["download_url"] = f"/api/v1/downloads/{task.id}"
    if task.error_msg:
        resp["error_msg"] = task.error_msg
    if task.completed_at:
        resp["completed_at"] = task.completed_at.isoformat()
    return resp


@router.get("/tasks/{task_id}/progress")
async def api_get_progress(task_id: str, db: AsyncSession = Depends(get_db)):
    task = await get_task(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "task_id": str(task.id),
        "status": task.status,
        "progress": task.progress,
        "current_step": _get_step_description(task.progress),
        "elapsed_time": 0,
        "estimated_remaining": 0,
    }


@router.get("/presets")
async def api_list_presets():
    return list_presets()


@router.get("/presets/{name}")
async def api_get_preset(name: str):
    try:
        return load_preset(name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"预设 '{name}' 不存在")


@router.get("/downloads/{task_id}")
async def api_download_result(task_id: str, db: AsyncSession = Depends(get_db)):
    task = await get_task(task_id, db)
    if not task or task.status != "completed" or not task.output_path:
        raise HTTPException(status_code=404, detail="处理结果不存在")

    full_path = storage.get_full_path(task.output_path)
    if not storage.exists(task.output_path):
        raise HTTPException(status_code=404, detail="文件已过期")

    filename = f"retrovid_{task.preset}_{task.output_path.split('/')[-1]}"
    return FileResponse(full_path, media_type="video/mp4", filename=filename)


@router.delete("/videos/{video_id}")
async def api_delete_video(video_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    storage.delete(video.storage_path)

    task_result = await db.execute(select(Task).where(Task.video_id == video_id))
    for task in task_result.scalars().all():
        if task.output_path:
            storage.delete(task.output_path)
        await db.delete(task)

    await db.delete(video)
    await db.commit()

    return {"message": "删除成功"}


def _get_step_description(progress: int) -> str:
    if progress < 10:
        return "准备处理"
    elif progress < 30:
        return "缩放分辨率"
    elif progress < 50:
        return "应用复古滤镜"
    elif progress < 70:
        return "添加噪点与扫描线"
    elif progress < 90:
        return "编码输出"
    else:
        return "处理完成"
