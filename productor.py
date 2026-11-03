import stomp
import json
import argparse
from decimal import Decimal, InvalidOperation
import xml.etree.ElementTree as ET

destino = '/queue/pedidos'

def construir_mensaje(formato: str, pedido: dict, texto: str) -> tuple[str, str]:
    if formato == "texto":
        return texto, "text/plain; charset=utf-8"
    if formato == "fijo":
        identificador = str(pedido["id"])
        cliente = str(pedido["cliente"])
        monto = Decimal(pedido["monto"])
        monto_campo = f"{monto:010.2f}"
        
        if not (identificador.isascii() and identificador.isdigit() and len(identificador) <= 6):
            raise ValueError("formato fijo, --id debe tener hasta 6 digitos")
        if len(cliente) > 20 or any(ord(c) > 127 for c in cliente):
            raise ValueError("formato fijo, --cliente debe tener hasta 20 caracteres ASCII")
            
        return f"{identificador.zfill(6)}{cliente:<20}{monto_campo}", "text/plain; charset=utf-8"
    if formato == "json":
        return json.dumps(pedido, ensure_ascii=False), "application/json; charset=utf-8"
    if formato == "xml":
        raiz = ET.Element("pedido")
        for clave, valor in pedido.items():
            ET.SubElement(raiz, clave).text = str(valor)
        return ET.tostring(raiz, encoding="utf-8", xml_declaration=True).decode("utf-8"), "application/xml; charset=utf-8"
    
    raise ValueError(f"formato desconocido {formato}")


def main():
    parser = argparse.ArgumentParser(description="Productor Stomp")
    parser.add_argument("--formato", choices=["texto", "fijo", "xml", "json"], default="texto")
    parser.add_argument("--mensaje", default="hola desde stomp")
    parser.add_argument("--id", default="123")
    parser.add_argument("--cliente", default="wells")
    parser.add_argument("--monto", default="123.45")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=61613)
    parser.add_argument("--usuario", default="admin") 
    parser.add_argument("--password", default="admin")

    args = parser.parse_args()

    try:
        monto = Decimal(args.monto)
        if not monto.is_finite():
            raise ValueError("El monto debe ser un número decimal finito.")
    except InvalidOperation as exc:
        parser.error(f"El monto proporcionado no es un número decimal válido: {args.monto}")
        
    pedido = {"id": args.id, "cliente": args.cliente, "monto": str(monto)} 
    
    try:
        cuerpo, mime = construir_mensaje(args.formato, pedido, args.mensaje)
    except ValueError as exc:
        parser.error(str(exc))

    conexion = stomp.Connection12([(args.host, args.port)], vhost="/")
    try:
        conexion.connect(args.usuario, args.password, wait=True)
        conexion.send(body=cuerpo, destination=destino, headers={"content-type": mime, "x.formato": args.formato, "persistent": "true"})
        print(f"Mensaje enviado a {destino} formato {args.formato}: \n{cuerpo}")
    finally:
        if conexion.is_connected():
            conexion.disconnect()

if __name__ == "__main__":
    main()