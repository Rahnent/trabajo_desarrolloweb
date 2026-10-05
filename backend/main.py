from fastapi import FastAPI, HTTPException, Header, status

app = FastAPI(title="Backend API")

BACKEND_SHARED_SECRET = "gateway-api-secret-456"

PRODUCTS = [
    {"id": 1, "name": "Laptop Pro", "price": 1200},
    {"id": 2, "name": "Mouse Inalámbrico", "price": 25}
]

ORDERS = [
    {"id": 101, "item": "Laptop Pro", "status": "shipped"}
]

def verify_gateway(x_gateway_secret: str):
    if x_gateway_secret != BACKEND_SHARED_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado"
        )

@app.get("/health")
def health():
    return {"status": "ok", "service": "backend"}

@app.get("/products")
def get_products(x_gateway_secret: str = Header(None)):
    verify_gateway(x_gateway_secret)
    return PRODUCTS

@app.get("/orders")
def get_orders(x_gateway_secret: str = Header(None)):
    verify_gateway(x_gateway_secret)
    return ORDERS

@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    x_gateway_secret: str = Header(None),
    x_authenticated_roles: str = Header(None)
):
    verify_gateway(x_gateway_secret)
    
    roles = [r.strip() for r in (x_authenticated_roles or "").split(",")]
    if "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación reservada para administradores"
        )
    
    global PRODUCTS
    PRODUCTS = [p for p in PRODUCTS if p["id"] != product_id]
    return {"status": "deleted", "id": product_id}