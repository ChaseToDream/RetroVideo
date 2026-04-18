from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./retrovid.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "./uploads"
    MAX_FILE_SIZE: int = 524288000
    ALLOWED_FORMATS: str = "mp4,avi,mov,mkv,webm"
    FFMPEG_PATH: str = "ffmpeg"
    FFPROBE_PATH: str = "ffprobe"
    PREVIEW_DURATION: int = 5
    RESULT_EXPIRE_HOURS: int = 24
    UPLOAD_EXPIRE_HOURS: int = 48
    MAX_CONCURRENT_TASKS: int = 3

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
