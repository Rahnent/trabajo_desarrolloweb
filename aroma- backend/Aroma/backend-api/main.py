from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import secrets
import os

app = FastAPI(title="Backend Inventory - Aroma y Café")

# Obtenemos el secreto compartido que viene desde el Gateway 
INTERNAL_GATEWAY_SECRET = os.getenv("INTERNAL_GATEWAY_SECRET", "gateway-api-secret-456")

def verify_gateway(x_gateway_secret: str = Header(default="")):
    # Compara si la info del secret es la misma
    if not secrets.compare_digest(x_gateway_secret, INTERNAL_GATEWAY_SECRET):
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado: Se prohíbe el acceso directo al backend sin el Gateway."
        )

fake_db = {
    "latte": 15,
    "espresso": 20,
    "capuchino": 5
}

class ActualizarStock(BaseModel):
    cantidad: int

# depende del gateway asi lo verifica y no acepta llamado de cualquiera
@app.get("/api/inventario/stock/{producto}", dependencies=[Depends(verify_gateway)])
def consultar_stock(producto: str):
    producto_lower = producto.lower()
    if producto_lower in fake_db:
        return {"producto": producto_lower, "stock": fake_db[producto_lower]}
    return {"producto": producto_lower, "stock": 0}

@app.post("/api/inventario/descontar/{producto}", dependencies=[Depends(verify_gateway)])
def descontar_stock(producto: str, item: ActualizarStock):
    producto_lower = producto.lower()
    if producto_lower not in fake_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    
    if fake_db[producto_lower] < item.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente para descontar.")
    
    fake_db[producto_lower] -= item.cantidad
    return {"status": "success", "producto": producto_lower, "stock_restante": fake_db[producto_lower]}