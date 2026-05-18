# LLM 部署实验记录系统 - 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建一个 FastAPI + SQLite 的 CRUD 服务，管理 GPU 芯片、大模型和部署实验记录。

**Architecture:** FastAPI 应用通过 SQLAlchemy 2.0 ORM 操作 SQLite 数据库。三个实体（GPU、Model、Experiment）各自有独立的 router 处理 CRUD，Pydantic schemas 负责请求/响应校验。

**Tech Stack:** Python 3.10+, FastAPI 0.115+, SQLAlchemy 2.0+, Pydantic v2, SQLite, httpx (测试用)

---

## File Structure

| 文件 | 职责 |
|------|------|
| `requirements.txt` | 项目依赖 |
| `app/__init__.py` | 包标记，空文件 |
| `app/database.py` | SQLAlchemy engine、SessionLocal、Base、init 函数 |
| `app/models.py` | 三个 ORM 模型：GPU、Model、Experiment |
| `app/schemas.py` | Pydantic Create/Update/Response schemas |
| `app/routers/__init__.py` | 包标记，空文件 |
| `app/routers/gpus.py` | GPU CRUD 路由 |
| `app/routers/models.py` | Model CRUD 路由 |
| `app/routers/experiments.py` | Experiment CRUD 路由（含筛选） |
| `app/main.py` | FastAPI app 实例，注册路由，lifespan 初始化数据库 |
| `tests/__init__.py` | 包标记，空文件 |
| `tests/conftest.py` | pytest fixtures：测试数据库、测试客户端 |
| `tests/test_gpus.py` | GPU CRUD 测试 |
| `tests/test_models.py` | Model CRUD 测试 |
| `tests/test_experiments.py` | Experiment CRUD 测试（含筛选和关联校验） |

---

### Task 1: 项目骨架和依赖

**Files:**
- Create: `requirements.txt`
- Create: `data/.gitkeep`
- Create: `app/__init__.py`
- Create: `app/routers/__init__.py`

- [ ] **Step 1: 创建 requirements.txt**

```txt
fastapi>=0.115.0
sqlalchemy>=2.0.0
uvicorn>=0.30.0
httpx>=0.27.0
pytest>=8.0.0
```

- [ ] **Step 2: 创建目录和空文件**

Run:
```bash
mkdir -p app/routers data tests
touch data/.gitkeep app/__init__.py app/routers/__init__.py tests/__init__.py
```

- [ ] **Step 3: 安装依赖**

Run: `pip install -r requirements.txt`
Expected: 所有包安装成功

- [ ] **Step 4: 提交**

```bash
git add requirements.txt data/.gitkeep app/__init__.py app/routers/__init__.py tests/__init__.py
git commit -m "chore: init project skeleton with dependencies"
```

---

### Task 2: 数据库配置

**Files:**
- Create: `app/database.py`

- [ ] **Step 1: 编写 database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 2: 验证模块可导入**

Run: `python -c "from app.database import Base, engine, SessionLocal, init_db; print('OK')"`
Expected: 输出 `OK`

- [ ] **Step 3: 提交**

```bash
git add app/database.py
git commit -m "feat: add database configuration"
```

---

### Task 3: ORM 模型

**Files:**
- Create: `app/models.py`

- [ ] **Step 1: 编写 models.py**

```python
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GPU(Base):
    __tablename__ = "gpus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    memory_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class Model(Base):
    __tablename__ = "models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    parameter_size: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("models.id", ondelete="RESTRICT"), nullable=False
    )
    gpu_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("gpus.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    model: Mapped[Model] = relationship("Model", lazy="selectin")
    gpu: Mapped[GPU] = relationship("GPU", lazy="selectin")
```

- [ ] **Step 2: 验证模块可导入**

Run: `python -c "from app.models import GPU, Model, Experiment; print('OK')"`
Expected: 输出 `OK`

- [ ] **Step 3: 提交**

