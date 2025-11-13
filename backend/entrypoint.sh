#!/bin/bash
# ============================================================================
# Entrypoint script para el contenedor del backend
# ============================================================================

set -e  # Exit on error

echo "=========================================="
echo "🚀 Starting Backend Container"
echo "=========================================="

# 1. Inicializar base de datos (migraciones)
echo "📦 Initializing database..."
python init_db.py

# 2. Iniciar servidor Uvicorn
echo "🌐 Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
