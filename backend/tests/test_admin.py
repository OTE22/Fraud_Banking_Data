import pytest


@pytest.mark.asyncio
async def test_list_users_admin_allowed(client):
    r = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    users = r2.json()
    assert isinstance(users, list)
    assert len(users) >= 2
    usernames = [u["username"] for u in users]
    assert "admin" in usernames
    assert "analyst1" in usernames


@pytest.mark.asyncio
async def test_list_users_nonadmin_forbidden(client):
    r = await client.post("/api/v1/auth/login", json={"username": "analyst1", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 403


@pytest.mark.asyncio
async def test_list_users_unauthenticated(client):
    r = await client.get("/api/v1/admin/users")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_user_admin_allowed(client):
    r = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = await client.post("/api/v1/admin/users", json={
        "username": "newguy", "email": "newguy@bank.com",
        "password": "testpass123", "roles": ["fraud_analyst"],
    }, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    data = r2.json()
    assert data["username"] == "newguy"
    assert "fraud_analyst" in data["roles"]


@pytest.mark.asyncio
async def test_create_user_nonadmin_forbidden(client):
    r = await client.post("/api/v1/auth/login", json={"username": "analyst1", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = await client.post("/api/v1/admin/users", json={
        "username": "hacker", "email": "h@k.com",
        "password": "testpass123", "roles": ["admin"],
    }, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 403


@pytest.mark.asyncio
async def test_assign_role_admin_allowed(client):
    r = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = await client.put("/api/v1/admin/users/2/role", json={
        "username": "analyst1", "email": "analyst1@bank.com",
        "password": "changeme123", "roles": ["fraud_analyst", "auditor"],
    }, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    data = r2.json()
    assert "auditor" in data["roles"]
    assert "fraud_analyst" in data["roles"]


@pytest.mark.asyncio
async def test_assign_role_nonadmin_forbidden(client):
    r = await client.post("/api/v1/auth/login", json={"username": "analyst1", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = await client.put("/api/v1/admin/users/2/role", json={
        "username": "analyst1", "email": "a@b.com",
        "password": "longenoughpw", "roles": ["admin"],
    }, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 403


@pytest.mark.asyncio
async def test_assign_role_nonexistent_user(client):
    r = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = await client.put("/api/v1/admin/users/999/role", json={
        "username": "ghost", "email": "g@b.com",
        "password": "longenoughpw", "roles": ["fraud_analyst"],
    }, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_admin_roles_endpoint(client):
    r = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/admin/roles", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    roles = r2.json()
    assert isinstance(roles, list)
    assert len(roles) == 6
    role_names = [rr["name"] for rr in roles]
    assert "admin" in role_names
    assert "fraud_analyst" in role_names


@pytest.mark.asyncio
async def test_admin_audit_logs(client):
    r = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert isinstance(r2.json(), list)
