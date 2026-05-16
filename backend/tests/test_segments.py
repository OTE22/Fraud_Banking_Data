import pytest


@pytest.mark.asyncio
async def test_segment_predict_admin_allowed(client):
    r = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = await client.post("/api/v1/segments/predict", params={"n_clusters": 4}, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    data = r2.json()
    assert "labels" in data
    assert "centroids" in data
    assert "n_clusters" in data
    assert data["n_clusters"] == 4


@pytest.mark.asyncio
async def test_segment_predict_nonadmin_forbidden(client):
    r = await client.post("/api/v1/auth/login", json={"username": "analyst1", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = await client.post("/api/v1/segments/predict", params={"n_clusters": 4}, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 403


@pytest.mark.asyncio
async def test_segment_predict_unauthenticated(client):
    r = await client.post("/api/v1/segments/predict", params={"n_clusters": 4})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_segments_info(client):
    r = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/segments/info", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    data = r2.json()
    assert "loaded" in data
    if data["loaded"]:
        assert "n_clusters" in data
        assert "feature_cols" in data
