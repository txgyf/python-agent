# InfereVal - LLM 推理性能评估平台

LLM 推理性能评估平台的 RESTful 后端 API，用于管理推理基准测试的芯片规格、模型元数据和实验数据。

## 技术栈

- Python 3.10+ / FastAPI
- SQLAlchemy 2.x + SQLite
- Pydantic v2
- pytest

## 快速开始

```bash
# 一键启动（自动创建虚拟环境、安装依赖、启动服务）
./start.sh

# 或手动启动
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn server.main:app --host 0.0.0.0 --port 8014 --reload
```

服务启动后访问 http://localhost:8014/docs 查看 Swagger 文档。

## 种子数据

```bash
cd backend
source .venv/bin/activate
python seed.py
```

## 运行测试

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```

## API 端点

| 模块 | 路径 | 说明 |
|------|------|------|
| 芯片规格 | `/api/v1/compute-specs` | GPU/加速卡硬件参数 CRUD + 批量创建 |
| 模型元数据 | `/api/v1/models` | LLM 模型信息 CRUD + 批量创建 |
| 实验记录 | `/api/v1/experiments` | 推理基准测试 CRUD + 批量创建 + 筛选 |

### 实验筛选参数

GET `/api/v1/experiments` 支持 `model_id`、`compute_spec_id`、`experiment_name_q`（模糊搜索）筛选，响应 header 包含 `X-Total-Count`。

## 项目结构

```
backend/
├── server/
│   ├── main.py              # FastAPI 应用入口
│   ├── api/api_v1.py        # API 路由
│   ├── crud/crud.py         # 数据库操作
│   ├── db/                  # 数据库配置
│   ├── models/              # SQLAlchemy 模型
│   ├── schemas/schemas.py   # Pydantic 数据验证
│   └── services/            # 业务逻辑（自动命名等）
├── tests/                   # 测试用例
├── seed.py                  # 种子数据脚本
└── requirements.txt
```