```bash
git add app/models.py
git commit -m "feat: add SQLAlchemy ORM models for GPU, Model, Experiment"
```

---

### Task 4: Pydantic Schemas

**Files:**
- Create: `app/schemas.py`

- [ ] **Step 1: 编写 schemas.py**

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# --- GPU ---

class GPUCreate(BaseModel):
    name: str
    manufacturer: str
    memory_gb: int


class GPUUpdate(BaseModel):
    name: str | None = None
    manufacturer: str | None = None
    memory_gb: int | None = None


class GPUResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    manufacturer: str
    memory_gb: int
    created_at: datetime


# --- Model ---

class ModelCreate(BaseModel):
    name: str
    provider: str
    parameter_size: str
    description: str | None = None


class ModelUpdate(BaseModel):
    name: str | None = None
    provider: str | None = None
    parameter_size: str | None = None
    description: str | None = None


class ModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    provider: str
    parameter_size: str
    description: str | None
    created_at: datetime


# --- Experiment ---

class ExperimentCreate(BaseModel):
    model_id: int
    gpu_id: int
    status: str = "pending"
    config: dict | None = None
    metrics: dict | None = None
    notes: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class ExperimentUpdate(BaseModel):
    model_id: int | None = None
    gpu_id: int | None = None
    status: str | None = None
    config: dict | None = None
    metrics: dict | None = None
    notes: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: int
    gpu_id: int
    status: str
    config: dict | None
    metrics: dict | None
    notes: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    model: ModelResponse
    gpu: GPUResponse


# --- Pagination ---

class PaginatedResponse(BaseModel):
    items: list
    total: int
```

- [ ] **Step 2: 验证模块可导入**

Run: `python -c "from app.schemas import GPUCreate, ModelCreate, ExperimentCreate; print('OK')"`
Expected: 输出 `OK`

- [ ] **Step 3: 提交**

```bash
git add app/schemas.py
git commit -m "feat: add Pydantic schemas for request/response validation"
```

---

### Task 5: 测试基础设施

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: 编写 conftest.py**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import GPU, Model

TEST_DB_URL = "sqlite:///./data/test.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_gpu(client):
    response = client.post("/api/gpus", json={
        "name": "A100",
        "manufacturer": "NVIDIA",
        "memory_gb": 80
    })
    return response.json()


@pytest.fixture
def sample_model(client):
    response = client.post("/api/models", json={
        "name": "LLaMA-3-70B",
        "provider": "Meta",
        "parameter_size": "70B",
        "description": "A large language model"
    })
    return response.json()
```

- [ ] **Step 2: 提交**

```bash
git add tests/conftest.py
git commit -m "test: add test fixtures and database setup"
```

---

### Task 6: GPU CRUD 路由

**Files:**
- Create: `app/routers/gpus.py`
- Create: `app/main.py` (初始版本，仅注册 gpu router)
- Create: `tests/test_gpus.py`

- [ ] **Step 1: 编写 gpus.py 路由**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GPU
from app.schemas import GPUCreate, GPUUpdate, GPUResponse, PaginatedResponse

router = APIRouter(prefix="/api/gpus", tags=["GPUs"])


@router.get("", response_model=PaginatedResponse)
def list_gpus(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(GPU)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}


@router.post("", response_model=GPUResponse, status_code=201)
def create_gpu(gpu: GPUCreate, db: Session = Depends(get_db)):
    db_gpu = GPU(**gpu.model_dump())
    db.add(db_gpu)
    db.commit()
    db.refresh(db_gpu)
    return db_gpu


@router.get("/{gpu_id}", response_model=GPUResponse)
def get_gpu(gpu_id: int, db: Session = Depends(get_db)):
    gpu = db.query(GPU).filter(GPU.id == gpu_id).first()
    if not gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    return gpu


