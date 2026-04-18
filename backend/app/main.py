from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.database import init_db
    await init_db()
    from pathlib import Path
    Path(settings.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    Path(settings.STORAGE_PATH, "previews").mkdir(parents=True, exist_ok=True)
    Path(settings.STORAGE_PATH, "results").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="RetroVid API",
    description="复古视频画质转换工具 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
