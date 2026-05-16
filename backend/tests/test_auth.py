import pytest


@pytest.mark.asyncio
async def test_register_public(client):
    r = await client.post("/api/v1/auth/register", json={
        "username": "newuser", "email": "new@bank.com",
        "password": "testpass123", "roles": ["fraud_analyst"],
    })
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@bank.com"
    assert "fraud_analyst" in data["roles"]
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    r = await client.post("/api/v1/auth/register", json={
        "username": "admin", "email": "admin2@bank.com",
        "password": "testpass123", "roles": ["fraud_analyst"],
    })
    assert r.status_code == 400
    assert "already" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_short_password(client):
    r = await client.post("/api/v1/auth/register", json={
        "username": "user2", "email": "u2@bank.com",
        "password": "short", "roles": ["fraud_analyst"],
    })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client):
    r = await client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "admin123",
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "admin"
    assert "admin" in data["user"]["roles"]


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    r = await client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "wrongpass",
    })
    assert r.status_code == 401
    assert "Invalid" in r.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    r = await client.post("/api/v1/auth/login", json={
        "username": "ghost", "password": "whatever123",
    })
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(client):
    r = await client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "admin123",
    })
    token = r.json()["access_token"]
    r2 = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["username"] == "admin"


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_invalid_token(client):
    r = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_login_response_has_user_data(client):
    r = await client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "admin123",
    })
    data = r.json()
    user = data["user"]
    assert user["id"] is not None
    assert user["username"] == "admin"
    assert user["email"] == "admin@bank.com"
    assert isinstance(user["roles"], list)
    assert user["is_active"] is True
