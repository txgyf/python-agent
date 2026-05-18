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
