from datetime import datetime
from typing import Union

from pydantic import BaseModel, ConfigDict


# --- GPU ---

class GPUCreate(BaseModel):
    name: str
    manufacturer: str
    memory_gb: int


class GPUUpdate(BaseModel):
    name: Union[str, None] = None
    manufacturer: Union[str, None] = None
    memory_gb: Union[int, None] = None


class GPUResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    manufacturer: str
    memory_gb: int
    created_at: datetime


# --- Model ---

class ModelCreate(BaseModel):
    name: str
    provider: str
    parameter_size: str
    description: Union[str, None] = None


class ModelUpdate(BaseModel):
    name: Union[str, None] = None
    provider: Union[str, None] = None
    parameter_size: Union[str, None] = None
    description: Union[str, None] = None


class ModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    provider: str
    parameter_size: str
    description: Union[str, None]
    created_at: datetime


# --- Experiment ---

class ExperimentCreate(BaseModel):
    model_id: int
    gpu_id: int
    status: str = "pending"
    config: Union[dict, None] = None
    metrics: Union[dict, None] = None
    notes: Union[str, None] = None
    started_at: Union[datetime, None] = None
    finished_at: Union[datetime, None] = None


class ExperimentUpdate(BaseModel):
    model_id: Union[int, None] = None
    gpu_id: Union[int, None] = None
    status: Union[str, None] = None
    config: Union[dict, None] = None
    metrics: Union[dict, None] = None
    notes: Union[str, None] = None
    started_at: Union[datetime, None] = None
    finished_at: Union[datetime, None] = None


class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: int
    gpu_id: int
    status: str
    config: Union[dict, None]
    metrics: Union[dict, None]
    notes: Union[str, None]
    started_at: Union[datetime, None]
    finished_at: Union[datetime, None]
    created_at: datetime
    model: ModelResponse
    gpu: GPUResponse


# --- Pagination ---

class PaginatedResponse(BaseModel):
    items: list
    total: int