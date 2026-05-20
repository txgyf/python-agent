本文档描述一个 LLM 推理性能评估平台的 RESTful 后端 API。

1. 项目目标
   提供一个 API 服务，用于管理 LLM 推理性能评估的实验数据，包括：

- 芯片规格（Compute Spec）：GPU/加速卡硬件参数
- 模型元数据（Model Metadata）：LLM 模型基本信息
- 实验记录（Experiment）：一次推理基准测试的配置 + 结果
- AI 对比总结：调用外部 LLM 对勾选实验做文字化性能对比

2. 技术栈与约束

层面
选型
语言
Python 3.10+
框架
FastAPI
ORM
SQLAlchemy 2.x（declarative style）
数据验证
Pydantic v2（from_attributes = True）
数据库
SQLite（本地开发）/ MySQL（生产，通过 pymysql）
迁移
Alembic
HTTP 客户端
httpx（调用 LLM API）
配置
环境变量 + dotenv；可选 Apollo 配置中心（仅 MySQL 模式）

数据库双模式：项目维护两套后端目录（`backend/` 用 SQLite，`backend_mysql/` 用 MySQL + Apollo）。差异仅在 `db/session.py`、`main.py` 的 title、`requirements.txt` 和 MySQL 版多一个 `config/apollo_env.py`。核心 models/schemas/crud/api 完全相同。

3. 项目结构

backend/
├── server/
│ ├── main.py # FastAPI app，CORS，挂载路由
│ ├── api/
│ │ └── api_v1.py # 所有 /api/v1/\* 端点
│ ├── crud/
│ │ └── crud.py # 数据库 CRUD 操作
│ ├── db/
│ │ ├── base_class.py # Declarative Base（自动生成 **tablename**）
│ │ ├── base.py # 导入所有 models 供 Alembic 发现
│ │ └── session.py # engine + SessionLocal
│ ├── models/
│ │ ├── compute_spec.py
│ │ ├── experiment.py
│ │ ├── experiment_result.py
│ │ └── model_metadata.py
│ ├── schemas/
│ │ └── schemas.py # Pydantic request/response models
│ └── services/
│ ├── ai_summary.py # LLM 调用：构建 prompt + httpx 请求
│ └── experiment_naming.py # 实验自动命名
├── alembic/ # 数据库迁移
├── alembic.ini
├── requirements.txt
├── seed.py # 种子数据生成脚本
└── tests/
├── conftest.py # pytest fixtures（SQLite 内存库）
└── test_api.py # API 集成测试

4. 数据模型

4.1 compute_specs 表

字段
类型
约束
说明
id
Integer
PK, auto

chip_name
String
indexed
芯片名称，如 "NVIDIA H800"
fp32_tflops
Float

FP32 算力（TFLOPS）
tf32_tflops
Float

TF32 算力
fp16_tflops
Float

FP16 算力
fp8_tflops
Float

FP8 算力
fp4_tflops
Float

FP4 算力
interconnect_bandwidth
Float

互联带宽（GB/s）
memory_gb
Float

显存容量（GB）
memory_bandwidth_tbs
Float

显存带宽（TB/s）
remarks
String
nullable
备注
updated_at
DateTime(tz)
auto now/onupdate

updated_by
String
NOT NULL
操作人

4.2 model_metadata 表

字段
类型
约束
说明
id
Integer
PK, auto

model_name
String
indexed
模型名称，如 "Llama-3-70B"
architecture
String

"Dense" 或 "MoE"
model_type
String
default "LLM"
模型类型
parameters_count
String

总参数量，如 "70B"、"671B"
active_parameters_count
String

激活参数量（MoE 模型不同于总量）
lpai_link
String
nullable
内部平台链接
updated_at
DateTime(tz)
auto now/onupdate

updated_by
String
nullable, default "admin"

4.3 experiment_results 表

字段
类型
约束
说明
id
Integer
PK, auto

actual_request_rate
Float

实际请求速率
max_request_concurrency
Integer

最大请求并发
successful_requests
Integer

成功请求数
duration_s
Float

基准测试持续秒数
total_input_tokens
Integer

总输入 token 数
total_generated_tokens
Integer

总生成 token 数
request_throughput_reqs
Float

请求吞吐（req/s）
input_token_throughput_toks
Float

输入 token 吞吐
output_token_throughput_toks
Float

输出 token 吞吐
total_token_throughput_toks
Float

总 token 吞吐
actual_concurrency
Float

实际并发度
goodput_reqs
Float
nullable
Goodput（req/s）
e2e_mean_ms
Float

端到端时延均值
e2e_median_ms
Float

端到端时延中位数
e2e_p95_ms
Float
nullable
端到端 P95
e2e_p99_ms
Float
nullable
端到端 P99
ttft_mean_ms
Float

首 token 时延均值
ttft_median_ms
Float

首 token 时延中位数
ttft_p95_ms
Float
nullable
TTFT P95
ttft_p99_ms
Float
nullable
TTFT P99
itl_mean_ms
Float

token 间隔时延均值
itl_median_ms
Float

