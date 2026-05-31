import os
import json

import httpx

API_BASE = os.environ.get("INFEREVAL_API_BASE", "http://localhost:8014")


def _get(path: str, params: dict | None = None) -> str:
    resp = httpx.get(f"{API_BASE}{path}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.text


def search_compute_specs() -> str:
    return _get("/api/v1/compute-specs")


def search_models() -> str:
    return _get("/api/v1/models")


def search_experiments(
    model_id: int | None = None,
    compute_spec_id: int | None = None,
    experiment_name_q: str | None = None,
) -> str:
    params = {}
    if model_id is not None:
        params["model_id"] = model_id
    if compute_spec_id is not None:
        params["compute_spec_id"] = compute_spec_id
    if experiment_name_q is not None:
        params["experiment_name_q"] = experiment_name_q
    return _get("/api/v1/experiments", params=params)


def get_experiment_detail(experiment_id: int) -> str:
    return _get(f"/api/v1/experiments/{experiment_id}")


TOOL_FUNCTIONS = {
    "search_compute_specs": search_compute_specs,
    "search_models": search_models,
    "search_experiments": search_experiments,
    "get_experiment_detail": get_experiment_detail,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_compute_specs",
            "description": "查询所有 GPU 芯片规格，包括芯片名称、算力（FP32/TF32/FP16/FP8/FP4）、显存、带宽等参数",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_models",
            "description": "查询所有 LLM 模型元数据，包括模型名称、架构（Dense/MoE）、参数量等",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_experiments",
            "description": "按条件搜索实验记录，可按模型ID、芯片ID、实验名称模糊搜索。返回实验列表包含关联的芯片、模型和性能指标。",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_id": {
                        "type": "integer",
                        "description": "按模型ID筛选",
                    },
                    "compute_spec_id": {
                        "type": "integer",
                        "description": "按芯片ID筛选",
                    },
                    "experiment_name_q": {
                        "type": "string",
                        "description": "实验名称模糊搜索（忽略空格和大小写）",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_experiment_detail",
            "description": "获取某个实验的完整详情，包含关联的芯片规格、模型信息和所有性能指标（吞吐、时延、显存使用等）",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiment_id": {
                        "type": "integer",
                        "description": "实验ID",
                    },
                },
                "required": ["experiment_id"],
            },
        },
    },
]
