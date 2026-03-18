from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    nickname = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    prompt = Column(Text, nullable=False)
    plot_text = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="projects")
    images = relationship("GeneratedImage", back_populates="project", cascade="all, delete-orphan")
    videos = relationship("GeneratedVideo", back_populates="project", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="project")


class GeneratedImage(Base):
    __tablename__ = "generated_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(Text, nullable=False)
    prompt_used = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    project = relationship("Project", back_populates="images")


class GeneratedVideo(Base):
    __tablename__ = "generated_videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    video_url = Column(Text, nullable=False)
    duration = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    project = relationship("Project", back_populates="videos")


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    points = Column(Integer, nullable=False, default=0)
    reason = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="rewards")
    project = relationship("Project", back_populates="rewards")