@router.put("/{gpu_id}", response_model=GPUResponse)
def update_gpu(gpu_id: int, gpu: GPUUpdate, db: Session = Depends(get_db)):
    db_gpu = db.query(GPU).filter(GPU.id == gpu_id).first()
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    for key, value in gpu.model_dump(exclude_unset=True).items():
        setattr(db_gpu, key, value)
    db.commit()
    db.refresh(db_gpu)
    return db_gpu


@router.delete("/{gpu_id}")
def delete_gpu(gpu_id: int, db: Session = Depends(get_db)):
    db_gpu = db.query(GPU).filter(GPU.id == gpu_id).first()
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    from app.models import Experiment
    if db.query(Experiment).filter(Experiment.gpu_id == gpu_id).first():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete GPU with associated experiments"
        )
    db.delete(db_gpu)
    db.commit()
    return {"message": "deleted"}
```

- [ ] **Step 2: 编写 main.py**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import gpus


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="LLM Deployment Tracker", lifespan=lifespan)
app.include_router(gpus.router)
```

- [ ] **Step 3: 编写 test_gpus.py**

```python
class TestGPUCreate:
    def test_create_gpu(self, client):
        response = client.post("/api/gpus", json={
            "name": "A100",
            "manufacturer": "NVIDIA",
            "memory_gb": 80
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "A100"
        assert data["manufacturer"] == "NVIDIA"
        assert data["memory_gb"] == 80
        assert "id" in data
        assert "created_at" in data


class TestGPUList:
    def test_list_gpus_empty(self, client):
        response = client.get("/api/gpus")
        assert response.status_code == 200
        assert response.json() == {"items": [], "total": 0}

    def test_list_gpus_with_data(self, client):
        client.post("/api/gpus", json={
            "name": "A100", "manufacturer": "NVIDIA", "memory_gb": 80
        })
        client.post("/api/gpus", json={
            "name": "H100", "manufacturer": "NVIDIA", "memory_gb": 80
        })
        response = client.get("/api/gpus")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_list_gpus_pagination(self, client):
        for i in range(5):
            client.post("/api/gpus", json={
                "name": f"GPU-{i}", "manufacturer": "NVIDIA", "memory_gb": 80
            })
        response = client.get("/api/gpus?skip=2&limit=2")
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2


class TestGPUGet:
    def test_get_gpu(self, client, sample_gpu):
        response = client.get(f"/api/gpus/{sample_gpu['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "A100"

    def test_get_gpu_not_found(self, client):
        response = client.get("/api/gpus/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "GPU not found"


class TestGPUUpdate:
    def test_update_gpu(self, client, sample_gpu):
        response = client.put(f"/api/gpus/{sample_gpu['id']}", json={
            "name": "A100-Updated"
        })
        assert response.status_code == 200
        assert response.json()["name"] == "A100-Updated"

    def test_update_gpu_not_found(self, client):
        response = client.put("/api/gpus/999", json={"name": "X"})
        assert response.status_code == 404


class TestGPUDelete:
    def test_delete_gpu(self, client, sample_gpu):
        response = client.delete(f"/api/gpus/{sample_gpu['id']}")
        assert response.status_code == 200
        assert response.json()["message"] == "deleted"

    def test_delete_gpu_not_found(self, client):
        response = client.delete("/api/gpus/999")
        assert response.status_code == 404
```

- [ ] **Step 4: 运行测试**

Run: `python -m pytest tests/test_gpus.py -v`
Expected: 全部 PASSED

- [ ] **Step 5: 提交**

```bash
git add app/routers/gpus.py app/main.py tests/test_gpus.py
git commit -m "feat: add GPU CRUD endpoints with tests"
```

---

### Task 7: Model CRUD 路由

**Files:**
- Create: `app/routers/models.py`
- Create: `tests/test_models.py`
- Modify: `app/main.py` — 注册 model router

- [ ] **Step 1: 编写 models.py 路由**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Model
from app.schemas import ModelCreate, ModelUpdate, ModelResponse, PaginatedResponse

router = APIRouter(prefix="/api/models", tags=["Models"])


@router.get("", response_model=PaginatedResponse)
def list_models(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(Model)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}


