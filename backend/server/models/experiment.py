from datetime import datetime, timezone

from sqlalchemy import Float, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.db.base_class import Base


class Experiment(Base):
    __tablename__ = "experiments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    compute_spec_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("compute_specs.id", ondelete="CASCADE"), nullable=False
    )
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("model_metadata.id", ondelete="CASCADE"), nullable=False
    )
    result_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("experiment_results.id", ondelete="CASCADE"), nullable=False
    )
    engine: Mapped[str] = mapped_column(String, nullable=False)
    engine_version: Mapped[str] = mapped_column(String, nullable=False)
    deployment_precision: Mapped[str] = mapped_column(String, nullable=False)
    isl: Mapped[int] = mapped_column(Integer, nullable=False)
    osl: Mapped[int] = mapped_column(Integer, nullable=False)
    request_rate: Mapped[float] = mapped_column(Float, nullable=False)
    total_requests: Mapped[int] = mapped_column(Integer, nullable=False)
    concurrency: Mapped[int] = mapped_column(Integer, nullable=False)
    deploy_param: Mapped[str | None] = mapped_column(String, nullable=True)
    resource_count: Mapped[int] = mapped_column(Integer, nullable=False)
    goodput_threshold: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lpai_link: Mapped[str | None] = mapped_column(String, nullable=True)
    remarks: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    updated_by: Mapped[str | None] = mapped_column(String, nullable=True, default="admin")

    compute_spec: Mapped["ComputeSpec"] = relationship("ComputeSpec", lazy="selectin")
    model: Mapped["ModelMetadata"] = relationship("ModelMetadata", lazy="selectin")
    result: Mapped["ExperimentResult"] = relationship("ExperimentResult", lazy="selectin")
