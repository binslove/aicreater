import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

COMFYUI_BASE_URL = os.getenv("COMFYUI_BASE_URL", "http://127.0.0.1:8188")
COMFYUI_TIMEOUT_SECONDS = int(os.getenv("COMFYUI_TIMEOUT_SECONDS", "120"))

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
STORAGE_ROOT = os.getenv("STORAGE_ROOT", "storage")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")
