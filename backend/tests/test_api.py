import sys, pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.ml.predictor import PREDICTOR
from app.core.db import get_db


class MockSession:
    async def __aenter__(self): return self
    async def __aexit__(self, *a): pass
    async def flush(self): pass
    async def close(self): pass

    def add(self, obj):
        pass

    async def commit(self):
        pass

    async def execute(self, stmt):
        class MockScalars:
            def all(self): return []
            def __iter__(self): return iter([])
            def first(self): return None

        class MockResult:
            def scalars(self): return MockScalars()

        return MockResult()


async def override_db():
    yield MockSession()


app.dependency_overrides[get_db] = override_db


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_predict_legitimate(client):
    payload = {
        "transaction_id": "test-001", "step": 1,
        "transaction_type": "PAYMENT", "amount": 50.0,
        "customer_id": "C001", "merchant_id": "M001",
        "oldbalance_orig": 1000.0, "newbalance_orig": 950.0,
        "oldbalance_dest": 5000.0, "newbalance_dest": 5050.0,
        "is_flagged_fraud": False,
    }
    r = await client.post("/api/v1/predict", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["transaction_id"] == "test-001"
    assert isinstance(data["fraud_probability"], float)
    assert isinstance(data["is_fraudulent"], bool)


@pytest.mark.asyncio
async def test_predict_invalid_type(client):
    payload = {
        "transaction_id": "test-002", "step": 1,
        "transaction_type": "INVALID", "amount": 100.0,
        "customer_id": "C001", "merchant_id": "M001",
        "oldbalance_orig": 0, "newbalance_orig": 0,
        "oldbalance_dest": 0, "newbalance_dest": 0,
        "is_flagged_fraud": False,
    }
    r = await client.post("/api/v1/predict", json=payload)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_drift_status(client):
    r = await client.get("/api/v1/drift/status")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_prediction_history(client):
    r = await client.get("/api/v1/predictions/history")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_drift_history(client):
    r = await client.get("/api/v1/drift/history")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_model_loaded():
    assert PREDICTOR.loaded is True
    assert PREDICTOR.model is not None
    assert PREDICTOR.scaler is not None
    assert PREDICTOR.type_encoder is not None
