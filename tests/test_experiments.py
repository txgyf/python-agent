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
