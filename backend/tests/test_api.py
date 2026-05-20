from tests.conftest import _make_result

# Import models to ensure they're registered with Base.metadata
from server.models.compute_spec import ComputeSpec  # noqa: F401
from server.models.model_metadata import ModelMetadata  # noqa: F401
from server.models.experiment import Experiment  # noqa: F401
from server.models.experiment_result import ExperimentResult  # noqa: F401


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