@router.post("", response_model=ModelResponse, status_code=201)
def create_model(model: ModelCreate, db: Session = Depends(get_db)):
    db_model = Model(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.put("/{model_id}", response_model=ModelResponse)
def update_model(model_id: int, model: ModelUpdate, db: Session = Depends(get_db)):
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    for key, value in model.model_dump(exclude_unset=True).items():
        setattr(db_model, key, value)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.delete("/{model_id}")
def delete_model(model_id: int, db: Session = Depends(get_db)):
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    from app.models import Experiment
    if db.query(Experiment).filter(Experiment.model_id == model_id).first():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete model with associated experiments"
        )
    db.delete(db_model)
    db.commit()
    return {"message": "deleted"}
```

- [ ] **Step 2: 更新 main.py 注册 model router**

在 `app/main.py` 中添加 import 和 include_router：

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import gpus, models


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="LLM Deployment Tracker", lifespan=lifespan)
app.include_router(gpus.router)
app.include_router(models.router)
```

- [ ] **Step 3: 编写 test_models.py**

```python
class TestModelCreate:
    def test_create_model(self, client):
        response = client.post("/api/models", json={
            "name": "LLaMA-3-70B",
            "provider": "Meta",
            "parameter_size": "70B",
            "description": "A large language model"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "LLaMA-3-70B"
        assert data["provider"] == "Meta"
        assert data["parameter_size"] == "70B"
        assert data["description"] == "A large language model"
        assert "id" in data
        assert "created_at" in data

    def test_create_model_without_description(self, client):
        response = client.post("/api/models", json={
            "name": "GPT-4",
            "provider": "OpenAI",
            "parameter_size": "unknown"
        })
        assert response.status_code == 201
        assert response.json()["description"] is None


class TestModelList:
    def test_list_models_empty(self, client):
        response = client.get("/api/models")
        assert response.status_code == 200
        assert response.json() == {"items": [], "total": 0}

    def test_list_models_pagination(self, client):
        for i in range(5):
            client.post("/api/models", json={
                "name": f"Model-{i}", "provider": "Test", "parameter_size": "1B"
            })
        response = client.get("/api/models?skip=1&limit=2")
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2


class TestModelGet:
    def test_get_model(self, client, sample_model):
        response = client.get(f"/api/models/{sample_model['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "LLaMA-3-70B"

    def test_get_model_not_found(self, client):
        response = client.get("/api/models/999")
        assert response.status_code == 404


class TestModelUpdate:
    def test_update_model(self, client, sample_model):
        response = client.put(f"/api/models/{sample_model['id']}", json={
            "description": "Updated description"
        })
        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"

    def test_update_model_not_found(self, client):
        response = client.put("/api/models/999", json={"name": "X"})
        assert response.status_code == 404


class TestModelDelete:
    def test_delete_model(self, client, sample_model):
        response = client.delete(f"/api/models/{sample_model['id']}")
        assert response.status_code == 200
        assert response.json()["message"] == "deleted"

    def test_delete_model_not_found(self, client):
        response = client.delete("/api/models/999")
        assert response.status_code == 404
```

- [ ] **Step 4: 运行测试**

Run: `python -m pytest tests/test_models.py -v`
Expected: 全部 PASSED

- [ ] **Step 5: 提交**

```bash
git add app/routers/models.py app/main.py tests/test_models.py
git commit -m "feat: add Model CRUD endpoints with tests"
```

---

### Task 8: Experiment CRUD 路由

**Files:**
- Create: `app/routers/experiments.py`
- Create: `tests/test_experiments.py`
- Modify: `app/main.py` — 注册 experiment router

- [ ] **Step 1: 编写 experiments.py 路由**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Experiment
from app.schemas import (
    ExperimentCreate, ExperimentUpdate, ExperimentResponse, PaginatedResponse
)

router = APIRouter(prefix="/api/experiments", tags=["Experiments"])


