# InfereVal Platform Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the project from the simple `app/` structure to a full `backend/` directory following the InfereVal spec, with 4 data models, CRUD APIs with batch operations, experiment auto-naming, and comprehensive tests.

**Architecture:** FastAPI application under `backend/server/` with layered structure: models → schemas → crud → api. SQLite database with dependency-injected sessions. Experiment creation follows a two-step process: first create ExperimentResult, then Experiment with auto-generated name.

**Tech Stack:** Python 3.10+, FastAPI, SQLAlchemy 2.x (declarative), Pydantic v2, SQLite, pytest + httpx

---

## File Structure

```
backend/
├── server/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app, CORS, router mount
│   ├── api/
│   │   ├── __init__.py
│   │   └── api_v1.py                  # All /api/v1/* endpoints
│   ├── crud/
│   │   ├── __init__.py
│   │   └── crud.py                    # CRUD functions for all entities
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base_class.py              # Declarative Base
│   │   ├── base.py                    # Import all models
│   │   └── session.py                 # Engine + SessionLocal + get_db
│   ├── models/
│   │   ├── __init__.py
│   │   ├── compute_spec.py            # ComputeSpec model
│   │   ├── model_metadata.py          # ModelMetadata model
│   │   ├── experiment_result.py       # ExperimentResult model
│   │   └── experiment.py              # Experiment model + relationships
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py                 # All Pydantic schemas
│   └── services/
│       ├── __init__.py
│       └── experiment_naming.py       # Auto-naming logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Fixtures with in-memory SQLite
│   └── test_api.py                    # All API tests
├── alembic/                           # Empty, placeholder for future
│   └── .gitkeep
├── alembic.ini                        # Placeholder
├── requirements.txt
└── seed.py                            # Seed data script
```

---

### Task 1: Project Scaffolding + Database Layer

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/server/__init__.py`
- Create: `backend/server/db/__init__.py`
- Create: `backend/server/db/base_class.py`
- Create: `backend/server/db/session.py`
- Create: `backend/server/db/base.py`
- Create: `backend/server/api/__init__.py`
- Create: `backend/server/crud/__init__.py`
- Create: `backend/server/models/__init__.py`
- Create: `backend/server/schemas/__init__.py`
- Create: `backend/server/services/__init__.py`
- Create: `backend/alembic/.gitkeep`
- Create: `backend/alembic.ini`

- [ ] **Step 1: Create directory structure and requirements.txt**

```bash
cd /Users/guanyifan/Desktop/project/python-agent
mkdir -p backend/server/{api,crud,db,models,schemas,services}
mkdir -p backend/tests
mkdir -p backend/alembic
touch backend/server/__init__.py
touch backend/server/{api,crud,db,models,schemas,services}/__init__.py
touch backend/tests/__init__.py
touch backend/alembic/.gitkeep
```

- [ ] **Step 2: Write requirements.txt**

Create `backend/requirements.txt`:
```
fastapi>=0.115.0
sqlalchemy>=2.0.0
uvicorn>=0.30.0
httpx>=0.27.0
pydantic>=2.0.0
pytest>=8.0.0
```

- [ ] **Step 3: Write db/base_class.py**

Create `backend/server/db/base_class.py`:
```python
from sqlalchemy.orm import as_declarative


@as_declarative()
class Base:
    pass
```

- [ ] **Step 4: Write db/session.py**

Create `backend/server/db/session.py`:
```python
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL", "sqlite:///./infereval.db"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 5: Write db/base.py (placeholder, models imported in Task 2)**

Create `backend/server/db/base.py`:
```python
from server.db.base_class import Base  # noqa: F401
```

- [ ] **Step 6: Write placeholder alembic.ini**

Create `backend/alembic.ini`:
```ini
[alembic]
script_location = alembic
sqlalchemy.url = sqlite:///./infereval.db
```

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat: scaffold backend/ directory structure with db layer"
```

---

### Task 2: All SQLAlchemy Models

**Files:**
- Create: `backend/server/models/compute_spec.py`
- Create: `backend/server/models/model_metadata.py`
- Create: `backend/server/models/experiment_result.py`
- Create: `backend/server/models/experiment.py`
- Modify: `backend/server/db/base.py`

- [ ] **Step 1: Write ComputeSpec model**

Create `backend/server/models/compute_spec.py`:
```python
from datetime import datetime, timezone

from sqlalchemy import Float, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from server.db.base_class import Base


class ComputeSpec(Base):
    __tablename__ = "compute_specs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chip_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    fp32_tflops: Mapped[float] = mapped_column(Float, nullable=False)
    tf32_tflops: Mapped[float] = mapped_column(Float, nullable=False)
    fp16_tflops: Mapped[float] = mapped_column(Float, nullable=False)
    fp8_tflops: Mapped[float] = mapped_column(Float, nullable=False)
    fp4_tflops: Mapped[float] = mapped_column(Float, nullable=False)
    interconnect_bandwidth: Mapped[float] = mapped_column(Float, nullable=False)
    memory_gb: Mapped[float] = mapped_column(Float, nullable=False)
    memory_bandwidth_tbs: Mapped[float] = mapped_column(Float, nullable=False)
    remarks: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    updated_by: Mapped[str] = mapped_column(String, nullable=False)
```

- [ ] **Step 2: Write ModelMetadata model**

Create `backend/server/models/model_metadata.py`:
```python
from datetime import datetime, timezone

from sqlalchemy import Float, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from server.db.base_class import Base


class ModelMetadata(Base):
    __tablename__ = "model_metadata"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    architecture: Mapped[str] = mapped_column(String, nullable=False)
    model_type: Mapped[str] = mapped_column(String, nullable=False, default="LLM")
    parameters_count: Mapped[str] = mapped_column(String, nullable=False)
    active_parameters_count: Mapped[str] = mapped_column(String, nullable=False)
    lpai_link: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    updated_by: Mapped[str | None] = mapped_column(String, nullable=True, default="admin")