token 间隔时延中位数
itl_p95_ms
Float
nullable
ITL P95
itl_p99_ms
Float
nullable
ITL P99
itl_max_ms
Float
nullable
ITL 最大值
tpot_mean_ms
Float
nullable
每输出 token 时延均值
tpot_median_ms
Float
nullable
TPOT 中位数
tpot_p95_ms
Float
nullable
TPOT P95
tpot_p99_ms
Float
nullable
TPOT P99
peak_memory_usage_pct
Float
nullable
峰值显存使用率（%）
avg_memory_usage_pct
Float
nullable
平均显存使用率（%）
peak_tensor_core_usage_pct
Float
nullable
Tensor Core 峰值使用率
avg_tensor_core_usage_pct
Float
nullable
Tensor Core 平均使用率

4.4 experiments 表

字段
类型
约束
说明
id
Integer
PK, auto

experiment_name
String(255)
nullable
实验名称，自动生成或用户指定
compute_spec_id
Integer
FK → compute_specs.id, CASCADE

model_id
Integer
FK → model_metadata.id, CASCADE

result_id
Integer
FK → experiment_results.id, CASCADE

engine
String

推理引擎，如 "vLLM"
engine_version
String

引擎版本
deployment_precision
String

部署精度，如 "BF16"
isl
Integer

输入序列长度
osl
Integer

输出序列长度
request_rate
Float

请求频率
total_requests
Integer

总请求数
concurrency
Integer

并发度
deploy_param
String
nullable
部署参数，如 "tp=8, dp=1"
resource_count
Integer

使用的 GPU 卡数
goodput_threshold
String(255)
nullable
Goodput 阈值
lpai_link
String
nullable
实验链接
remarks
String
nullable
备注
updated_at
DateTime(tz)
auto now/onupdate

updated_by
String
nullable, default "admin"

关系：Experiment → ComputeSpec（多对一）、ModelMetadata（多对一）、ExperimentResult（一对一）

5. API 契约

基础路径：/api/v1。所有端点返回 JSON。

5.1 芯片规格 CRUD

方法
路径
请求体
响应
说明
GET
/compute-specs
—
ComputeSpec[]
列表，支持 skip/limit 查询参数
POST
/compute-specs
ComputeSpecCreate
ComputeSpec
创建单个
POST
/compute-specs/batch
ComputeSpecCreate[]
ComputeSpec[]
批量创建
PUT
/compute-specs/{id}
ComputeSpecUpdate
ComputeSpec
部分更新
DELETE
/compute-specs/{id}
—
ComputeSpec
删除；若
删除保护：若 `experiments` 表中存在 `compute_spec_id = id` 的记录，返回 `409 {"detail": "该芯片有 N 条关联实验，请先删除相关实验数据"}`。

5.2 模型元数据 CRUD

方法
路径
请求体
响应
说明
GET
/models
—
ModelMetadata[]
列表
POST
/models
ModelMetadataCreate
ModelMetadata

POST
/models/batch
ModelMetadataCreate[]
ModelMetadata[]

PUT
/models/{id}
ModelMetadataUpdate
ModelMetadata

DELETE
/models/{id}
—
ModelMetadata
同样有 409 关联保护

5.3 实验 CRUD

方法
路径
请求体
响应
说明
GET
/experiments
—
Experiment[]
支持筛选（见下），X-Total-Count header
POST
/experiments
ExperimentCreate
ExperimentSimple
内含 result 嵌套对象
POST
/experiments/batch
ExperimentCreate[]
ExperimentSimple[]

PUT
/experiments/{id}
ExperimentUpdate
ExperimentSimple
可同时更新 result
DELETE
/experiments/{id}
—
ExperimentSimple
级联删除关联 result

GET /experiments 筛选参数：

参数
类型
说明
model_id
int
按模型 ID 筛选
compute_spec_id
int
按芯片 ID 筛选
experiment_name_q
string
实验名模糊搜索（忽略空格+大小写）
skip
int
分页偏移，默认 0
limit
int
分页大小，默认 10000

模糊搜索规则：去掉 experiment_name_q 中的空格并转小写，用 `LIKE %q%` 匹配（同时也去掉存储值中的空格来比较）。

响应 header 包含 X-Total-Count 表示符合条件的总记录数。

5.4 AI 对比总结

方法
路径
请求体
响应
说明
POST
/comparison/ai-summary
ComparisonAISummaryRequest
ComparisonAISummaryResponse
调用外部 LLM

请求体结构：
{
"x_axis_dimension": "model" | "experiment",
"baseline_chip_id": 1,
"baseline_chip_name": "NVIDIA H800",
"selected_chips_order": ["NVIDIA H800", "NVIDIA H20"], // 第一个为 baseline
"selected_metric_keys": ["output_token_throughput", "ttft_mean"],
"rows": [
{
"experiment_id": 1,
"chip_name": "NVIDIA H800",
"model_name": "Llama-3-70B",
"model_architecture": "Dense",
"model_type": "LLM",
"engine": "vLLM",
"engine_version": "v0.6.3",
"deployment_precision": "BF16",
"deploy_param": "tp=8, dp=1",
"resource_count": 8,
"isl": 512,
"osl": 512,
"request_rate": 10.0,
"concurrency": 32,
"metrics": {
"request_throughput": 12.5,
"output_token_throughput": 1600.0,
"ttft_mean_ms": 48.5,
...
}
}
]
}

