# ============================================================================
# Dockerfile - Backend FastAPI
# ============================================================================

FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Hacer el entrypoint ejecutable
RUN chmod +x entrypoint.sh

# Exponer puerto
EXPOSE 8000

# Entrypoint que inicializa DB y luego inicia el servidor
ENTRYPOINT ["./entrypoint.sh"]
