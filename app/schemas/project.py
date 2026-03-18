from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ProjectCreate(BaseModel):
    prompt: str
    plot_text: str | None = None


class ProjectRead(BaseModel):
    id: UUID
    user_id: UUID
    prompt: str
    plot_text: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
