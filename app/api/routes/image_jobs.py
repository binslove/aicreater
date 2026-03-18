from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.image_job import get_image_job_by_id
from app.crud.project import get_project_by_id
from app.db.database import get_db
from app.schemas.image_job import ImageJobCreate, ImageJobRead
from app.services.image_generation_service import ImageGenerationService

router = APIRouter(prefix="/image-jobs", tags=["image-jobs"])


@router.post("", response_model=ImageJobRead, status_code=status.HTTP_201_CREATED)
def create_image_job_endpoint(
    payload: ImageJobCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ImageJobRead:
    project = get_project_by_id(db=db, project_id=payload.project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    service = ImageGenerationService()
    job = service.generate_image(
        db=db,
        user_id=current_user.id,
        project_id=payload.project_id,
        prompt=payload.prompt,
        negative_prompt=payload.negative_prompt,
        width=payload.width,
        height=payload.height,
    )
    return job


@router.get("/{job_id}", response_model=ImageJobRead)
def get_image_job_endpoint(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ImageJobRead:
    job = get_image_job_by_id(db=db, job_id=job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image job not found",
        )

    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    return job
