# InfereVal - LLM 推理性能评估平台

LLM 推理性能评估平台的 RESTful 后端 API，用于管理推理基准测试的芯片规格、模型元数据和实验数据。

## 技术栈

- Python 3.10+ / FastAPI
- SQLAlchemy 2.x + SQLite（本地）/ PostgreSQL（生产）
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

## 部署到腾讯云

### 方式一：云服务器（CVM）+ Docker（推荐）

1. 购买一台轻量应用服务器（2核4G 够用），选 Ubuntu 系统
2. SSH 登录服务器，安装 Docker：
   ```bash
   curl -fsSL https://get.docker.com | sh
   ```
3. 拉取代码并启动：
   ```bash
   git clone https://github.com/txgyf/python-agent.git
   cd python-agent
   export DB_PASSWORD=改成一个强密码
   docker compose up -d
   ```
4. 在腾讯云安全组中放行 8014 端口
5. 访问 `http://你的服务器IP:8014/docs`

### 方式二：云服务器 + 托管数据库（TencentDB）

如果需要独立的数据库服务：

1. 在腾讯云购买 **TencentDB for PostgreSQL** 实例
2. 修改 `docker-compose.yml`，删除 `db` 服务，将 `DATABASE_URL` 改为 TencentDB 的连接地址：
   ```yaml
   environment:
     - DATABASE_URL=postgresql://用户名:密码@数据库地址:5432/infereval
   ```
3. 其余步骤与方式一相同

### 常用运维命令

```bash
docker compose logs -f       # 查看日志
docker compose restart       # 重启服务
docker compose down          # 停止服务
docker compose pull && docker compose up -d   # 更新代码后重新部署
```
