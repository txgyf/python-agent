from datetime import datetime, timezone
from typing import Union

from sqlalchemy import String, Integer, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GPU(Base):
    __tablename__ = "gpus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    memory_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class Model(Base):
    __tablename__ = "models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    parameter_size: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Union[str, None]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("models.id", ondelete="RESTRICT"), nullable=False
    )
    gpu_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("gpus.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    config: Mapped[Union[dict, None]] = mapped_column(JSON, nullable=True)
    metrics: Mapped[Union[dict, None]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Union[str, None]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Union[datetime, None]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Union[datetime, None]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    model: Mapped[Model] = relationship("Model", lazy="selectin")
    gpu: Mapped[GPU] = relationship("GPU", lazy="selectin")