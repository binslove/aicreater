from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Job


def create_image_job(
    db: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    prompt: str,
    negative_prompt: str | None,
    width: int,
    height: int,
) -> Job:
    job = Job(
        user_id=user_id,
        project_id=project_id,
        job_type="image_generation",
        status="queued",
        input_payload={
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
        },
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_image_job_by_id(db: Session, job_id: UUID) -> Job | None:
    stmt = select(Job).where(
        Job.id == job_id,
        Job.job_type == "image_generation",
    )
    return db.scalar(stmt)


def update_image_job_status(
    db: Session,
    *,
    job: Job,
    status: str,
    error_message: str | None = None,
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
) -> Job:
    job.status = status
    job.error_message = error_message

    if started_at is not None:
        job.started_at = started_at

    if completed_at is not None:
        job.completed_at = completed_at

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_image_job_output(
    db: Session,
    *,
    job: Job,
    output_payload: dict[str, Any],
) -> Job:
    job.output_payload = output_payload
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
