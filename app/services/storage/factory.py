from __future__ import annotations

from app.core.config import STORAGE_BACKEND
from app.services.storage.r2 import R2StorageService


def get_storage_service():
    if STORAGE_BACKEND == "r2":
        return R2StorageService()

    raise ValueError(f"Unsupported storage backend: {STORAGE_BACKEND}")