```

- [ ] **Step 3: Write ExperimentResult model**

Create `backend/server/models/experiment_result.py`:
```python
from sqlalchemy import Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from server.db.base_class import Base


class ExperimentResult(Base):
    __tablename__ = "experiment_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actual_request_rate: Mapped[float] = mapped_column(Float, nullable=False)
    max_request_concurrency: Mapped[int] = mapped_column(Integer, nullable=False)
    successful_requests: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_s: Mapped[float] = mapped_column(Float, nullable=False)
    total_input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    total_generated_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    request_throughput_reqs: Mapped[float] = mapped_column(Float, nullable=False)
    input_token_throughput_toks: Mapped[float] = mapped_column(Float, nullable=False)
    output_token_throughput_toks: Mapped[float] = mapped_column(Float, nullable=False)
    total_token_throughput_toks: Mapped[float] = mapped_column(Float, nullable=False)
    actual_concurrency: Mapped[float] = mapped_column(Float, nullable=False)
    goodput_reqs: Mapped[float | None] = mapped_column(Float, nullable=True)
    e2e_mean_ms: Mapped[float] = mapped_column(Float, nullable=False)
    e2e_median_ms: Mapped[float] = mapped_column(Float, nullable=False)
    e2e_p95_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    e2e_p99_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    ttft_mean_ms: Mapped[float] = mapped_column(Float, nullable=False)
    ttft_median_ms: Mapped[float] = mapped_column(Float, nullable=False)
    ttft_p95_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    ttft_p99_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    itl_mean_ms: Mapped[float] = mapped_column(Float, nullable=False)
    itl_median_ms: Mapped[float] = mapped_column(Float, nullable=False)
    itl_p95_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    itl_p99_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    itl_max_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    tpot_mean_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    tpot_median_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    tpot_p95_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    tpot_p99_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    peak_memory_usage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_memory_usage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    peak_tensor_core_usage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_tensor_core_usage_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
```

- [ ] **Step 4: Write Experiment model with relationships**

Create `backend/server/models/experiment.py`:
```python
from datetime import datetime, timezone

from sqlalchemy import Float, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.db.base_class import Base


class Experiment(Base):
    __tablename__ = "experiments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    compute_spec_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("compute_specs.id", ondelete="CASCADE"), nullable=False
    )
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("model_metadata.id", ondelete="CASCADE"), nullable=False
    )
    result_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("experiment_results.id", ondelete="CASCADE"), nullable=False
    )
    engine: Mapped[str] = mapped_column(String, nullable=False)
    engine_version: Mapped[str] = mapped_column(String, nullable=False)
    deployment_precision: Mapped[str] = mapped_column(String, nullable=False)
    isl: Mapped[int] = mapped_column(Integer, nullable=False)
    osl: Mapped[int] = mapped_column(Integer, nullable=False)
    request_rate: Mapped[float] = mapped_column(Float, nullable=False)
    total_requests: Mapped[int] = mapped_column(Integer, nullable=False)
    concurrency: Mapped[int] = mapped_column(Integer, nullable=False)
    deploy_param: Mapped[str | None] = mapped_column(String, nullable=True)
    resource_count: Mapped[int] = mapped_column(Integer, nullable=False)
    goodput_threshold: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lpai_link: Mapped[str | None] = mapped_column(String, nullable=True)
    remarks: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    updated_by: Mapped[str | None] = mapped_column(String, nullable=True, default="admin")

    compute_spec: Mapped["ComputeSpec"] = relationship("ComputeSpec", lazy="selectin")
    model: Mapped["ModelMetadata"] = relationship("ModelMetadata", lazy="selectin")
    result: Mapped["ExperimentResult"] = relationship("ExperimentResult", lazy="selectin")
```

- [ ] **Step 5: Update db/base.py to import all models**

Replace `backend/server/db/base.py`:
```python
from server.db.base_class import Base  # noqa: F401
from server.models.compute_spec import ComputeSpec  # noqa: F401
from server.models.model_metadata import ModelMetadata  # noqa: F401
from server.models.experiment_result import ExperimentResult  # noqa: F401
from server.models.experiment import Experiment  # noqa: F401
```

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "feat: add all 4 SQLAlchemy models (ComputeSpec, ModelMetadata, ExperimentResult, Experiment)"
```

---

### Task 3: All Pydantic Schemas

**Files:**
- Create: `backend/server/schemas/schemas.py`

- [ ] **Step 1: Write all schemas**

