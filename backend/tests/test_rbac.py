import pytest


@pytest.mark.asyncio
async def test_admin_can_access_fraud_alerts(client):
    r = await client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "admin123",
    })
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/fraud/alerts", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_analyst_can_access_fraud_alerts(client):
    r = await client.post("/api/v1/auth/login", json={
        "username": "analyst1", "password": "admin123",
    })
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/fraud/alerts", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_nonadmin_cannot_list_users(client):
    r = await client.post("/api/v1/auth/login", json={
        "username": "analyst1", "password": "admin123",
    })
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 403


@pytest.mark.asyncio
async def test_unauthorized_access_returns_401(client):
    r = await client.get("/api/v1/fraud/alerts")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_admin_can_access_admin_roles(client):
    r = await client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "admin123",
    })
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/admin/roles", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_analyst_cannot_access_admin_roles(client):
    r = await client.post("/api/v1/auth/login", json={
        "username": "analyst1", "password": "admin123",
    })
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/admin/roles", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_access_audit_logs(client):
    r = await client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "admin123",
    })
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_analyst_cannot_access_audit_logs(client):
    r = await client.post("/api/v1/auth/login", json={
        "username": "analyst1", "password": "admin123",
    })
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 403


@pytest.mark.asyncio
async def test_all_roles_can_access_me(client):
    for user, pw in [("admin", "admin123"), ("analyst1", "admin123")]:
        r = await client.post("/api/v1/auth/login", json={"username": user, "password": pw})
        assert r.status_code == 200
        token = r.json()["access_token"]
        r2 = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 200
        assert r2.json()["username"] == user
