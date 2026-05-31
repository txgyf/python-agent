# InfereVal Agent 设计文档

## 背景

在 InfereVal 平台基础上搭建 AI Agent，用自然语言回答关于 GPU 芯片、模型和实验记录的问题。先做 CLI 版本，后续接入飞书机器人。使用 DeepSeek 作为 LLM。

## 方案

**Tool Calling Agent**：利用 DeepSeek 的 function calling 能力，定义查询工具调后端 API 获取数据，LLM 自动选择工具并组织回答。

## 架构

```
用户提问 → Agent（DeepSeek + Tool Calling）
              ↓ 判断需要调用哪个工具
         httpx 调后端 API（/api/v1/*）
              ↓ 拿到 JSON 数据
         LLM 综合整理 → 返回自然语言回答
```

Agent 与后端完全解耦，通过 HTTP API 通信。使用前需先启动后端服务。

## 目录结构

```
backend/agent/
├── __init__.py
├── agent.py      # Agent 核心：DeepSeek 客户端 + 工具调度 + 多轮对话
├── tools.py      # 查询工具函数 + OpenAI 格式的工具描述 schema
└── cli.py        # CLI 入口（终端交互循环）
```

## 核心接口

`agent.chat(message: str) -> str` — 所有界面（CLI、飞书）统一调用这个方法。

## 查询工具

| 工具                    | 调用的 API                     | 参数                                                         | 用途                                             |
| ----------------------- | ------------------------------ | ------------------------------------------------------------ | ------------------------------------------------ |
| `search_compute_specs`  | `GET /api/v1/compute-specs`    | 无                                                           | 查询所有 GPU 芯片及参数                          |
| `search_models`         | `GET /api/v1/models`           | 无                                                           | 查询所有模型元数据                               |
| `search_experiments`    | `GET /api/v1/experiments`      | `model_id`, `compute_spec_id`, `experiment_name_q`（均可选） | 按条件查实验                                     |
| `get_experiment_detail` | `GET /api/v1/experiments/{id}` | `experiment_id`                                              | 查某个实验的完整结果（含嵌套的芯片、模型、指标） |

每个工具内部用 `httpx` 调后端 API，返回 JSON 供 LLM 理解。

## Agent 核心（agent.py）

1. 初始化 DeepSeek 客户端（`base_url=https://api.deepseek.com`，模型 `deepseek-v4-pro`，用 `openai` SDK）
2. 注册工具函数和 function calling schema
3. `chat(message)` 流程：
   - 用户消息加入对话历史
   - 调用 DeepSeek API，传入 tools 定义
   - 若 LLM 返回 tool_calls → 执行对应工具 → 结果喂回 LLM → 继续
   - 直到 LLM 返回最终文本回答
4. 支持多轮对话（保留 messages 历史）

## CLI（cli.py）

- 终端交互循环：读取输入 → `agent.chat()` → 打印回答
- 输入 `quit` 退出
- 启动命令：`cd backend && python -m agent.cli`

## 环境变量

| 变量                 | 说明                     | 默认值                  |
| -------------------- | ------------------------ | ----------------------- |
| `DEEPSEEK_API_KEY`   | DeepSeek API Key（必填） | —                       |
| `DEEPSEEK_MODEL`     | 模型名                   | `deepseek-v4-pro`         |
| `INFEREVAL_API_BASE` | 后端 API 地址            | `http://localhost:8014` |

## 新增依赖

在 `backend/requirements.txt` 加：

```
openai>=1.0.0
```

## 系统提示词

Agent 的 system prompt 指定角色为 InfereVal 平台的数据查询助手，用中文回答，回答要简洁准确，基于工具返回的实际数据而非编造。

## 验证方式

1. 启动后端：`./start.sh`
2. 启动 Agent：`cd backend && DEEPSEEK_API_KEY=xxx python -m agent.cli`
3. 测试问题：
   - "有哪些GPU芯片？"
   - "有关于Llama模型的实验吗？"
   - "H800上跑了哪些实验，性能怎么样？"

## 后续扩展

Agent 核心逻辑与界面解耦，`chat(message)` 接口可直接复用于：

- 飞书机器人 → 接收飞书消息 → `agent.chat()` → 回复到飞书
- Web 聊天界面 → 同理
