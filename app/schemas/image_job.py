from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ImageJobCreate(BaseModel):
    project_id: UUID
    prompt: str = Field(..., min_length=1, max_length=2000)
    negative_prompt: str | None = None
    width: int = Field(default=512, ge=64, le=2048)
    height: int = Field(default=512, ge=64, le=2048)


class ImageJobUpdate(BaseModel):
    status: str | None = Field(default=None)
    output_payload: dict[str, Any] | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ImageJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    project_id: UUID
    job_type: str
    status: str
    input_payload: dict[str, Any] | None = None
    output_payload: dict[str, Any] | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ImageJobListResponse(BaseModel):
    items: list[ImageJobRead]
    total: int