import pytest
import httpx

BASE_URL = "http://localhost:8000"
BACKEND_DIRECT_URL = "http://localhost:9000"

def test_backend_bypass_blocked():
    res = httpx.get(f"{BACKEND_DIRECT_URL}/products")
    assert res.status_code == 403

def test_full_stack_lifecycle():
    with httpx.Client(base_url=BASE_URL) as client:
        res_fail = client.post("/auth/login", json={"username": "ana", "password": "bad"})
        assert res_fail.status_code == 401

        res_login = client.post("/auth/login", json={"username": "ana", "password": "1234"})
        assert res_login.status_code == 200
        assert "session_token" in client.cookies

        res_me = client.get("/auth/me")
        assert res_me.status_code == 200
        assert res_me.json()["username"] == "ana"

        res_prod = client.get("/api/products")
        assert res_prod.status_code == 200

        res_del_denied = client.delete("/api/products/1")
        assert res_del_denied.status_code == 403

        res_logout = client.post("/auth/logout")
        assert res_logout.status_code == 200

        res_me_after = client.get("/auth/me")
        assert res_me_after.status_code == 401

def test_admin_deletion():
    with httpx.Client(base_url=BASE_URL) as client:
        res_login = client.post("/auth/login", json={"username": "ernesto", "password": "admin123"})
        assert res_login.status_code == 200

        res_del = client.delete("/api/products/1")
        assert res_del.status_code == 200
        assert res_del.json()["status"] == "deleted"