@router.get("", response_model=PaginatedResponse)
def list_experiments(
    skip: int = 0,
    limit: int = 20,
    status: str | None = None,
    model_id: int | None = None,
    gpu_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Experiment)
    if status:
        query = query.filter(Experiment.status == status)
    if model_id:
        query = query.filter(Experiment.model_id == model_id)
    if gpu_id:
        query = query.filter(Experiment.gpu_id == gpu_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}


@router.post("", response_model=ExperimentResponse, status_code=201)
def create_experiment(
    experiment: ExperimentCreate, db: Session = Depends(get_db)
):
    from app.models import GPU, Model
    if not db.query(GPU).filter(GPU.id == experiment.gpu_id).first():
        raise HTTPException(status_code=400, detail="GPU not found")
    if not db.query(Model).filter(Model.id == experiment.model_id).first():
        raise HTTPException(status_code=400, detail="Model not found")
    db_exp = Experiment(**experiment.model_dump())
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp


@router.put("/{experiment_id}", response_model=ExperimentResponse)
def update_experiment(
    experiment_id: int, experiment: ExperimentUpdate, db: Session = Depends(get_db)
):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    for key, value in experiment.model_dump(exclude_unset=True).items():
        setattr(exp, key, value)
    db.commit()
    db.refresh(exp)
    return exp


