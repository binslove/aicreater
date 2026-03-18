from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import MediaAsset, MediaStat
from app.schemas.media import MediaCreate, MediaUpdate


def create_media(db: Session, media_in: MediaCreate) -> MediaAsset:
    media = MediaAsset(**media_in.model_dump())
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


def get_media_by_id(db: Session, media_id: UUID) -> MediaAsset | None:
    stmt = select(MediaAsset).where(
        MediaAsset.id == media_id,
        MediaAsset.deleted_at.is_(None),
    )
    return db.scalar(stmt)


def get_media_list_by_project(
    db: Session,
    project_id: UUID,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[MediaAsset], int]:
    conditions = [
        MediaAsset.project_id == project_id,
        MediaAsset.deleted_at.is_(None),
    ]

    total_stmt = select(func.count()).select_from(MediaAsset).where(*conditions)
    total = db.scalar(total_stmt) or 0

    stmt = (
        select(MediaAsset)
        .where(*conditions)
        .order_by(MediaAsset.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    items = list(db.scalars(stmt).all())

    return items, total


def update_media(
    db: Session,
    media: MediaAsset,
    media_in: MediaUpdate,
) -> MediaAsset:
    update_data = media_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(media, field, value)

    db.add(media)
    db.commit()
    db.refresh(media)
    return media


def get_media_stats(db: Session, media_asset_id: UUID) -> MediaStat | None:
    stmt = select(MediaStat).where(MediaStat.media_asset_id == media_asset_id)
    return db.scalar(stmt)


def ensure_media_stats(db: Session, media_asset_id: UUID) -> MediaStat:
    stmt = select(MediaStat).where(MediaStat.media_asset_id == media_asset_id)
    stats = db.scalar(stmt)

    if stats is None:
        stats = MediaStat(
            media_asset_id=media_asset_id,
            view_count=0,
            like_count=0,
            comment_count=0,
            bookmark_count=0,
        )
        db.add(stats)
        db.flush()

    return stats


def increment_media_view_count(db: Session, media_asset_id: UUID) -> MediaStat:
    stats = ensure_media_stats(db=db, media_asset_id=media_asset_id)
    stats.view_count += 1
    db.add(stats)
    db.commit()
    db.refresh(stats)
    return stats


def increment_media_like_count(db: Session, media_asset_id: UUID) -> MediaStat:
    stats = ensure_media_stats(db=db, media_asset_id=media_asset_id)
    stats.like_count += 1
    db.add(stats)
    db.commit()
    db.refresh(stats)
    return stats


def decrement_media_like_count(db: Session, media_asset_id: UUID) -> MediaStat:
    stats = ensure_media_stats(db=db, media_asset_id=media_asset_id)
    if stats.like_count > 0:
        stats.like_count -= 1
    db.add(stats)
    db.commit()
    db.refresh(stats)
    return stats


def increment_media_comment_count(db: Session, media_asset_id: UUID) -> MediaStat:
    stats = ensure_media_stats(db=db, media_asset_id=media_asset_id)
    stats.comment_count += 1
    db.add(stats)
    db.commit()
    db.refresh(stats)
    return stats


def decrement_media_comment_count(db: Session, media_asset_id: UUID) -> MediaStat:
    stats = ensure_media_stats(db=db, media_asset_id=media_asset_id)
    if stats.comment_count > 0:
        stats.comment_count -= 1
    db.add(stats)
    db.commit()
    db.refresh(stats)
    return stats