Create `backend/server/schemas/schemas.py`:
```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# --- ComputeSpec ---

class ComputeSpecBase(BaseModel):
    chip_name: str
    fp32_tflops: float
    tf32_tflops: float
    fp16_tflops: float
    fp8_tflops: float
    fp4_tflops: float
    interconnect_bandwidth: float
    memory_gb: float
    memory_bandwidth_tbs: float
    remarks: str | None = None
    updated_by: str


class ComputeSpecCreate(ComputeSpecBase):
    pass


class ComputeSpecUpdate(BaseModel):
    chip_name: str | None = None
    fp32_tflops: float | None = None
    tf32_tflops: float | None = None
    fp16_tflops: float | None = None
    fp8_tflops: float | None = None
    fp4_tflops: float | None = None
    interconnect_bandwidth: float | None = None
    memory_gb: float | None = None
    memory_bandwidth_tbs: float | None = None
    remarks: str | None = None
    updated_by: str | None = None


class ComputeSpec(ComputeSpecBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: datetime | None = None


# --- ModelMetadata ---

class ModelMetadataBase(BaseModel):
    model_name: str
    architecture: str
    model_type: str = "LLM"
    parameters_count: str
    active_parameters_count: str
    lpai_link: str | None = None
    updated_by: str | None = "admin"


class ModelMetadataCreate(ModelMetadataBase):
    pass


class ModelMetadataUpdate(BaseModel):
    model_name: str | None = None
    architecture: str | None = None
    model_type: str | None = None
    parameters_count: str | None = None
    active_parameters_count: str | None = None
    lpai_link: str | None = None
    updated_by: str | None = None


class ModelMetadata(ModelMetadataBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: datetime | None = None


# --- ExperimentResult ---

class ExperimentResultBase(BaseModel):
    actual_request_rate: float
    max_request_concurrency: int
    successful_requests: int
    duration_s: float
    total_input_tokens: int
    total_generated_tokens: int
    request_throughput_reqs: float
    input_token_throughput_toks: float
    output_token_throughput_toks: float
    total_token_throughput_toks: float
    actual_concurrency: float
    goodput_reqs: float | None = None
    e2e_mean_ms: float
    e2e_median_ms: float
    e2e_p95_ms: float | None = None
    e2e_p99_ms: float | None = None
    ttft_mean_ms: float
    ttft_median_ms: float
    ttft_p95_ms: float | None = None
    ttft_p99_ms: float | None = None
    itl_mean_ms: float
    itl_median_ms: float
    itl_p95_ms: float | None = None
    itl_p99_ms: float | None = None
    itl_max_ms: float | None = None
    tpot_mean_ms: float | None = None
    tpot_median_ms: float | None = None
    tpot_p95_ms: float | None = None
    tpot_p99_ms: float | None = None
    peak_memory_usage_pct: float | None = None
    avg_memory_usage_pct: float | None = None
    peak_tensor_core_usage_pct: float | None = None
    avg_tensor_core_usage_pct: float | None = None


class ExperimentResultCreate(ExperimentResultBase):
    pass


class ExperimentResultUpdate(BaseModel):
    actual_request_rate: float | None = None
    max_request_concurrency: int | None = None
    successful_requests: int | None = None
    duration_s: float | None = None
    total_input_tokens: int | None = None
    total_generated_tokens: int | None = None
    request_throughput_reqs: float | None = None
    input_token_throughput_toks: float | None = None
    output_token_throughput_toks: float | None = None
    total_token_throughput_toks: float | None = None
    actual_concurrency: float | None = None
    goodput_reqs: float | None = None
    e2e_mean_ms: float | None = None
    e2e_median_ms: float | None = None
    e2e_p95_ms: float | None = None
    e2e_p99_ms: float | None = None
    ttft_mean_ms: float | None = None
    ttft_median_ms: float | None = None
    ttft_p95_ms: float | None = None
    ttft_p99_ms: float | None = None
    itl_mean_ms: float | None = None
    itl_median_ms: float | None = None
    itl_p95_ms: float | None = None
    itl_p99_ms: float | None = None
    itl_max_ms: float | None = None
    tpot_mean_ms: float | None = None
    tpot_median_ms: float | None = None
    tpot_p95_ms: float | None = None
    tpot_p99_ms: float | None = None
    peak_memory_usage_pct: float | None = None
    avg_memory_usage_pct: float | None = None
    peak_tensor_core_usage_pct: float | None = None
    avg_tensor_core_usage_pct: float | None = None


class ExperimentResult(ExperimentResultBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# --- Experiment ---

class ExperimentBase(BaseModel):
    compute_spec_id: int
    model_id: int
    engine: str
    engine_version: str
    deployment_precision: str
    isl: int
    osl: int
    request_rate: float
    total_requests: int
    concurrency: int
    deploy_param: str | None = None
    resource_count: int
    goodput_threshold: str | None = None
    lpai_link: str | None = None
    remarks: str | None = None
    updated_by: str | None = "admin"


class ExperimentCreate(BaseModel):
    experiment_name: str | None = None
    compute_spec_id: int
    model_id: int
    engine: str
    engine_version: str
    deployment_precision: str
    isl: int
    osl: int
    request_rate: float
    total_requests: int
    concurrency: int
    deploy_param: str | None = None
    resource_count: int
    goodput_threshold: str | None = None
    lpai_link: str | None = None
    remarks: str | None = None
    updated_by: str | None = "admin"
    result: ExperimentResultCreate


class ExperimentUpdate(BaseModel):
    experiment_name: str | None = None
    compute_spec_id: int | None = None
    model_id: int | None = None
    engine: str | None = None
    engine_version: str | None = None
    deployment_precision: str | None = None
    isl: int | None = None
    osl: int | None = None
    request_rate: float | None = None
    total_requests: int | None = None
    concurrency: int | None = None
    deploy_param: str | None = None
    resource_count: int | None = None
    goodput_threshold: str | None = None
    lpai_link: str | None = None
    remarks: str | None = None
    updated_by: str | None = None
    result: ExperimentResultUpdate | None = None


class Experiment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    experiment_name: str | None = None
    compute_spec_id: int
    model_id: int
    result_id: int
    engine: str
    engine_version: str
    deployment_precision: str
    isl: int
    osl: int
    request_rate: float
    total_requests: int
    concurrency: int
    deploy_param: str | None = None
    resource_count: int
    goodput_threshold: str | None = None
    lpai_link: str | None = None
    remarks: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None
    compute_spec: ComputeSpec
    model: ModelMetadata
    result: ExperimentResult


class ExperimentSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    experiment_name: str | None = None
    compute_spec_id: int
    model_id: int
    result_id: int
    engine: str
    engine_version: str
    deployment_precision: str
    isl: int
    osl: int
    request_rate: float
    total_requests: int
    concurrency: int
    deploy_param: str | None = None
    resource_count: int
    goodput_threshold: str | None = None
    lpai_link: str | None = None
    remarks: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None
```

- [ ] **Step 2: Commit**

```bash
git add backend/server/schemas/
git commit -m "feat: add all Pydantic schemas (Base/Create/Update/Read pattern)"
```

---

### Task 4: Test Infrastructure

**Files:**
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Write test conftest.py with in-memory SQLite**

