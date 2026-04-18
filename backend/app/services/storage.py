import os
import shutil
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings


class StorageService:
    """本地文件存储服务（开发阶段），后续可替换为 MinIO/S3"""

    def __init__(self):
        self.base_path = Path(settings.STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, file: BinaryIO, relative_path: str) -> str:
        """保存文件到存储，返回完整路径"""
        full_path = self.base_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(file, f)
        return str(full_path)

    async def save_bytes(self, data: bytes, relative_path: str) -> str:
        """保存字节数据到存储"""
        full_path = self.base_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(data)
        return str(full_path)

    def get_full_path(self, relative_path: str) -> str:
        """获取完整文件路径"""
        return str(self.base_path / relative_path)

    def get_file_size(self, relative_path: str) -> int:
        """获取文件大小"""
        full_path = self.base_path / relative_path
        return full_path.stat().st_size if full_path.exists() else 0

    def exists(self, relative_path: str) -> bool:
        """检查文件是否存在"""
        return (self.base_path / relative_path).exists()

    def delete(self, relative_path: str) -> bool:
        """删除文件"""
        full_path = self.base_path / relative_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False


storage = StorageService()