@router.delete("/{experiment_id}")
def delete_experiment(experiment_id: int, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    db.delete(exp)
    db.commit()
    return {"message": "deleted"}
```

- [ ] **Step 2: 更新 main.py 注册 experiment router**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import gpus, models, experiments


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="LLM Deployment Tracker", lifespan=lifespan)
app.include_router(gpus.router)
app.include_router(models.router)
app.include_router(experiments.router)
```

- [ ] **Step 3: 编写 test_experiments.py**

```python
class TestExperimentCreate:
    def test_create_experiment(self, client, sample_gpu, sample_model):
        response = client.post("/api/experiments", json={
            "model_id": sample_model["id"],
            "gpu_id": sample_gpu["id"],
            "status": "pending",
            "config": {"batch_size": 32, "quantization": "int8"},
            "notes": "Initial test"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert data["config"]["batch_size"] == 32
        assert data["model"]["name"] == "LLaMA-3-70B"
        assert data["gpu"]["name"] == "A100"

    def test_create_experiment_invalid_gpu(self, client, sample_model):
        response = client.post("/api/experiments", json={
            "model_id": sample_model["id"],
            "gpu_id": 999
        })
        assert response.status_code == 400
        assert "GPU not found" in response.json()["detail"]

    def test_create_experiment_invalid_model(self, client, sample_gpu):
        response = client.post("/api/experiments", json={
            "model_id": 999,
            "gpu_id": sample_gpu["id"]
        })
        assert response.status_code == 400
        assert "Model not found" in response.json()["detail"]


class TestExperimentList:
    def test_list_experiments_empty(self, client):
        response = client.get("/api/experiments")
        assert response.status_code == 200
        assert response.json() == {"items": [], "total": 0}

    def test_list_experiments_filter_by_status(self, client, sample_gpu, sample_model):
        client.post("/api/experiments", json={
            "model_id": sample_model["id"],
            "gpu_id": sample_gpu["id"],
            "status": "running"
        })
        client.post("/api/experiments", json={
            "model_id": sample_model["id"],
            "gpu_id": sample_gpu["id"],
            "status": "completed"
        })
        response = client.get("/api/experiments?status=running")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "running"

    def test_list_experiments_filter_by_model(self, client, sample_gpu, sample_model):
        client.post("/api/experiments", json={
            "model_id": sample_model["id"],
            "gpu_id": sample_gpu["id"]
        })
        response = client.get(f"/api/experiments?model_id={sample_model['id']}")
        assert response.json()["total"] == 1

        response = client.get("/api/experiments?model_id=999")
        assert response.json()["total"] == 0

    def test_list_experiments_filter_by_gpu(self, client, sample_gpu, sample_model):
        client.post("/api/experiments", json={
            "model_id": sample_model["id"],
            "gpu_id": sample_gpu["id"]
        })
        response = client.get(f"/api/experiments?gpu_id={sample_gpu['id']}")
        assert response.json()["total"] == 1


class TestExperimentGet:
    def test_get_experiment(self, client, sample_gpu, sample_model):
        create_resp = client.post("/api/experiments", json={
            "model_id": sample_model["id"],
            "gpu_id": sample_gpu["id"]
        })
        exp_id = create_resp.json()["id"]
        response = client.get(f"/api/experiments/{exp_id}")
        assert response.status_code == 200
        assert response.json()["id"] == exp_id

    def test_get_experiment_not_found(self, client):
        response = client.get("/api/experiments/999")
        assert response.status_code == 404


class TestExperimentUpdate:
    def test_update_experiment_status(self, client, sample_gpu, sample_model):
        create_resp = client.post("/api/experiments", json={
            "model_id": sample_model["id"],
            "gpu_id": sample_gpu["id"]
        })
        exp_id = create_resp.json()["id"]
        response = client.put(f"/api/experiments/{exp_id}", json={
            "status": "running",
            "metrics": {"throughput": 150.5, "latency_ms": 12.3}
        })
        assert response.status_code == 200
        assert response.json()["status"] == "running"
        assert response.json()["metrics"]["throughput"] == 150.5

    def test_update_experiment_not_found(self, client):
        response = client.put("/api/experiments/999", json={"status": "running"})
        assert response.status_code == 404


class TestExperimentDelete:
    def test_delete_experiment(self, client, sample_gpu, sample_model):
        create_resp = client.post("/api/experiments", json={
            "model_id": sample_model["id"],
            "gpu_id": sample_gpu["id"]
        })
        exp_id = create_resp.json()["id"]
        response = client.delete(f"/api/experiments/{exp_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "deleted"

    def test_delete_experiment_not_found(self, client):
        response = client.delete("/api/experiments/999")
        assert response.status_code == 404


class TestAssociationProtection:
    def test_cannot_delete_gpu_with_experiments(
        self, client, sample_gpu, sample_model
    ):
        client.post("/api/experiments", json={
            "model_id": sample_model["id"],
            "gpu_id": sample_gpu["id"]
        })
        response = client.delete(f"/api/gpus/{sample_gpu['id']}")
        assert response.status_code == 400
        assert "associated experiments" in response.json()["detail"]

    def test_cannot_delete_model_with_experiments(
        self, client, sample_gpu, sample_model
    ):
        client.post("/api/experiments", json={
            "model_id": sample_model["id"],
            "gpu_id": sample_gpu["id"]
        })
        response = client.delete(f"/api/models/{sample_model['id']}")
        assert response.status_code == 400
        assert "associated experiments" in response.json()["detail"]
```

- [ ] **Step 4: 运行全部测试**

Run: `python -m pytest tests/ -v`
Expected: 全部 PASSED

- [ ] **Step 5: 提交**

```bash
git add app/routers/experiments.py app/main.py tests/test_experiments.py
git commit -m "feat: add Experiment CRUD endpoints with filters and tests"
```

---

### Task 9: 启动验证

- [ ] **Step 1: 启动服务**

Run: `uvicorn app.main:app --reload --port 8000`

- [ ] **Step 2: 验证 Swagger 文档**

浏览器打开 `http://localhost:8000/docs`，确认三个实体共 15 个接口都显示正确。

- [ ] **Step 3: 验证完整流程**

在 Swagger UI 中测试完整流程：
1. POST 创建一个 GPU
2. POST 创建一个 Model
3. POST 创建一个 Experiment（引用上面的 GPU 和 Model id）
4. GET 查看实验列表，确认 model 和 gpu 以嵌套对象返回
5. PUT 更新实验状态为 running
6. DELETE 删除实验
7. DELETE 删除 GPU 和 Model（删除后应成功）
