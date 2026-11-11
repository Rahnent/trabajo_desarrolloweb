from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

app = FastAPI(title="API Gateway con Vault - Aroma y Café")

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "token-secreto-aroma")

class ItemCompra(BaseModel):
    producto: str
    cantidad: int

def obtener_secreto_de_vault():
    """Consulta la caja fuerte de Vault para extraer el secreto compartido de integración"""
    url = f"{VAULT_ADDR}/v1/secret/data/gateway"
    headers = {"X-Vault-Token": VAULT_TOKEN}
    try:
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data["data"]["data"].get("backend_shared_secret", "gateway-api-secret-456")
    except Exception:
        pass
    # Valor por defecto en caso de que Vault esté iniciando
    return "gateway-api-secret-456"

@app.get("/")
def read_root():
    return {"message": "API Gateway con Vault en línea y respondiendo."}

@app.post("/api/comprar")
def procesar_compra(item: ItemCompra):
    # 1. Obtenemos el secreto dinámicamente desde HashiCorp Vault
    secret_key = obtener_secreto_de_vault()
    
    # Preparamos las cabeceras secretas entre servicios
    headers_internos = {
        "X-Gateway-Secret": secret_key,
        "X-Client-Source": "Web-Aroma-Client"
    }

    stock_url = f"http://inventory-service:9000/api/inventario/stock/{item.producto}"
    descontar_url = f"http://inventory-service:9000/api/inventario/descontar/{item.producto}"
    
    try:
        # 2. Consultar stock enviando la cabecera secreta del Gateway
        response_stock = requests.get(stock_url, headers=headers_internos)
        if response_stock.status_code != 200:
            raise HTTPException(status_code=response_stock.status_code, detail="Error al consultar el inventario o acceso no autorizado.")
        
        data = response_stock.json()
        stock_disponible = data.get("stock", 0)
        
        if stock_disponible < item.cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente.")
        
        # 3. Descontar stock en el inventario enviando también la cabecera secreta
        response_descuento = requests.post(descontar_url, json={"cantidad": item.cantidad}, headers=headers_internos)
        if response_descuento.status_code != 200:
            raise HTTPException(status_code=500, detail="Error al descontar el stock.")
            
        resultado_inventario = response_descuento.json()
        
        return {
            "status": "success", 
            "message": f"Compra exitosa de {item.cantidad} {item.producto}(s) mediada por API Gateway y Vault.",
            "inventario_actualizado": resultado_inventario
        }
            
    except requests.exceptions.RequestException as e:
         raise HTTPException(status_code=502, detail=f"No se pudo conectar con el servicio interno: {str(e)}")