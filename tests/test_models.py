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
