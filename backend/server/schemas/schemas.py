from datetime import datetime

from pydantic import BaseModel, ConfigDict


# --- ComputeSpec ---

class ComputeSpecBase(BaseModel):
    chip_name: str
    fp32_tflops: float
    tf32_tflops: float
    fp16_tflops: float
    fp8_tflops: float
    fp4_tflops: float
    interconnect_bandwidth: float
    memory_gb: float
    memory_bandwidth_tbs: float
    remarks: str | None = None
    updated_by: str


class ComputeSpecCreate(ComputeSpecBase):
    pass


class ComputeSpecUpdate(BaseModel):
    chip_name: str | None = None
    fp32_tflops: float | None = None
    tf32_tflops: float | None = None
    fp16_tflops: float | None = None
    fp8_tflops: float | None = None
    fp4_tflops: float | None = None
    interconnect_bandwidth: float | None = None
    memory_gb: float | None = None
    memory_bandwidth_tbs: float | None = None
    remarks: str | None = None
    updated_by: str | None = None


class ComputeSpec(ComputeSpecBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: datetime | None = None


# --- ModelMetadata ---

class ModelMetadataBase(BaseModel):
    model_name: str
    architecture: str
    model_type: str = "LLM"
    parameters_count: str
    active_parameters_count: str
    lpai_link: str | None = None
    updated_by: str | None = "admin"


class ModelMetadataCreate(ModelMetadataBase):
    pass


class ModelMetadataUpdate(BaseModel):
    model_name: str | None = None
    architecture: str | None = None
    model_type: str | None = None
    parameters_count: str | None = None
    active_parameters_count: str | None = None
    lpai_link: str | None = None
    updated_by: str | None = None


class ModelMetadata(ModelMetadataBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: datetime | None = None


# --- ExperimentResult ---

class ExperimentResultBase(BaseModel):
    actual_request_rate: float
    max_request_concurrency: int
    successful_requests: int
    duration_s: float
    total_input_tokens: int
    total_generated_tokens: int
    request_throughput_reqs: float
    input_token_throughput_toks: float
    output_token_throughput_toks: float
    total_token_throughput_toks: float
    actual_concurrency: float
    goodput_reqs: float | None = None
    e2e_mean_ms: float
    e2e_median_ms: float
    e2e_p95_ms: float | None = None
    e2e_p99_ms: float | None = None
    ttft_mean_ms: float
    ttft_median_ms: float
    ttft_p95_ms: float | None = None
    ttft_p99_ms: float | None = None
    itl_mean_ms: float
    itl_median_ms: float
    itl_p95_ms: float | None = None
    itl_p99_ms: float | None = None
    itl_max_ms: float | None = None
    tpot_mean_ms: float | None = None
    tpot_median_ms: float | None = None
    tpot_p95_ms: float | None = None
    tpot_p99_ms: float | None = None
    peak_memory_usage_pct: float | None = None
    avg_memory_usage_pct: float | None = None
    peak_tensor_core_usage_pct: float | None = None
    avg_tensor_core_usage_pct: float | None = None


class ExperimentResultCreate(ExperimentResultBase):
    pass


class ExperimentResultUpdate(BaseModel):
    actual_request_rate: float | None = None
    max_request_concurrency: int | None = None
    successful_requests: int | None = None
    duration_s: float | None = None
    total_input_tokens: int | None = None
    total_generated_tokens: int | None = None
    request_throughput_reqs: float | None = None
    input_token_throughput_toks: float | None = None
    output_token_throughput_toks: float | None = None
    total_token_throughput_toks: float | None = None
    actual_concurrency: float | None = None
    goodput_reqs: float | None = None
    e2e_mean_ms: float | None = None
    e2e_median_ms: float | None = None
    e2e_p95_ms: float | None = None
    e2e_p99_ms: float | None = None
    ttft_mean_ms: float | None = None
    ttft_median_ms: float | None = None
    ttft_p95_ms: float | None = None
    ttft_p99_ms: float | None = None
    itl_mean_ms: float | None = None
    itl_median_ms: float | None = None
    itl_p95_ms: float | None = None
    itl_p99_ms: float | None = None
    itl_max_ms: float | None = None
    tpot_mean_ms: float | None = None
    tpot_median_ms: float | None = None
    tpot_p95_ms: float | None = None
    tpot_p99_ms: float | None = None
    peak_memory_usage_pct: float | None = None
    avg_memory_usage_pct: float | None = None
    peak_tensor_core_usage_pct: float | None = None
    avg_tensor_core_usage_pct: float | None = None


class ExperimentResult(ExperimentResultBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# --- Experiment ---

class ExperimentBase(BaseModel):
    compute_spec_id: int
    model_id: int
    engine: str
    engine_version: str
    deployment_precision: str
    isl: int
    osl: int
    request_rate: float
    total_requests: int
    concurrency: int
    deploy_param: str | None = None
    resource_count: int
    goodput_threshold: str | None = None
    lpai_link: str | None = None
    remarks: str | None = None
    updated_by: str | None = "admin"


class ExperimentCreate(BaseModel):
    experiment_name: str | None = None
    compute_spec_id: int
    model_id: int
    engine: str
    engine_version: str
    deployment_precision: str
    isl: int
    osl: int
    request_rate: float
    total_requests: int
    concurrency: int
    deploy_param: str | None = None
    resource_count: int
    goodput_threshold: str | None = None
    lpai_link: str | None = None
    remarks: str | None = None
    updated_by: str | None = "admin"
    result: ExperimentResultCreate


class ExperimentUpdate(BaseModel):
    experiment_name: str | None = None
    compute_spec_id: int | None = None
    model_id: int | None = None
    engine: str | None = None
    engine_version: str | None = None
    deployment_precision: str | None = None
    isl: int | None = None
    osl: int | None = None
    request_rate: float | None = None
    total_requests: int | None = None
    concurrency: int | None = None
    deploy_param: str | None = None
    resource_count: int | None = None
    goodput_threshold: str | None = None
    lpai_link: str | None = None
    remarks: str | None = None
    updated_by: str | None = None
    result: ExperimentResultUpdate | None = None


class Experiment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    experiment_name: str | None = None
    compute_spec_id: int
    model_id: int
    result_id: int
    engine: str
    engine_version: str
    deployment_precision: str
    isl: int
    osl: int
    request_rate: float
    total_requests: int
    concurrency: int
    deploy_param: str | None = None
    resource_count: int
    goodput_threshold: str | None = None
    lpai_link: str | None = None
    remarks: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None
    compute_spec: ComputeSpec
    model: ModelMetadata
    result: ExperimentResult


class ExperimentSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    experiment_name: str | None = None
    compute_spec_id: int
    model_id: int
    result_id: int
    engine: str
    engine_version: str
    deployment_precision: str
    isl: int
    osl: int
    request_rate: float
    total_requests: int
    concurrency: int
    deploy_param: str | None = None
    resource_count: int
    goodput_threshold: str | None = None
    lpai_link: str | None = None
    remarks: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None
