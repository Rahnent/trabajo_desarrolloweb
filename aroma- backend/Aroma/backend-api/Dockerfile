# Usamos una imagen ligera de Python
FROM python:3.10-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los archivos de requerimientos e instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código (tu backend_api.py o gateway.py)
COPY . .

# Exponemos el puerto (cambiar según el servicio, ej. 8000 o 9000)
EXPOSE 9000

# Comando para levantar FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]