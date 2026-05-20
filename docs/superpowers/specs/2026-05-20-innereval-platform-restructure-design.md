# LLM 推理性能评估平台 - 重构设计

## 背景

当前项目使用简单的 `app/` 扁平结构，模型（`gpus`、`models`、`experiments`）与目标规范差异较大。需要按 `index.md` 文档重构为完整的评估平台后端。

## 范围

- **仅 SQLite 版本**：创建 `backend/` 目录，不含 `backend_mysql/`
- **跳过 AI 对比总结**：不实现 `/comparison/ai-summary` 端点
- **方案**：全新创建 `backend/`，完成后删除旧 `app/` 目录

## 目录结构

```
backend/
├── server/
│   ├── __init__.py
│   ├── main.py              # FastAPI app，CORS，挂载路由
│   ├── api/
│   │   ├── __init__.py
│   │   └── api_v1.py        # 所有 /api/v1/* 端点
│   ├── crud/
│   │   ├── __init__.py
│   │   └── crud.py           # 数据库 CRUD 操作
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base_class.py     # Declarative Base（自动生成 __tablename__）
│   │   ├── base.py           # 导入所有 models 供 Alembic 发现
│   │   └── session.py        # engine + SessionLocal
│   ├── models/
│   │   ├── __init__.py
│   │   ├── compute_spec.py
│   │   ├── experiment.py
│   │   ├── experiment_result.py
│   │   └── model_metadata.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py        # Pydantic request/response models
│   └── services/
│       ├── __init__.py
│       └── experiment_naming.py  # 实验自动命名
├── alembic/                  # 数据库迁移
├── alembic.ini
├── requirements.txt
├── seed.py                   # 种子数据生成脚本
└── tests/
    ├── __init__.py
    ├── conftest.py           # pytest fixtures（SQLite 内存库）
    └── test_api.py           # API 集成测试
```

## 数据模型

### compute_specs 表
- 字段：id, chip_name(indexed), fp32_tflops, tf32_tflops, fp16_tflops, fp8_tflops, fp4_tflops, interconnect_bandwidth, memory_gb, memory_bandwidth_tbs, remarks(nullable), updated_at(auto), updated_by(NOT NULL)
- `__tablename__` 自动从类名生成

### model_metadata 表
- 字段：id, model_name(indexed), architecture, model_type(default "LLM"), parameters_count, active_parameters_count, lpai_link(nullable), updated_at(auto), updated_by(nullable, default "admin")

### experiment_results 表
- 字段：id, actual_request_rate, max_request_concurrency, successful_requests, duration_s, total_input_tokens, total_generated_tokens, request_throughput_reqs, input_token_throughput_toks, output_token_throughput_toks, total_token_throughput_toks, actual_concurrency, goodput_reqs(nullable), e2e_mean_ms, e2e_median_ms, e2e_p95_ms(nullable), e2e_p99_ms(nullable), ttft_mean_ms, ttft_median_ms, ttft_p95_ms(nullable), ttft_p99_ms(nullable), itl_mean_ms, itl_median_ms, itl_p95_ms(nullable), itl_p99_ms(nullable), itl_max_ms(nullable), tpot_mean_ms(nullable), tpot_median_ms(nullable), tpot_p95_ms(nullable), tpot_p99_ms(nullable), peak_memory_usage_pct(nullable), avg_memory_usage_pct(nullable), peak_tensor_core_usage_pct(nullable), avg_tensor_core_usage_pct(nullable)

### experiments 表
- 字段：id, experiment_name(nullable, 255), compute_spec_id(FK CASCADE), model_id(FK CASCADE), result_id(FK CASCADE), engine, engine_version, deployment_precision, isl, osl, request_rate, total_requests, concurrency, deploy_param(nullable), resource_count, goodput_threshold(nullable, 255), lpai_link(nullable), remarks(nullable), updated_at(auto), updated_by(nullable, default "admin")
- 关系：Experiment → ComputeSpec(多对一)、ModelMetadata(多对一)、ExperimentResult(一对一)

## Pydantic Schema 设计

