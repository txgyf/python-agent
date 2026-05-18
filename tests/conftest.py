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