Create `backend/tests/conftest.py`:
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from server.db.base_class import Base
from server.db.session import get_db
from server.main import app

TEST_DB_URL = "sqlite://"
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
def sample_compute_spec(client):
    response = client.post("/api/v1/compute-specs", json={
        "chip_name": "NVIDIA H800",
        "fp32_tflops": 67.0,
        "tf32_tflops": 989.0,
        "fp16_tflops": 1979.0,
        "fp8_tflops": 3958.0,
        "fp4_tflops": 0.0,
        "interconnect_bandwidth": 900.0,
        "memory_gb": 80.0,
        "memory_bandwidth_tbs": 3.35,
        "updated_by": "admin"
    })
    return response.json()


@pytest.fixture
def sample_model(client):
    response = client.post("/api/v1/models", json={
        "model_name": "Llama-3-70B",
        "architecture": "Dense",
        "model_type": "LLM",
        "parameters_count": "70B",
        "active_parameters_count": "70B",
        "updated_by": "admin"
    })
    return response.json()


def _make_result():
    return {
        "actual_request_rate": 10.0,
        "max_request_concurrency": 32,
        "successful_requests": 100,
        "duration_s": 60.0,
        "total_input_tokens": 51200,
        "total_generated_tokens": 51200,
        "request_throughput_reqs": 12.5,
        "input_token_throughput_toks": 6400.0,
        "output_token_throughput_toks": 1600.0,
        "total_token_throughput_toks": 8000.0,
        "actual_concurrency": 30.0,
        "goodput_reqs": 12.0,
        "e2e_mean_ms": 100.0,
        "e2e_median_ms": 95.0,
        "e2e_p95_ms": 200.0,
        "e2e_p99_ms": 250.0,
        "ttft_mean_ms": 48.5,
        "ttft_median_ms": 45.0,
        "ttft_p95_ms": 80.0,
        "ttft_p99_ms": 100.0,
        "itl_mean_ms": 5.0,
        "itl_median_ms": 4.5,
        "itl_p95_ms": 10.0,
        "itl_p99_ms": 15.0,
    }


@pytest.fixture
def sample_experiment(client, sample_compute_spec, sample_model):
    payload = {
        "compute_spec_id": sample_compute_spec["id"],
        "model_id": sample_model["id"],
        "engine": "vLLM",
        "engine_version": "v0.6.3",
        "deployment_precision": "BF16",
        "isl": 512,
        "osl": 512,
        "request_rate": 10.0,
        "total_requests": 100,
        "concurrency": 32,
        "deploy_param": "tp=8, dp=1",
        "resource_count": 8,
        "updated_by": "admin",
        "result": _make_result()
    }
    response = client.post("/api/v1/experiments", json=payload)
    return response.json()
```

- [ ] **Step 2: Commit**

```bash
git add backend/tests/
git commit -m "feat: add test infrastructure with fixtures and sample data"
```

---

### Task 5: Experiment Naming Service

**Files:**
- Create: `backend/server/services/experiment_naming.py`

- [ ] **Step 1: Write the naming service**

Create `backend/server/services/experiment_naming.py`:
```python
from datetime import datetime

from sqlalchemy.orm import Session


def generate_experiment_name(
    db: Session,
    compute_spec_id: int,
    model_id: int,
    result_id: int,
) -> str:
    from server.models.compute_spec import ComputeSpec
    from server.models.model_metadata import ModelMetadata

    spec = db.query(ComputeSpec).filter(ComputeSpec.id == compute_spec_id).first()
    model = db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
    chip_name = spec.chip_name.replace(" ", "") if spec else "unknown"
    model_name = model.model_name.replace(" ", "") if model else "unknown"
    date_str = datetime.now().strftime("%y%m%d")
    suffix = str(result_id % 10000).zfill(4)
    return f"{model_name}_{chip_name}_{date_str}_{suffix}"


def normalize_name(name: str | None) -> str | None:
    if name is None:
        return None
    return name.replace(" ", "")
```

- [ ] **Step 2: Commit**

```bash
git add backend/server/services/experiment_naming.py
git commit -m "feat: add experiment auto-naming service"
```

---

### Task 6: CRUD Operations

**Files:**
- Create: `backend/server/crud/crud.py`

- [ ] **Step 1: Write all CRUD functions**

Create `backend/server/crud/crud.py`:
```python
import re

from sqlalchemy.orm import Session

from server.models.compute_spec import ComputeSpec
from server.models.model_metadata import ModelMetadata
from server.models.experiment_result import ExperimentResult
from server.models.experiment import Experiment
from server.schemas.schemas import (
    ComputeSpecCreate, ComputeSpecUpdate,
    ModelMetadataCreate, ModelMetadataUpdate,
    ExperimentResultCreate, ExperimentResultUpdate,
    ExperimentCreate, ExperimentUpdate,
)
from server.services.experiment_naming import generate_experiment_name, normalize_name


# --- ComputeSpec ---

def get_compute_specs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ComputeSpec).offset(skip).limit(limit).all()


