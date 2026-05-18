# LLM 部署实验记录系统 - 设计文档

## 概述

一个轻量级的 Python Web 服务，用于管理大模型部署实验记录。提供模型、GPU 芯片和实验记录的 CRUD API。

## 技术栈

| 组件 | 选型 | 版本 |
|------|------|------|
| Web 框架 | FastAPI | 0.115+ |
| ORM | SQLAlchemy | 2.0+ |
| 数据库 | SQLite | 内置 |
| 数据验证 | Pydantic v2 | FastAPI 内置 |

## 项目结构

```
python/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI 应用入口
│   ├── database.py         # 数据库连接配置
│   ├── models.py           # SQLAlchemy ORM 模型
│   ├── schemas.py          # Pydantic 请求/响应模型
│   └── routers/
│       ├── __init__.py
│       ├── gpus.py         # GPU CRUD 接口
│       ├── models.py       # 模型 CRUD 接口
│       └── experiments.py  # 实验记录 CRUD 接口
├── requirements.txt
└── data/                   # SQLite 数据库文件目录
```

## 数据模型

### GPU 芯片 (GPU)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 自增主键 |
| name | String(100) | 芯片名称，如 "A100"、"H100" |
| manufacturer | String(100) | 厂商，如 "NVIDIA"、"AMD" |
| memory_gb | Integer | 显存大小（GB） |
| created_at | DateTime | 创建时间 |

### 模型 (Model)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 自增主键 |
| name | String(200) | 模型名称，如 "LLaMA-3-70B" |
| provider | String(100) | 提供方，如 "Meta"、"OpenAI" |
| parameter_size | String(50) | 参数量，如 "70B"、"175B" |
| description | Text | 模型描述 |
| created_at | DateTime | 创建时间 |

### 实验记录 (Experiment)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 自增主键 |
| model_id | Integer (FK) | 关联模型 |
| gpu_id | Integer (FK) | 关联 GPU |
| status | String(20) | 状态：pending / running / completed / failed |
| config | JSON | 实验配置（量化方式、batch_size 等） |
| metrics | JSON | 实验结果指标（吞吐量、延迟、显存占用等） |
| notes | Text | 备注信息 |
| started_at | DateTime (nullable) | 开始时间 |
| finished_at | DateTime (nullable) | 结束时间 |
| created_at | DateTime | 创建时间 |

**外键约束：** model_id → Model.id, gpu_id → GPU.id。删除 Model 或 GPU 时不级联删除关联的 Experiment（RESTRICT），保留历史记录。

## API 接口

### 通用分页

列表接口统一支持 `skip`（默认 0）和 `limit`（默认 20）参数。

### GPU 芯片 `/api/gpus`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /api/gpus | GPU 列表 | - | `{items: [...], total: int}` |
| POST | /api/gpus | 创建 GPU | GPUCreate | GPUResponse |
| GET | /api/gpus/{id} | GPU 详情 | - | GPUResponse |
| PUT | /api/gpus/{id} | 更新 GPU | GPUUpdate | GPUResponse |
| DELETE | /api/gpus/{id} | 删除 GPU | - | `{message: "deleted"}` |

### 模型 `/api/models`

与 GPU 相同的 CRUD 结构，使用 ModelCreate / ModelUpdate / ModelResponse。

### 实验记录 `/api/experiments`

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /api/experiments | 实验列表 | - | `{items: [...], total: int}` |
| POST | /api/experiments | 创建实验 | ExperimentCreate | ExperimentResponse |
| GET | /api/experiments/{id} | 实验详情 | - | ExperimentResponse |
| PUT | /api/experiments/{id} | 更新实验 | ExperimentUpdate | ExperimentResponse |
| DELETE | /api/experiments/{id} | 删除实验 | - | `{message: "deleted"}` |

**额外筛选参数：**
- `status` — 按状态筛选（pending/running/completed/failed）
- `model_id` — 按模型筛选
- `gpu_id` — 按 GPU 筛选

实验列表和详情接口中，model 和 gpu 信息以嵌套对象形式返回（而非仅返回 id）。

## 错误处理

- 404：资源不存在时返回 `{detail: "xxx not found"}`
- 422：请求体校验失败时由 FastAPI/Pydantic 自动处理
- 删除 GPU/Model 时，若有关联 Experiment 则返回 400 错误提示

## 无认证

本系统为纯内部工具，不设认证机制。
