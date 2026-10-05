import pytest
from httpx import AsyncClient, ASGITransport
from auth_service.main import app as auth_app
from backend.main import app as backend_app

@pytest.mark.asyncio
async def test_auth_login_success():
    transport = ASGITransport(app=auth_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/login", json={"username": "ana", "password": "1234"})
        assert res.status_code == 200
        assert "access_token" in res.json()

@pytest.mark.asyncio
async def test_auth_login_invalid():
    transport = ASGITransport(app=auth_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/login", json={"username": "ana", "password": "err"})
        assert res.status_code == 401

@pytest.mark.asyncio
async def test_backend_direct_bypass_rejected():
    transport = ASGITransport(app=backend_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/products")
        assert res.status_code == 403

@pytest.mark.asyncio
async def test_backend_admin_authorization():
    transport = ASGITransport(app=backend_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.delete(
            "/products/1",
            headers={
                "X-Gateway-Secret": "gateway-api-secret-456",
                "X-Authenticated-Roles": "user"
            }
        )
        assert res.status_code == 403

        res_admin = await client.delete(
            "/products/1",
            headers={
                "X-Gateway-Secret": "gateway-api-secret-456",
                "X-Authenticated-Roles": "user,admin"
            }
        )
        assert res_admin.status_code == 200