from sqlalchemy import Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from server.db.base_class import Base


class ExperimentResult(Base):
    __tablename__ = "experiment_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actual_request_rate: Mapped[float] = mapped_column(Float, nullable=False)
    max_request_concurrency: Mapped[int] = mapped_column(Integer, nullable=False)
    successful_requests: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_s: Mapped[float] = mapped_column(Float, nullable=False)
    total_input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    total_generated_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    request_throughput_reqs: Mapped[float] = mapped_column(Float, nullable=False)
    input_token_throughput_toks: Mapped[float] = mapped_column(Float, nullable=False)
    output_token_throughput_toks: Mapped[float] = mapped_column(Float, nullable=False)
    total_token_throughput_toks: Mapped[float] = mapped_column(Float, nullable=False)
    actual_concurrency: Mapped[float] = mapped_column(Float, nullable=False)
    goodput_reqs: Mapped[float | None] = mapped_column(Float, nullable=True)
    e2e_mean_ms: Mapped[float] = mapped_column(Float, nullable=False)
    e2e_median_ms: Mapped[float] = mapped_column(Float, nullable=False)
    e2e_p95_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    e2e_p99_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    ttft_mean_ms: Mapped[float] = mapped_column(Float, nullable=False)
    ttft_median_ms: Mapped[float] = mapped_column(Float, nullable=False)
    ttft_p95_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    ttft_p99_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    itl_mean_ms: Mapped[float] = mapped_column(Float, nullable=False)
    itl_median_ms: Mapped[float] = mapped_column(Float, nullable=False)
    itl_p95_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    itl_p99_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    itl_max_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    tpot_mean_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    tpot_median_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    tpot_p95_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    tpot_p99_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    peak_memory_usage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_memory_usage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    peak_tensor_core_usage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_tensor_core_usage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
