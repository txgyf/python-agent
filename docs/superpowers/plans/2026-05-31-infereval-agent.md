# InfereVal Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI-based AI Agent that answers natural language questions about GPU chips, models, and experiments by calling the InfereVal backend API via DeepSeek's function calling.

**Architecture:** Agent uses DeepSeek API with OpenAI-compatible SDK. Four query tools call the existing `/api/v1/*` endpoints via httpx. Agent core is decoupled from CLI so it can be reused for Feishu bot later.

**Tech Stack:** Python 3.10+, openai SDK, httpx, DeepSeek API (deepseek-v4-pro)

---

## File Structure

```
backend/agent/
├── __init__.py          # Package init
├── tools.py             # Query tool functions + OpenAI tool schemas
├── agent.py             # Agent core: DeepSeek client + tool dispatch + chat()
└── cli.py               # CLI entry point
```

- Modify: `backend/requirements.txt` — add openai dependency

---

### Task 1: Add openai dependency

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Add openai to requirements.txt**

Add to end of `backend/requirements.txt`:
```
openai>=1.0.0
```

- [ ] **Step 2: Install and verify**

```bash
cd /Users/guanyifan/Desktop/project/python-agent/backend
source .venv/bin/activate
pip install openai -q
python -c "import openai; print('ok')"
```
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add backend/requirements.txt
git commit -m "feat: add openai dependency for InfereVal Agent"
```

---

### Task 2: Create agent package + query tools

**Files:**
- Create: `backend/agent/__init__.py`
- Create: `backend/agent/tools.py`

- [ ] **Step 1: Create agent package**

```bash
mkdir -p /Users/guanyifan/Desktop/project/python-agent/backend/agent
touch /Users/guanyifan/Desktop/project/python-agent/backend/agent/__init__.py
```

- [ ] **Step 2: Write tools.py**

Create `backend/agent/tools.py`:
```python
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
```

- [ ] **Step 3: Commit**

```bash
git add backend/agent/
git commit -m "feat: add Agent query tools with OpenAI function calling schemas"
```

---

### Task 3: Agent core

**Files:**
- Create: `backend/agent/agent.py`

- [ ] **Step 1: Write agent.py**

Create `backend/agent/agent.py`:
```python
import os

from openai import OpenAI

from agent.tools import TOOL_FUNCTIONS, TOOLS_SCHEMA

SYSTEM_PROMPT = """你是 InfereVal 平台的数据查询助手。用户会问你关于 GPU 芯片、LLM 模型和推理性能实验的问题。

规则：
- 用中文回答，简洁准确
- 基于工具返回的实际数据回答，不要编造数据
- 如果数据为空或没有匹配结果，直接告诉用户没有找到
- 涉及性能对比时，用表格或列表清晰展示关键指标
- 可以主动对比不同芯片或模型的表现"""


class InfereValAgent:
    def __init__(self):
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")
        model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.model = model
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def chat(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})
        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
            )
            choice = response.choices[0]
            if choice.finish_reason == "tool_calls":
                for tool_call in choice.message.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = {}
                    if tool_call.function.arguments:
                        import json
                        fn_args = json.loads(tool_call.function.arguments)
                    fn = TOOL_FUNCTIONS[fn_name]
                    result = fn(**fn_args)
                    self.messages.append(choice.message)
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
                continue
            else:
                self.messages.append(choice.message)
                return choice.message.content

    def reset(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
```

- [ ] **Step 2: Commit**

```bash
git add backend/agent/agent.py
git commit -m "feat: add InfereVal Agent core with DeepSeek tool calling"
```

---

### Task 4: CLI entry point

**Files:**
- Create: `backend/agent/cli.py`

- [ ] **Step 1: Write cli.py**

Create `backend/agent/cli.py`:
```python
from agent.agent import InfereValAgent


def main():
    try:
        agent = InfereValAgent()
    except ValueError as e:
        print(f"错误: {e}")
        print("请设置环境变量: export DEEPSEEK_API_KEY=你的key")
        return

    print("InfereVal Agent 已启动（输入 quit 退出，reset 重置对话）")
    print()

    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("再见！")
            break
        if user_input.lower() == "reset":
            agent.reset()
            print("对话已重置。\n")
            continue

        try:
            response = agent.chat(user_input)
            print(f"\nAgent: {response}\n")
        except Exception as e:
            print(f"\n出错了: {e}\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test CLI launches (requires backend running + API key)**

```bash
cd /Users/guanyifan/Desktop/project/python-agent/backend
source .venv/bin/activate
python -m agent.cli
```
Expected: Prints "InfereVal Agent 已启动" or shows API key error message

- [ ] **Step 3: Commit**

```bash
git add backend/agent/cli.py
git commit -m "feat: add CLI entry point for InfereVal Agent"
```

---

### Task 5: End-to-end verification

- [ ] **Step 1: Ensure backend is running with seed data**

```bash
cd /Users/guanyifan/Desktop/project/python-agent/backend
source .venv/bin/activate
python seed.py
python -m uvicorn server.main:app --host 0.0.0.0 --port 8014 &
```

- [ ] **Step 2: Test Agent with a question**

```bash
DEEPSEEK_API_KEY=你的key python -m agent.cli
```

Test questions to try:
1. "有哪些GPU芯片？"
2. "有关于Llama模型的实验吗？"
3. "H800上跑了哪些实验，性能怎么样？"

Expected: Agent calls the appropriate tools and returns data-based answers in Chinese.

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete InfereVal Agent with CLI interface"
```
