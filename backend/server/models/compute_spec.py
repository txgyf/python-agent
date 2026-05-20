from datetime import datetime, timezone

from sqlalchemy import Float, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from server.db.base_class import Base


class ComputeSpec(Base):
    __tablename__ = "compute_specs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chip_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    fp32_tflops: Mapped[float] = mapped_column(Float, nullable=False)
    tf32_tflops: Mapped[float] = mapped_column(Float, nullable=False)
    fp16_tflops: Mapped[float] = mapped_column(Float, nullable=False)
    fp8_tflops: Mapped[float] = mapped_column(Float, nullable=False)
    fp4_tflops: Mapped[float] = mapped_column(Float, nullable=False)
    interconnect_bandwidth: Mapped[float] = mapped_column(Float, nullable=False)
    memory_gb: Mapped[float] = mapped_column(Float, nullable=False)
    memory_bandwidth_tbs: Mapped[float] = mapped_column(Float, nullable=False)
    remarks: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    updated_by: Mapped[str] = mapped_column(String, nullable=False)
