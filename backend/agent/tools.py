import os
import json

import httpx
from langchain_core.tools import tool

API_BASE = os.environ.get("INFEREVAL_API_BASE", "http://localhost:8014")


def _get(path: str, params: dict | None = None) -> str:
    resp = httpx.get(f"{API_BASE}{path}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.text


@tool(description="查询所有 GPU 芯片规格，包括芯片名称、算力、显存、带宽等参数")
def search_compute_specs() -> str:
    return _get("/api/v1/compute-specs")


@tool(description="查询所有 LLM 模型元数据，包括模型名称、架构、参数量等")
def search_models() -> str:
    return _get("/api/v1/models")


@tool(description="按条件搜索实验记录，可按模型ID、芯片ID、实验名称模糊搜索")
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


@tool(description="获取某个实验的完整详情，包含关联的芯片规格、模型信息和所有性能指标")
def get_experiment_detail(experiment_id: int) -> str:
    return _get(f"/api/v1/experiments/{experiment_id}")


@tool(description="对比多个实验的性能指标，输入实验ID列表，返回结构化对比数据")
def compare_experiments(experiment_ids: list[int]) -> str:
    rows = []
    for eid in experiment_ids:
        data = json.loads(_get(f"/api/v1/experiments/{eid}"))
        rows.append({
            "experiment_id": data["id"],
            "experiment_name": data.get("experiment_name"),
            "chip": data["compute_spec"]["chip_name"],
            "model": data["model"]["model_name"],
            "engine": f"{data['engine']} {data['engine_version']}",
            "deployment_precision": data["deployment_precision"],
            "resource_count": data["resource_count"],
            "isl": data["isl"],
            "osl": data["osl"],
            "concurrency": data["concurrency"],
            "result": data["result"],
        })
    return json.dumps(rows, ensure_ascii=False, indent=2)


@tool(description="调用 LLM 对指定实验生成文字化的性能对比总结")
def generate_summary(experiment_ids: list[int], focus: str | None = None) -> str:
    rows = []
    for eid in experiment_ids:
        data = json.loads(_get(f"/api/v1/experiments/{eid}"))
        rows.append(data)
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")
    client = __import__("openai").OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    focus_text = f"重点关注：{focus}" if focus else ""
    prompt = f"""请根据以下实验数据，用中文生成 2-5 条分条性能对比总结。按模型架构分组，以第一个实验的芯片为基准对比各芯片的吞吐和时延指标，最后给一条总结性结论。
{focus_text}

实验数据：
{json.dumps(rows, ensure_ascii=False, indent=2)}"""
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.25,
    )
    return resp.choices[0].message.content


TOOL_FUNCTIONS = {
    "search_compute_specs": search_compute_specs,
    "search_models": search_models,
    "search_experiments": search_experiments,
    "get_experiment_detail": get_experiment_detail,
    "compare_experiments": compare_experiments,
    "generate_summary": generate_summary,
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
    {
        "type": "function",
        "function": {
            "name": "compare_experiments",
            "description": "对比多个实验的性能指标。输入实验ID列表，返回结构化对比数据（吞吐、时延、显存等），自动生成对比表格。当用户要求对比/比较不同实验或芯片的性能时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiment_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "要对比的实验ID列表",
                    },
                },
                "required": ["experiment_ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_summary",
            "description": "调用 LLM 对指定实验生成文字化的性能对比总结（2-5条分条结论），包含吞吐对比、时延分析和总结性结论。当用户要求总结/分析实验性能时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiment_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "要总结的实验ID列表",
                    },
                    "focus": {
                        "type": "string",
                        "description": "用户关注的重点，如'吞吐量'、'时延'等，可选",
                    },
                },
                "required": ["experiment_ids"],
            },
        },
    },
]

LANGCHAIN_TOOLS = [search_compute_specs, search_models, search_experiments, get_experiment_detail, compare_experiments, generate_summary]