响应结构：
{
"summary": "1. Dense 模型下：H800 输出吞吐 1600 tok/s，H20 为 640 tok/s（0.40x）...",
"llm_model": "gpt-4o-mini"
}

错误：LLM 未配置时返回 503；HTTP 错误或格式异常也返回 503 并附带 detail。

6. 核心业务逻辑

6.1 实验自动命名

创建实验时，若未提供 experiment_name：

1. 查询关联的 ComputeSpec 和 ModelMetadata 获取 chip_name 和 model_name
2. 去掉所有空格
3. 格式：{model*name}*{chip*name}*{YYMMDD}\_{4位随机数}（随机数 = result_id % 10000）
4. 若用户提供了名称，则去除空格后直接使用
   6.2 实验创建流程

5. 先创建 ExperimentResult 记录，获得 result_id
6. 生成/规范化 experiment_name
7. 创建 Experiment 记录，关联 result_id
   6.3 实验更新流程

8. 若请求包含 result 字段，先更新关联的 ExperimentResult
9. 更新 Experiment 本身字段
10. 自动设置 updated_at = utcnow()
    6.4 实验删除

11. 删除 Experiment 记录
12. 级联删除关联的 ExperimentResult 记录
    6.5 AI 总结服务

配置（通过环境变量）：

变量
说明
默认值
INFEREVAL_LLM_API_BASE
LLM API 基地址
—（必填）
INFEREVAL_LLM_API_KEY
API 密钥
—（必填）
INFEREVAL_LLM_MODEL
模型名
gpt-4o-mini
INFEREVAL_LLM_MAX_TOKENS
最大输出 token
1100
INFEREVAL_LLM_TIMEOUT_S
HTTP 超时秒数
120
INFEREVAL_LLM_EXTRA_HEADER
额外 HTTP header（"Name: value" 格式）
—

调用流程：

1. 构建系统 prompt：要求 LLM 以中文输出 2-5 条分条总结，按模型架构组织，以 baseline 芯片为参照对比各芯片的吞吐/时延指标，最后一条为总结性结论
2. 构建用户消息：将请求体 JSON 序列化后作为上下文
3. 通过 httpx 调用 OpenAI 兼容的 /chat/completions 端点，temperature=0.25
4. 后处理：去掉 Markdown 标记（#、\*\*、- 列表符号），保留分行
   6.6 Apollo 配置中心集成（仅 MySQL 模式）

- 若设置 APOLLO_CONFIG_URL，启动时从 Apollo 拉取 MySQL 连接信息和 LLM 配置写入环境变量
- 已存在的环境变量优先（不会被 Apollo 覆盖）
- 需安装 apollo-client-python
- 可通过 APOLLO_ENV_KEYS 环境变量自定义 Apollo key → env key 的映射

7. Pydantic Schema 层次

每个实体遵循 Base → Create / Update → Read 三层模式：

- XxxBase：共有字段
- XxxCreate：继承 Base，用于 POST
- XxxUpdate：所有字段 Optional，用于 PUT（exclude_unset=True 只更新提供的字段）
- Xxx：读取模型，含 id 和 from_attributes = True
  Experiment 特殊：
- ExperimentCreate 内嵌 result: ExperimentResultCreate（创建时同时提交结果）
- Experiment（读取用）包含嵌套的 compute_spec、model、result 完整对象
- ExperimentSimple（创建/更新/删除响应）只有 id + result_id，不含关联对象

8. Declarative Base 约定

- Base 类使用 @as_declarative() 装饰器
- **tablename** 自动生成为类名小写
- 所有 model 在 db/base.py 中导入，供 Alembic autogenerate 发现

9. 数据库会话

- 使用 yield 依赖注入：get_db() → try: yield db finally: db.close()
- SQLite 模式：connect_args={"check_same_thread": False}
- MySQL 模式：pool_pre_ping=True, pool_recycle=3600
- DATABASE_URL 环境变量优先；SQLite 默认 sqlite:///./infereval.db

10. 测试

- 框架：pytest + FastAPI TestClient
- 使用独立 SQLite 内存数据库，每个测试用事务回滚隔离
- conftest.py 中 setup_db fixture 在 session 级别创建/销毁表
- 测试覆盖：根路径、芯片 CRUD、模型 CRUD、实验创建含 result

11. CORS

允许所有来源（allow_origins=["*"]），适合开发/内网部署场景。

12. 启动方式

cd backend
python3 -m uvicorn server.main:app --host 0.0.0.0 --port 8014

生产环境（MySQL 版）通过 start.sh 启动，先加载 .env，设置 PYTHONPATH，再以 nohup 后台运行 uvicorn。
