from app.core.config import STORAGE_BACKEND
from app.services.storage.local_storage import LocalStorageService


def get_storage_service():
    if STORAGE_BACKEND == "local":
        return LocalStorageService()

    raise ValueError(f"Unsupported STORAGE_BACKEND: {STORAGE_BACKEND}")