def create_compute_spec(db: Session, data: ComputeSpecCreate):
    obj = ComputeSpec(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_compute_specs_batch(db: Session, items: list[ComputeSpecCreate]):
    objs = [ComputeSpec(**item.model_dump()) for item in items]
    db.add_all(objs)
    db.commit()
    for obj in objs:
        db.refresh(obj)
    return objs


def update_compute_spec(db: Session, spec_id: int, data: ComputeSpecUpdate):
    obj = db.query(ComputeSpec).filter(ComputeSpec.id == spec_id).first()
    if not obj:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_compute_spec(db: Session, spec_id: int):
    obj = db.query(ComputeSpec).filter(ComputeSpec.id == spec_id).first()
    if not obj:
        return None
    count = db.query(Experiment).filter(Experiment.compute_spec_id == spec_id).count()
    if count > 0:
        return count
    db.delete(obj)
    db.commit()
    return obj


# --- ModelMetadata ---

def get_models(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ModelMetadata).offset(skip).limit(limit).all()


def create_model(db: Session, data: ModelMetadataCreate):
    obj = ModelMetadata(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_models_batch(db: Session, items: list[ModelMetadataCreate]):
    objs = [ModelMetadata(**item.model_dump()) for item in items]
    db.add_all(objs)
    db.commit()
    for obj in objs:
        db.refresh(obj)
    return objs


def update_model(db: Session, model_id: int, data: ModelMetadataUpdate):
    obj = db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
    if not obj:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_model(db: Session, model_id: int):
    obj = db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
    if not obj:
        return None
    count = db.query(Experiment).filter(Experiment.model_id == model_id).count()
    if count > 0:
        return count
    db.delete(obj)
    db.commit()
    return obj


# --- Experiment ---

def get_experiments(
    db: Session,
    model_id: int | None = None,
    compute_spec_id: int | None = None,
    experiment_name_q: str | None = None,
    skip: int = 0,
    limit: int = 10000,
):
    query = db.query(Experiment)
    if model_id is not None:
        query = query.filter(Experiment.model_id == model_id)
    if compute_spec_id is not None:
        query = query.filter(Experiment.compute_spec_id == compute_spec_id)
    if experiment_name_q:
        cleaned = re.sub(r"\s+", "", experiment_name_q).lower()
        query = query.filter(
            Experiment.experiment_name != None  # noqa: E711
        )
        rows = query.all()
        matched = [
            r for r in rows
            if cleaned in re.sub(r"\s+", "", r.experiment_name or "").lower()
        ]
        return matched
    return query.offset(skip).limit(limit).all()


def get_experiments_count(
    db: Session,
    model_id: int | None = None,
    compute_spec_id: int | None = None,
    experiment_name_q: str | None = None,
):
    query = db.query(Experiment)
    if model_id is not None:
        query = query.filter(Experiment.model_id == model_id)
    if compute_spec_id is not None:
        query = query.filter(Experiment.compute_spec_id == compute_spec_id)
    if experiment_name_q:
        cleaned = re.sub(r"\s+", "", experiment_name_q).lower()
        query = query.filter(
            Experiment.experiment_name != None  # noqa: E711
        )
        rows = query.all()
        return len([
            r for r in rows
            if cleaned in re.sub(r"\s+", "", r.experiment_name or "").lower()
        ])
    return query.count()


def create_experiment(db: Session, data: ExperimentCreate):
    # 1. Create result first
    result = ExperimentResult(**data.result.model_dump())
    db.add(result)
    db.commit()
    db.refresh(result)

    # 2. Generate name
    name = normalize_name(data.experiment_name)
    if name is None:
        name = generate_experiment_name(db, data.compute_spec_id, data.model_id, result.id)

    # 3. Create experiment
    exp_data = data.model_dump(exclude={"result", "experiment_name"})
    exp = Experiment(experiment_name=name, result_id=result.id, **exp_data)
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


def create_experiments_batch(db: Session, items: list[ExperimentCreate]):
    return [create_experiment(db, item) for item in items]


def update_experiment(db: Session, exp_id: int, data: ExperimentUpdate):
    exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
    if not exp:
        return None
    # Update result if provided
    if data.result is not None:
        result = db.query(ExperimentResult).filter(
            ExperimentResult.id == exp.result_id
        ).first()
        if result:
            for key, value in data.result.model_dump(exclude_unset=True).items():
                setattr(result, key, value)
    # Update experiment fields
    update_data = data.model_dump(exclude_unset=True, exclude={"result"})
    if data.result is not None:
        update_data.pop("result", None)
    for key, value in update_data.items():
        setattr(exp, key, value)
    db.commit()
    db.refresh(exp)
    return exp


def delete_experiment(db: Session, exp_id: int):
    exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
    if not exp:
        return None
    result_id = exp.result_id
    db.delete(exp)
    # Cascade delete result
    result = db.query(ExperimentResult).filter(ExperimentResult.id == result_id).first()
    if result:
        db.delete(result)
    db.commit()
    return exp
```

- [ ] **Step 2: Commit**

```bash
git add backend/server/crud/crud.py
git commit -m "feat: add CRUD operations for all entities with experiment auto-naming"
```

---

### Task 7: API Endpoints

**Files:**
- Create: `backend/server/api/api_v1.py`

- [ ] **Step 1: Write all API endpoints**

Create `backend/server/api/api_v1.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from server.db.session import get_db
from server.crud import crud
from server.schemas.schemas import (
    ComputeSpec, ComputeSpecCreate, ComputeSpecUpdate,
    ModelMetadata, ModelMetadataCreate, ModelMetadataUpdate,
    Experiment, ExperimentSimple, ExperimentCreate, ExperimentUpdate,
)

router = APIRouter(prefix="/api/v1")


# --- Root ---

@router.get("")
def root():
    return {"message": "InfereVal API v1"}


# --- ComputeSpec ---

@router.get("/compute-specs", response_model=list[ComputeSpec])
def list_compute_specs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_compute_specs(db, skip=skip, limit=limit)


@router.post("/compute-specs", response_model=ComputeSpec, status_code=201)
def create_compute_spec(data: ComputeSpecCreate, db: Session = Depends(get_db)):
    return crud.create_compute_spec(db, data)


@router.post("/compute-specs/batch", response_model=list[ComputeSpec], status_code=201)
def create_compute_specs_batch(items: list[ComputeSpecCreate], db: Session = Depends(get_db)):
    return crud.create_compute_specs_batch(db, items)


@router.put("/compute-specs/{spec_id}", response_model=ComputeSpec)
def update_compute_spec(spec_id: int, data: ComputeSpecUpdate, db: Session = Depends(get_db)):
    result = crud.update_compute_spec(db, spec_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="ComputeSpec not found")
    return result


@router.delete("/compute-specs/{spec_id}", response_model=ComputeSpec)
def delete_compute_spec(spec_id: int, db: Session = Depends(get_db)):
    result = crud.delete_compute_spec(db, spec_id)
    if result is None:
        raise HTTPException(status_code=404, detail="ComputeSpec not found")
    if isinstance(result, int):
        raise HTTPException(
            status_code=409,
            detail=f"该芯片有 {result} 条关联实验，请先删除相关实验数据"
        )
    return result


# --- ModelMetadata ---

@router.get("/models", response_model=list[ModelMetadata])
def list_models(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_models(db, skip=skip, limit=limit)


@router.post("/models", response_model=ModelMetadata, status_code=201)
def create_model(data: ModelMetadataCreate, db: Session = Depends(get_db)):
    return crud.create_model(db, data)


@router.post("/models/batch", response_model=list[ModelMetadata], status_code=201)
def create_models_batch(items: list[ModelMetadataCreate], db: Session = Depends(get_db)):
    return crud.create_models_batch(db, items)


@router.put("/models/{model_id}", response_model=ModelMetadata)
def update_model(model_id: int, data: ModelMetadataUpdate, db: Session = Depends(get_db)):
    result = crud.update_model(db, model_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="ModelMetadata not found")
    return result


@router.delete("/models/{model_id}", response_model=ModelMetadata)
def delete_model(model_id: int, db: Session = Depends(get_db)):
    result = crud.delete_model(db, model_id)
    if result is None:
        raise HTTPException(status_code=404, detail="ModelMetadata not found")
    if isinstance(result, int):
        raise HTTPException(
            status_code=409,
            detail=f"该模型有 {result} 条关联实验，请先删除相关实验数据"
        )
    return result


# --- Experiment ---

@router.get("/experiments", response_model=list[Experiment])
def list_experiments(
    model_id: int | None = None,
    compute_spec_id: int | None = None,
    experiment_name_q: str | None = None,
    skip: int = 0,
    limit: int = 10000,
    db: Session = Depends(get_db),
):
    items = crud.get_experiments(
        db, model_id=model_id, compute_spec_id=compute_spec_id,
        experiment_name_q=experiment_name_q, skip=skip, limit=limit,
    )
    total = crud.get_experiments_count(
        db, model_id=model_id, compute_spec_id=compute_spec_id,
        experiment_name_q=experiment_name_q,
    )
    return Response(
        content=_serialize_list(items),
        media_type="application/json",
        headers={"X-Total-Count": str(total)},
    )


def _serialize_list(items):
    import json
    from pydantic import TypeAdapter
    adapter = TypeAdapter(list[Experiment])
    return adapter.dump_json(items).decode()


@router.post("/experiments", response_model=ExperimentSimple, status_code=201)
def create_experiment(data: ExperimentCreate, db: Session = Depends(get_db)):
    return crud.create_experiment(db, data)


@router.post("/experiments/batch", response_model=list[ExperimentSimple], status_code=201)
def create_experiments_batch(items: list[ExperimentCreate], db: Session = Depends(get_db)):
    return crud.create_experiments_batch(db, items)


@router.put("/experiments/{exp_id}", response_model=ExperimentSimple)
def update_experiment(exp_id: int, data: ExperimentUpdate, db: Session = Depends(get_db)):
    result = crud.update_experiment(db, exp_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return result


@router.delete("/experiments/{exp_id}", response_model=ExperimentSimple)
def delete_experiment(exp_id: int, db: Session = Depends(get_db)):
    result = crud.delete_experiment(db, exp_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return result
```

- [ ] **Step 2: Commit**

```bash
git add backend/server/api/api_v1.py
git commit -m "feat: add all API v1 endpoints for ComputeSpec, ModelMetadata, Experiment"
```

---

### Task 8: Main Application

**Files:**
- Create: `backend/server/main.py`

- [ ] **Step 1: Write FastAPI main app**

Create `backend/server/main.py`:
```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.db.base import Base  # noqa: F401 - ensure models are imported
from server.db.session import engine
from server.api.api_v1 import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="InfereVal - LLM 推理性能评估平台", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
```

- [ ] **Step 2: Commit**

```bash
git add backend/server/main.py
git commit -m "feat: add FastAPI main app with CORS and lifespan"
```

---

### Task 9: All Tests

**Files:**
- Create: `backend/tests/test_api.py`

- [ ] **Step 1: Write all API tests**

Create `backend/tests/test_api.py`:
```python
from tests.conftest import _make_result


# --- Root ---

def test_root(client):
    response = client.get("/api/v1")
    assert response.status_code == 200
    assert "message" in response.json()


# --- ComputeSpec ---

def test_create_compute_spec(client):
    response = client.post("/api/v1/compute-specs", json={
        "chip_name": "NVIDIA H800",
        "fp32_tflops": 67.0,
        "tf32_tflops": 989.0,
        "fp16_tflops": 1979.0,
        "fp8_tflops": 3958.0,
        "fp4_tflops": 0.0,
        "interconnect_bandwidth": 900.0,
        "memory_gb": 80.0,
        "memory_bandwidth_tbs": 3.35,
        "updated_by": "admin"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["chip_name"] == "NVIDIA H800"
    assert data["id"] is not None


def test_list_compute_specs(client, sample_compute_spec):
    response = client.get("/api/v1/compute-specs")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_update_compute_spec(client, sample_compute_spec):
    response = client.put(
        f"/api/v1/compute-specs/{sample_compute_spec['id']}",
        json={"fp32_tflops": 70.0}
    )
    assert response.status_code == 200
    assert response.json()["fp32_tflops"] == 70.0


def test_delete_compute_spec(client, sample_compute_spec):
    response = client.delete(f"/api/v1/compute-specs/{sample_compute_spec['id']}")
    assert response.status_code == 200


def test_delete_compute_spec_404(client):
    response = client.delete("/api/v1/compute-specs/9999")
    assert response.status_code == 404


def test_delete_compute_spec_with_experiments(client, sample_experiment):
    cs_id = sample_experiment["compute_spec_id"]
    response = client.delete(f"/api/v1/compute-specs/{cs_id}")
    assert response.status_code == 409
    assert "关联实验" in response.json()["detail"]


def test_batch_create_compute_specs(client):
    response = client.post("/api/v1/compute-specs/batch", json=[
        {
            "chip_name": "NVIDIA A100",
            "fp32_tflops": 19.5,
            "tf32_tflops": 312.0,
            "fp16_tflops": 624.0,
            "fp8_tflops": 0.0,
            "fp4_tflops": 0.0,
            "interconnect_bandwidth": 600.0,
            "memory_gb": 80.0,
            "memory_bandwidth_tbs": 2.0,
            "updated_by": "admin"
        },
        {
            "chip_name": "NVIDIA H20",
            "fp32_tflops": 44.0,
            "tf32_tflops": 148.0,
            "fp16_tflops": 296.0,
            "fp8_tflops": 593.0,
            "fp4_tflops": 0.0,
            "interconnect_bandwidth": 900.0,
            "memory_gb": 96.0,
            "memory_bandwidth_tbs": 4.0,
            "updated_by": "admin"
        },
    ])
    assert response.status_code == 201
    assert len(response.json()) == 2


# --- ModelMetadata ---

def test_create_model(client):
    response = client.post("/api/v1/models", json={
        "model_name": "Llama-3-70B",
        "architecture": "Dense",
        "model_type": "LLM",
        "parameters_count": "70B",
        "active_parameters_count": "70B",
        "updated_by": "admin"
    })
    assert response.status_code == 201
    assert response.json()["model_name"] == "Llama-3-70B"


def test_list_models(client, sample_model):
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_update_model(client, sample_model):
    response = client.put(
        f"/api/v1/models/{sample_model['id']}",
        json={"parameters_count": "70.1B"}
    )
    assert response.status_code == 200
    assert response.json()["parameters_count"] == "70.1B"


def test_delete_model(client, sample_model):
    response = client.delete(f"/api/v1/models/{sample_model['id']}")
    assert response.status_code == 200


def test_delete_model_404(client):
    response = client.delete("/api/v1/models/9999")
    assert response.status_code == 404


def test_delete_model_with_experiments(client, sample_experiment):
    m_id = sample_experiment["model_id"]
    response = client.delete(f"/api/v1/models/{m_id}")
    assert response.status_code == 409
    assert "关联实验" in response.json()["detail"]


def test_batch_create_models(client):
    response = client.post("/api/v1/models/batch", json=[
        {
            "model_name": "Qwen-72B",
            "architecture": "Dense",
            "parameters_count": "72B",
            "active_parameters_count": "72B",
            "updated_by": "admin"
        },
        {
            "model_name": "DeepSeek-V3",
            "architecture": "MoE",
            "parameters_count": "671B",
            "active_parameters_count": "37B",
            "updated_by": "admin"
        },
    ])
    assert response.status_code == 201
    assert len(response.json()) == 2


# --- Experiment ---

def test_create_experiment(client, sample_compute_spec, sample_model):
    payload = {
        "compute_spec_id": sample_compute_spec["id"],
        "model_id": sample_model["id"],
        "engine": "vLLM",
        "engine_version": "v0.6.3",
        "deployment_precision": "BF16",
        "isl": 512,
        "osl": 512,
        "request_rate": 10.0,
        "total_requests": 100,
        "concurrency": 32,
        "deploy_param": "tp=8, dp=1",
        "resource_count": 8,
        "updated_by": "admin",
        "result": _make_result()
    }
    response = client.post("/api/v1/experiments", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["result_id"] is not None
    assert data["experiment_name"] is not None
    assert "Llama-3-70B" in data["experiment_name"]


def test_create_experiment_with_name(client, sample_compute_spec, sample_model):
    payload = {
        "experiment_name": "my custom name",
        "compute_spec_id": sample_compute_spec["id"],
        "model_id": sample_model["id"],
        "engine": "vLLM",
        "engine_version": "v0.6.3",
        "deployment_precision": "BF16",
        "isl": 512,
        "osl": 512,
        "request_rate": 10.0,
        "total_requests": 100,
        "concurrency": 32,
        "resource_count": 8,
        "updated_by": "admin",
        "result": _make_result()
    }
    response = client.post("/api/v1/experiments", json=payload)
    assert response.status_code == 201
    assert response.json()["experiment_name"] == "mycustomname"


def test_list_experiments(client, sample_experiment):
    response = client.get("/api/v1/experiments")
    assert response.status_code == 200
    assert response.headers.get("x-total-count") is not None
    data = response.json()
    assert len(data) >= 1
    assert data[0]["compute_spec"] is not None
    assert data[0]["model"] is not None
    assert data[0]["result"] is not None


def test_list_experiments_filter_model(client, sample_experiment):
    response = client.get(
        "/api/v1/experiments",
        params={"model_id": sample_experiment["model_id"]}
    )
    assert response.status_code == 200
    assert int(response.headers["x-total-count"]) >= 1


def test_list_experiments_filter_compute_spec(client, sample_experiment):
    response = client.get(
        "/api/v1/experiments",
        params={"compute_spec_id": sample_experiment["compute_spec_id"]}
    )
    assert response.status_code == 200
    assert int(response.headers["x-total-count"]) >= 1


def test_list_experiments_filter_name(client, sample_experiment):
    response = client.get(
        "/api/v1/experiments",
        params={"experiment_name_q": "Llama"}
    )
    assert response.status_code == 200
    assert int(response.headers["x-total-count"]) >= 1


def test_list_experiments_filter_name_no_match(client, sample_experiment):
    response = client.get(
        "/api/v1/experiments",
        params={"experiment_name_q": "nonexistent"}
    )
    assert response.status_code == 200
    assert int(response.headers["x-total-count"]) == 0


def test_update_experiment(client, sample_experiment):
    response = client.put(
        f"/api/v1/experiments/{sample_experiment['id']}",
        json={"engine": "TRT-LLM"}
    )
    assert response.status_code == 200
    assert response.json()["engine"] == "TRT-LLM"


def test_update_experiment_with_result(client, sample_experiment):
    response = client.put(
        f"/api/v1/experiments/{sample_experiment['id']}",
        json={"result": {"e2e_mean_ms": 200.0}}
    )
    assert response.status_code == 200


def test_delete_experiment(client, sample_experiment):
    response = client.delete(f"/api/v1/experiments/{sample_experiment['id']}")
    assert response.status_code == 200


def test_delete_experiment_404(client):
    response = client.delete("/api/v1/experiments/9999")
    assert response.status_code == 404


def test_batch_create_experiments(client, sample_compute_spec, sample_model):
    payload = [
        {
            "compute_spec_id": sample_compute_spec["id"],
            "model_id": sample_model["id"],
            "engine": "vLLM",
            "engine_version": "v0.6.3",
            "deployment_precision": "BF16",
            "isl": 512,
            "osl": 512,
            "request_rate": 10.0,
            "total_requests": 100,
            "concurrency": 32,
            "resource_count": 8,
            "updated_by": "admin",
            "result": _make_result()
        },
        {
            "compute_spec_id": sample_compute_spec["id"],
            "model_id": sample_model["id"],
            "engine": "TRT-LLM",
            "engine_version": "v0.1.0",
            "deployment_precision": "FP8",
            "isl": 1024,
            "osl": 1024,
            "request_rate": 20.0,
            "total_requests": 200,
            "concurrency": 64,
            "resource_count": 4,
            "updated_by": "admin",
            "result": _make_result()
        },
    ]
    response = client.post("/api/v1/experiments/batch", json=payload)
    assert response.status_code == 201
    assert len(response.json()) == 2
```

- [ ] **Step 2: Run tests and verify they all pass**

Run: `cd /Users/guanyifan/Desktop/project/python-agent/backend && python -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_api.py
git commit -m "feat: add comprehensive API tests for all endpoints"
```

---

### Task 10: Seed Script

**Files:**
- Create: `backend/seed.py`

- [ ] **Step 1: Write seed data script**

Create `backend/seed.py`:
```python
"""Seed the database with sample data."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from server.db.base import Base
from server.db.session import engine, SessionLocal
from server.crud.crud import (
    create_compute_spec, create_compute_specs_batch,
    create_model, create_models_batch,
    create_experiment, create_experiments_batch,
)
from server.schemas.schemas import (
    ComputeSpecCreate, ModelMetadataCreate,
    ExperimentCreate, ExperimentResultCreate,
)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Create compute specs
        spec1 = create_compute_spec(db, ComputeSpecCreate(
            chip_name="NVIDIA H800", fp32_tflops=67.0, tf32_tflops=989.0,
            fp16_tflops=1979.0, fp8_tflops=3958.0, fp4_tflops=0.0,
            interconnect_bandwidth=900.0, memory_gb=80.0,
            memory_bandwidth_tbs=3.35, updated_by="admin"
        ))
        spec2 = create_compute_spec(db, ComputeSpecCreate(
            chip_name="NVIDIA H20", fp32_tflops=44.0, tf32_tflops=148.0,
            fp16_tflops=296.0, fp8_tflops=593.0, fp4_tflops=0.0,
            interconnect_bandwidth=900.0, memory_gb=96.0,
            memory_bandwidth_tbs=4.0, updated_by="admin"
        ))

        # Create models
        model1 = create_model(db, ModelMetadataCreate(
            model_name="Llama-3-70B", architecture="Dense",
            parameters_count="70B", active_parameters_count="70B",
            updated_by="admin"
        ))
        model2 = create_model(db, ModelMetadataCreate(
            model_name="DeepSeek-V3", architecture="MoE",
            parameters_count="671B", active_parameters_count="37B",
            updated_by="admin"
        ))

        # Create experiments
        result_data = ExperimentResultCreate(
            actual_request_rate=10.0, max_request_concurrency=32,
            successful_requests=100, duration_s=60.0,
            total_input_tokens=51200, total_generated_tokens=51200,
            request_throughput_reqs=12.5, input_token_throughput_toks=6400.0,
            output_token_throughput_toks=1600.0, total_token_throughput_toks=8000.0,
            actual_concurrency=30.0, e2e_mean_ms=100.0, e2e_median_ms=95.0,
            ttft_mean_ms=48.5, ttft_median_ms=45.0,
            itl_mean_ms=5.0, itl_median_ms=4.5,
        )
        create_experiment(db, ExperimentCreate(
            compute_spec_id=spec1.id, model_id=model1.id,
            engine="vLLM", engine_version="v0.6.3",
            deployment_precision="BF16", isl=512, osl=512,
            request_rate=10.0, total_requests=100, concurrency=32,
            resource_count=8, updated_by="admin", result=result_data
        ))

        print("Seed data created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
```

- [ ] **Step 2: Commit**

```bash
git add backend/seed.py
git commit -m "feat: add seed data script"
```

---

### Task 11: Cleanup Old Code

**Files:**
- Delete: `app/` directory
- Delete: `data/test.db`
- Delete: `docs/superpowers/specs/2026-05-18-llm-deployment-tracker-design.md` (old design)
- Delete: `docs/superpowers/plans/2026-05-18-llm-deployment-tracker.md` (old plan)

- [ ] **Step 1: Remove old app directory and outdated files**

```bash
cd /Users/guanyifan/Desktop/project/python-agent
rm -rf app/
rm -f data/test.db
rm -f docs/superpowers/specs/2026-05-18-llm-deployment-tracker-design.md
rm -rf docs/superpowers/plans/
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "chore: remove old app/ structure, migrated to backend/"
```
