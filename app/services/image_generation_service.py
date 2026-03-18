from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.crud.image_job import (
    create_image_job,
    update_image_job_output,
    update_image_job_status,
)
from app.crud.media import create_media
from app.schemas.media import MediaCreate
from app.services.comfyui.client import ComfyUIClient
from app.services.comfyui.workflow_builder import build_text_to_image_workflow
from app.services.storage.factory import get_storage_service


class ImageGenerationService:
    def __init__(self) -> None:
        self.comfy_client = ComfyUIClient()
        self.storage = get_storage_service()

    def generate_image(
        self,
        db: Session,
        *,
        user_id: UUID,
        project_id: UUID,
        prompt: str,
        negative_prompt: str | None,
        width: int,
        height: int,
    ):
        job = create_image_job(
            db,
            user_id=user_id,
            project_id=project_id,
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
        )

        try:
            update_image_job_status(
                db,
                job=job,
                status="processing",
                started_at=datetime.utcnow(),
            )

            workflow = build_text_to_image_workflow(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
            )

            prompt_id = self.comfy_client.submit_workflow(workflow)
            result = self.comfy_client.wait_until_done(prompt_id)

            outputs = result.get("outputs", {})
            saved_images = []

            for node_output in outputs.values():
                images = node_output.get("images", [])
                saved_images.extend(images)

            if not saved_images:
                raise RuntimeError("No generated image returned from ComfyUI")

            first_image = saved_images[0]

            image_bytes = self.comfy_client.download_image(
                filename=first_image["filename"],
                subfolder=first_image.get("subfolder", ""),
                folder_type=first_image.get("type", "output"),
            )

            filename = f"{uuid4()}.png"
            relative_path = f"images/{project_id}/{filename}"

            saved = self.storage.save_file(
                data=image_bytes,
                relative_path=relative_path,
            )

            media = create_media(
                db=db,
                media_in=MediaCreate(
                    user_id=user_id,
                    project_id=project_id,
                    job_id=job.id,
                    media_type="image",
                    origin_type="generated",
                    filename=filename,
                    original_filename=first_image.get("filename"),
                    content_type="image/png",
                    size_bytes=saved["size_bytes"],
                    storage_provider=saved["storage_provider"],
                    storage_path=saved["storage_path"],
                    public_url=saved["public_url"],
                    thumbnail_url=None,
                    status="active",
                    width=width,
                    height=height,
                    duration_seconds=None,
                    prompt_text=prompt,
                    error_message=None,
                ),
            )

            update_image_job_output(
                db,
                job=job,
                output_payload={
                    "prompt_id": prompt_id,
                    "media_id": str(media.id),
                    "filename": filename,
                    "public_url": media.public_url,
                },
            )

            update_image_job_status(
                db,
                job=job,
                status="completed",
                completed_at=datetime.utcnow(),
            )

            return job

        except Exception as e:
            update_image_job_status(
                db,
                job=job,
                status="failed",
                error_message=str(e),
                completed_at=datetime.utcnow(),
            )
            raise
