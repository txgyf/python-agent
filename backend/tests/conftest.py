import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from server.db.base_class import Base
from server.db.session import get_db
from server.main import app

TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, pool_pre_ping=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Global test connection to ensure all sessions use the same in-memory database
test_connection = test_engine.connect()


def override_get_db():
    db = TestSessionLocal(bind=test_connection)
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
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