每个实体三层模式：
- **XxxBase**：共有字段
- **XxxCreate**：继承 Base，用于 POST
- **XxxUpdate**：所有字段 Optional，用于 PUT（exclude_unset=True）
- **Xxx**：读取模型，含 id + from_attributes = True

Experiment 特殊：
- `ExperimentCreate` 内嵌 `result: ExperimentResultCreate`
- `Experiment`（读取用）包含嵌套的 compute_spec、model、result 完整对象
- `ExperimentSimple`（创建/更新/删除响应）只有 id + result_id，不含关联对象

## API 端点

### 芯片规格 CRUD
- `GET /api/v1/compute-specs` — 列表，支持 skip/limit
- `POST /api/v1/compute-specs` — 创建单个
- `POST /api/v1/compute-specs/batch` — 批量创建
- `PUT /api/v1/compute-specs/{id}` — 部分更新
- `DELETE /api/v1/compute-specs/{id}` — 删除，关联实验时返回 409

### 模型元数据 CRUD
- `GET /api/v1/models` — 列表
- `POST /api/v1/models` — 创建
- `POST /api/v1/models/batch` — 批量创建
- `PUT /api/v1/models/{id}` — 更新
- `DELETE /api/v1/models/{id}` — 删除，关联实验时返回 409

### 实验 CRUD
- `GET /api/v1/experiments` — 列表，支持筛选（model_id, compute_spec_id, experiment_name_q, skip, limit），X-Total-Count header
- `POST /api/v1/experiments` — 创建（内含 result）
- `POST /api/v1/experiments/batch` — 批量创建
- `PUT /api/v1/experiments/{id}` — 更新（可同时更新 result）
- `DELETE /api/v1/experiments/{id}` — 删除，级联删除 result

模糊搜索规则：去掉 experiment_name_q 中的空格并转小写，用 LIKE %q% 匹配。

## 核心业务逻辑

### 实验自动命名
创建实验时，若未提供 experiment_name：
1. 查询关联的 ComputeSpec 和 ModelMetadata 获取 chip_name 和 model_name
2. 格式：`{model_name}_{chip_name}_{YYMMDD}_{4位随机数}`（随机数 = result_id % 10000）
3. 去掉所有空格
4. 若用户提供了名称，则去除空格后直接使用

### 实验创建流程
1. 先创建 ExperimentResult 记录，获得 result_id
2. 生成/规范化 experiment_name
3. 创建 Experiment 记录，关联 result_id

### 实验更新流程
1. 若请求包含 result 字段，先更新关联的 ExperimentResult
2. 更新 Experiment 本身字段

### 实验删除
1. 删除 Experiment 记录
2. 级联删除关联的 ExperimentResult 记录

### 删除保护
- 删除 ComputeSpec：若 experiments 表中存在 compute_spec_id = id 的记录，返回 409
- 删除 ModelMetadata：同理

## Declarative Base 约定
- 使用 `@as_declarative()` 装饰器
- `__tablename__` 自动生成为类名小写
- 所有 model 在 db/base.py 中导入

## 数据库会话
- yield 依赖注入：get_db() → try: yield db finally: db.close()
- SQLite：connect_args={"check_same_thread": False}
- DATABASE_URL 环境变量优先；默认 sqlite:///./infereval.db

## 测试
- 框架：pytest + FastAPI TestClient
- 独立 SQLite 内存数据库，每个测试用事务回滚隔离
- conftest.py 中 setup_db fixture 在 session 级别创建/销毁表
- 覆盖：根路径、芯片 CRUD + 批量 + 删除保护、模型 CRUD + 批量 + 删除保护、实验 CRUD + 筛选 + 自动命名

## CORS
允许所有来源（allow_origins=["*"]）。

## 启动方式
```
cd backend
python3 -m uvicorn server.main:app --host 0.0.0.0 --port 8014
```

## 不包含的功能
- AI 对比总结服务（`/comparison/ai-summary`）
- MySQL 版本（`backend_mysql/`）
- Apollo 配置中心集成
- Alembic 迁移脚本（仅创建目录结构，不生成迁移）
