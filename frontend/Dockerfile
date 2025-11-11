# ============================================================================
# Dockerfile - Frontend React + Vite
# ============================================================================

FROM node:20-alpine

# Directorio de trabajo
WORKDIR /app

# Copiar package files
COPY package.json package-lock.json* ./

# Instalar dependencias
RUN npm install

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 5173

# Comando por defecto (modo desarrollo)
CMD ["npm", "run", "dev"]
