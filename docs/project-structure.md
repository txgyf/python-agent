# 项目结构与阅读指南

## 目录结构

```
python-agent/
├── README.md                    ← 项目说明
├── start.sh                     ← 一键启动脚本
├── Dockerfile                   ← Docker 镜像配置（部署用）
├── docker-compose.yml           ← Docker 编排（部署用）
├── .gitignore                   ← Git 忽略规则
│
└── backend/                     ← 核心代码
    ├── requirements.txt         ← Python 依赖列表
    ├── seed.py                  ← 往数据库灌示例数据的脚本
    ├── alembic.ini              ← 数据库迁移配置（预留）
    ├── alembic/.gitkeep         ← 空目录占位
    │
    ├── server/
    │   ├── main.py              ← 入口文件，FastAPI 应用从这里启动
    │   │
    │   ├── db/                  ← 数据库配置层
    │   │   ├── base_class.py    ←   SQLAlchemy Base 类定义
    │   │   ├── base.py          ←   导入所有模型（供框架发现）
    │   │   └── session.py       ←   数据库连接 + get_db 依赖注入
    │   │
    │   ├── models/              ← 数据库表结构（ORM 模型）
    │   │   ├── compute_spec.py       芯片规格表（GPU 参数）
    │   │   ├── model_metadata.py     模型元数据表（LLM 模型信息）
    │   │   ├── experiment_result.py  实验结果表（性能指标）
    │   │   └── experiment.py         实验表（关联上面三张表）
    │   │
    │   ├── schemas/             ← 数据验证层（Pydantic）
    │   │   └── schemas.py       ←   请求/响应的数据格式定义
    │   │
    │   ├── crud/                ← 数据库操作层
    │   │   └── crud.py          ←   增删改查函数
    │   │
    │   ├── api/                 ← API 路由层
    │   │   └── api_v1.py        ←   所有 /api/v1/* 的端点定义
    │   │
    │   └── services/            ← 业务逻辑层
    │       └── experiment_naming.py  实验自动命名逻辑
    │
    └── tests/                   ← 测试
        ├── conftest.py          ←   测试配置和 fixtures
        └── test_api.py          ←   27 个 API 测试
```

## 阅读顺序

1. `README.md` — 了解项目是干什么的
2. `backend/server/main.py` — 看应用入口，很短
3. `backend/server/models/` — 理解数据结构（4 张表）
4. `backend/server/schemas/schemas.py` — 看接口的数据格式
5. `backend/server/api/api_v1.py` — 看有哪些 API 端点
6. `backend/server/crud/crud.py` — 看具体的数据库操作

## 请求处理流程

```
请求进来 → API 层接收（api_v1.py）
         → CRUD 层操作数据库（crud.py）
         → 模型定义表结构（models/）
         → Schema 定义数据格式（schemas/）
```

## 各层职责

| 层 | 目录 | 职责 |
|----|------|------|
| 入口 | `main.py` | 创建 FastAPI 应用、配置 CORS、启动时建表 |
| 数据库配置 | `db/` | 数据库连接、Session 管理、Base 类 |
| 模型 | `models/` | 定义数据库表结构（字段、类型、外键、关系） |
| 数据验证 | `schemas/` | 定义 API 请求和响应的数据格式（Pydantic） |
| 数据库操作 | `crud/` | 增删改查函数，操作数据库 |
| 路由 | `api/` | 定义 API 端点，调用 CRUD 函数 |
| 业务逻辑 | `services/` | 实验自动命名等业务规则 |
| 测试 | `tests/` | API 集成测试 |

## 数据模型关系

```
ComputeSpec (芯片规格)  ←──┐
                           ├── Experiment (实验) ──→ ExperimentResult (实验结果)
ModelMetadata (模型元数据) ←─┘
```

- 一个芯片可以被多个实验引用（多对一）
- 一个模型可以被多个实验引用（多对一）
- 一个实验只有一个结果（一对一）
