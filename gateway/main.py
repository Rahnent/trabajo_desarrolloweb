import os
import httpx
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="API Gateway")

AUTH_URL = os.getenv("AUTH_URL", "http://auth-service:8100")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-api:9000")
VAULT_URL = os.getenv("VAULT_URL", "http://vault:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "dev-only-token")

SECRETS = {}

async def load_secrets_from_vault():
    global SECRETS
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{VAULT_URL}/v1/secret/data/gateway",
                headers={"X-Vault-Token": VAULT_TOKEN},
                timeout=3.0
            )
            if res.status_code == 200:
                data = res.json()["data"]["data"]
                SECRETS = data
                return
    except Exception:
        pass
    
    SECRETS = {
        "backend_shared_secret": "gateway-api-secret-456",
        "auth_introspection_secret": "gateway-auth-secret-789"
    }

@app.on_event("startup")
async def on_startup():
    await load_secrets_from_vault()

@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}

class LoginBody(BaseModel):
    username: str
    password: str

@app.post("/auth/login")
async def gateway_login(creds: LoginBody, response: Response):
    async with httpx.AsyncClient() as client:
        try:
            auth_res = await client.post(f"{AUTH_URL}/login", json=creds.dict())
        except httpx.RequestError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth Service no disponible")
            
        if auth_res.status_code != 200:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
        
        token_data = auth_res.json()
        token = token_data["access_token"]
        
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            samesite="lax",
            secure=False
        )
        return {"status": "logged_in"}

async def get_current_user(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sin sesión activa")
    
    introspection_secret = SECRETS.get("auth_introspection_secret", "gateway-auth-secret-789")
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(
                f"{AUTH_URL}/introspect",
                json={"token": token},
                headers={"X-Auth-Secret": introspection_secret}
            )
        except httpx.RequestError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth Service no disponible")
        
        if res.status_code != 200:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error de validación")
        
        data = res.json()
        if not data.get("active"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión expirada o inválida")
        
        return data, token

@app.get("/auth/me")
async def get_me(request: Request):
    user_info, _ = await get_current_user(request)
    return user_info

@app.post("/auth/logout")
async def gateway_logout(request: Request, response: Response):
    token = request.cookies.get("session_token")
    if token:
        introspection_secret = SECRETS.get("auth_introspection_secret", "gateway-auth-secret-789")
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{AUTH_URL}/logout",
                    json={"token": token},
                    headers={"X-Auth-Secret": introspection_secret}
                )
            except Exception:
                pass
    
    response.delete_cookie(key="session_token")
    return {"status": "logged_out"}

@app.api_route("/api/{path:path}", methods=["GET", "POST", "DELETE"])
async def proxy_backend(path: str, request: Request):
    user_info, _ = await get_current_user(request)
    
    backend_secret = SECRETS.get("backend_shared_secret", "gateway-api-secret-456")
    forward_headers = {
        "X-Gateway-Secret": backend_secret,
        "X-Authenticated-User": user_info["user_id"],
        "X-Authenticated-Username": user_info["username"],
        "X-Authenticated-Roles": ",".join(user_info["roles"])
    }
    
    if request.method == "DELETE" and "admin" not in user_info["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
    
    async with httpx.AsyncClient() as client:
        try:
            req_body = await request.body()
            be_res = await client.request(
                method=request.method,
                url=f"{BACKEND_URL}/{path}",
                headers=forward_headers,
                content=req_body
            )
            return Response(content=be_res.content, status_code=be_res.status_code, media_type="application/json")
        except httpx.RequestError:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Backend no disponible")

app.mount("/", StaticFiles(directory="/app/frontend", html=True), name="frontend")