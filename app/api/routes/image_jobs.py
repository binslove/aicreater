from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.image_job import (
    create_image_job,
    get_image_jobs_by_project,
    update_image_job,
)
from app.crud.media import create_media_from_image_job_result
from app.db.database import get_db
from app.db.models import Job, Project, User
from app.schemas.image_job import (
    ImageJobCreate,
    ImageJobListResponse,
    ImageJobRead,
    ImageJobUpdate,
)

router = APIRouter(prefix="/image-jobs", tags=["image-jobs"])


# -----------------------------
# 권한 체크
# -----------------------------
def require_project_owner(db: Session, project_id: UUID, current_user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return project


def require_image_job_owner(db: Session, job_id: UUID, current_user: User) -> Job:
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.job_type == "image_generation",
    ).first()

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image job not found",
        )

    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return job


# -----------------------------
# CREATE
# -----------------------------
@router.post("", response_model=ImageJobRead, status_code=status.HTTP_201_CREATED)
def create_image_job_endpoint(
    payload: ImageJobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ImageJobRead:
    require_project_owner(db, payload.project_id, current_user)

    job = create_image_job(
        db=db,
        user_id=current_user.id,
        project_id=payload.project_id,
        prompt=payload.prompt,
        negative_prompt=payload.negative_prompt,
        width=payload.width,
        height=payload.height,
    )

    return job


# -----------------------------
# READ (단건)
# -----------------------------
@router.get("/{job_id}", response_model=ImageJobRead)
def get_image_job_endpoint(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ImageJobRead:
    job = require_image_job_owner(db, job_id, current_user)
    return job


# -----------------------------
# LIST (프로젝트 기준)
# -----------------------------
@router.get("/project/{project_id}", response_model=ImageJobListResponse)
def list_project_image_jobs_endpoint(
    project_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ImageJobListResponse:
    require_project_owner(db, project_id, current_user)

    items, total = get_image_jobs_by_project(
        db=db,
        project_id=project_id,
        skip=skip,
        limit=limit,
    )

    return ImageJobListResponse(items=items, total=total)


# -----------------------------
# PATCH (상태 변경 / 결과 저장 / 완료 시 media 자동 생성)
# -----------------------------
@router.patch("/{job_id}", response_model=ImageJobRead)
def patch_image_job_endpoint(
    job_id: UUID,
    payload: ImageJobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ImageJobRead:
    job = require_image_job_owner(db, job_id, current_user)

    update_data = payload.model_dump(exclude_unset=True)
    new_status = update_data.get("status")

    if new_status is not None:
        allowed_statuses = {"queued", "running", "completed", "failed"}

        if new_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status",
            )

        if new_status == "running" and "started_at" not in update_data:
            update_data["started_at"] = datetime.now(timezone.utc)

        if new_status in {"completed", "failed"} and "completed_at" not in update_data:
            update_data["completed_at"] = datetime.now(timezone.utc)

    if new_status == "completed":
        output_payload = update_data.get("output_payload", job.output_payload)

        if not output_payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="output_payload is required when status is completed",
            )

        if not output_payload.get("filename"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="output_payload.filename is required",
            )

        if not output_payload.get("storage_path"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="output_payload.storage_path is required",
            )

    try:
        updated_job = update_image_job(
            db=db,
            db_job=job,
            update_data=update_data,
        )

        if updated_job.status == "completed":
            create_media_from_image_job_result(db=db, job=updated_job)

        return updated_job

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise