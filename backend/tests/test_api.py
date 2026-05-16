import pytest
from app.ml.predictor import PREDICTOR


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data
    assert "db_connected" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_predict_legitimate(client):
    r = await client.post("/api/v1/predict", json={
        "transaction_id": "test-001", "step": 1,
        "transaction_type": "PAYMENT", "amount": 50.0,
        "customer_id": "C001", "merchant_id": "M001",
        "oldbalance_orig": 1000.0, "newbalance_orig": 950.0,
        "oldbalance_dest": 5000.0, "newbalance_dest": 5050.0,
        "is_flagged_fraud": False,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["transaction_id"] == "test-001"
    assert isinstance(data["fraud_probability"], float)
    assert isinstance(data["is_fraudulent"], bool)
    assert data["model_version"] == "v1.0"


@pytest.mark.asyncio
async def test_predict_suspicious(client):
    r = await client.post("/api/v1/predict", json={
        "transaction_id": "test-sus-001", "step": 1,
        "transaction_type": "CASH_OUT", "amount": 850000.0,
        "customer_id": "C001", "merchant_id": "M001",
        "oldbalance_orig": 100000.0, "newbalance_orig": 5000.0,
        "oldbalance_dest": 0.0, "newbalance_dest": 850000.0,
        "is_flagged_fraud": False,
    })
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_predict_invalid_type(client):
    r = await client.post("/api/v1/predict", json={
        "transaction_id": "test-002", "step": 1,
        "transaction_type": "INVALID", "amount": 100.0,
        "customer_id": "C001", "merchant_id": "M001",
        "oldbalance_orig": 0, "newbalance_orig": 0,
        "oldbalance_dest": 0, "newbalance_dest": 0,
        "is_flagged_fraud": False,
    })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_predict_missing_fields(client):
    r = await client.post("/api/v1/predict", json={
        "transaction_id": "test-003", "amount": 100.0,
    })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_prediction_history(client):
    r = await client.get("/api/v1/predictions/history")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_prediction_history_with_limit(client):
    r = await client.get("/api/v1/predictions/history?limit=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_prediction_logs(client):
    r = await client.get("/api/v1/predictions/logs")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_prediction_log_not_found(client):
    r = await client.get("/api/v1/predictions/log/nonexistent-tx")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_drift_status(client):
    r = await client.get("/api/v1/drift/status")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_drift_history(client):
    r = await client.get("/api/v1/drift/history")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_drift_run(client):
    r = await client.post("/api/v1/drift/run")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_feast_info(client):
    r = await client.get("/api/v1/features/feast")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_ensemble_score(client):
    r = await client.post("/api/v1/fraud/ensemble-score", json={
        "transaction_id": "ens-001", "ml_score": 0.6,
        "rules_score": 0.4, "anomaly_score": 0.2,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["transaction_id"] == "ens-001"
    assert "final_score" in data
    assert "decision" in data
    assert data["decision"] in ("fraud", "legitimate")


def test_model_loaded():
    assert PREDICTOR.loaded is True
    assert PREDICTOR.model is not None
    assert PREDICTOR.scaler is not None
    assert PREDICTOR.type_encoder is not None


def test_anomaly_model_loaded():
    assert PREDICTOR.anomaly_model is not None
    assert PREDICTOR.anomaly_scaler is not None
    assert PREDICTOR.anomaly_feature_cols is not None


@pytest.mark.asyncio
async def test_anomaly_predict_endpoint(client):
    r = await client.post("/api/v1/predict/anomaly", json={
        "transaction_id": "test_anom_1", "transaction_type": "CASH_OUT",
        "amount": 500000.0, "oldbalance_orig": 600000.0,
        "newbalance_orig": 0.0, "oldbalance_dest": 0.0,
        "newbalance_dest": 500000.0, "is_flagged_fraud": False,
        "customer_id": "C999", "merchant_id": "M999",
        "step": 1,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["transaction_id"] == "test_anom_1"
    assert data["anomaly_score"] is not None
    assert data["is_anomaly"] is not None


@pytest.mark.asyncio
async def test_anomaly_csv_export(client):
    r = await client.post("/api/v1/predict", json={
        "transaction_id": "csv_export_1", "transaction_type": "CASH_OUT",
        "amount": 10000, "oldbalance_orig": 50000, "newbalance_orig": 40000,
        "oldbalance_dest": 0, "newbalance_dest": 10000,
        "is_flagged_fraud": False, "customer_id": "C1", "merchant_id": "M1", "step": 1,
    })
    assert r.status_code == 200
    r2 = await client.get("/api/v1/predict/anomaly/export?limit=10")
    assert r2.status_code == 200
    assert "text/csv" in r2.headers.get("content-type", "")
    body = r2.text
    assert "transaction_id" in body
    assert "anomaly_score" in body
    header_line = body.split("\n")[0]
    assert header_line.startswith("transaction_id")
