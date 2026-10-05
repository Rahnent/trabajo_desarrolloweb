import secrets
from fastapi import FastAPI, HTTPException, Header, status
from pydantic import BaseModel

app = FastAPI(title="Auth Service")

USERS = {
    "ana": {
        "user_id": "USR-001",
        "password": "1234",
        "roles": ["user"]
    },
    "ernesto": {
        "user_id": "USR-003",
        "password": "admin123",
        "roles": ["user", "admin"]
    }
}

SESSIONS = {}
EXPECTED_INTROSPECTION_SECRET = "gateway-auth-secret-789"

class LoginRequest(BaseModel):
    username: str
    password: str

class IntrospectRequest(BaseModel):
    token: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}

@app.post("/login")
def login(creds: LoginRequest):
    user = USERS.get(creds.username)
    if not user or user["password"] != creds.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    token = secrets.token_hex(32)
    SESSIONS[token] = {
        "user_id": user["user_id"],
        "username": creds.username,
        "roles": user["roles"]
    }
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 900
    }

@app.post("/introspect")
def introspect(payload: IntrospectRequest, x_auth_secret: str = Header(None)):
    if x_auth_secret != EXPECTED_INTROSPECTION_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    
    session = SESSIONS.get(payload.token)
    if not session:
        return {"active": False}
    
    return {
        "active": True,
        "user_id": session["user_id"],
        "username": session["username"],
        "roles": session["roles"]
    }

@app.post("/logout")
def logout(payload: IntrospectRequest, x_auth_secret: str = Header(None)):
    if x_auth_secret != EXPECTED_INTROSPECTION_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    
    if payload.token in SESSIONS:
        del SESSIONS[payload.token]
    
    return {"status": "revoked"}