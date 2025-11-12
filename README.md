# Sistema de Gestión de Proyectos y Tareas SVA

Sistema completo de gestión de proyectos y tareas con interfaz web responsive, API REST, bot de Telegram para notificaciones y recordatorios automáticos.

## 📊 Estado Actual del Proyecto

- **Versión**: 2.0.0
- **Fase Actual**: Fase 5 - Cache y Optimización (Próximamente)
- **Fases Completadas**: Fase 0 ✅ | Fase 1 ✅ | Fase 2 ✅ | Fase 3 ✅ | Fase 4 ✅
- **Progreso Global**: 71%
- **Última Actualización**: 2024-11-12 19:15

### ✅ Fases Completadas

**Fase 0: Configuración del Proyecto** (2024-11-10)
- Docker Compose con MySQL, Redis, Backend, Frontend
- Schema SQL con UUIDs implementados
- Backend FastAPI configurado con JWT
- Frontend React + TypeScript + Vite configurado

**Fase 1: Backend API Core** (2024-11-10 - 2024-11-11)
- 17 endpoints REST implementados
- Autenticación JWT con bcrypt
- CRUD completo de usuarios, proyectos y tareas
- Validación de UUIDs en todos los endpoints
- Sistema de permisos (owner vs responsible)
- Documentación Swagger/ReDoc automática

**Fase 2: Frontend Web** (2024-11-11 - Completada 100%)
- ✅ Sistema de autenticación completo (Login, Register, JWT)
- ✅ Layout principal con Sidebar y Header responsive
- ✅ **Gestión completa de proyectos (CRUD)**
  - Crear, editar, eliminar proyectos
  - Archivar/desarchivar proyectos
  - Cards con estadísticas y progreso visual
  - Selector de emojis (72 opciones)
- ✅ **Gestión completa de tareas (CRUD)**
  - TaskForm (crear/editar con validaciones)
  - Vista Lista y Vista Kanban (toggle entre vistas)
  - Filtros avanzados (proyecto, estado, prioridad, responsable)
  - Búsqueda en tiempo real (título y descripción)
  - UserAutocomplete con búsqueda de usuarios
  - Selector de prioridad y estado con colores neutros
  - DatePicker para deadlines
  - Indicadores de urgencia (Vencido, Hoy, Mañana)
  - Marcar como completada
- ✅ **Dashboard con datos reales del backend**
  - Estadísticas en tiempo real
  - Proyectos recientes (últimos 5)
  - Próximas tareas (5 con deadline más cercano)
  - Badges de estado y prioridad
- ✅ Componentes reutilizables (Modal, Button, Input, Textarea, EmojiPicker, Select, Badge, UserAutocomplete)
- ✅ Servicios de API conectados al backend
- ✅ Protección de rutas con PrivateRoute
- ✅ Diseño responsive completo (móvil, tablet, desktop)

## Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **Python 3.11+** - Lenguaje de programación
- **SQLAlchemy** - ORM para base de datos
- **Alembic** - Migraciones de base de datos
- **MySQL 8.0** - Base de datos relacional
- **Redis 7.0** - Cache y message broker
- **Celery** - Workers para tareas asíncronas
- **python-telegram-bot** - Integración con Telegram
- **JWT** - Autenticación y autorización
- **bcrypt** - Hash de contraseñas

### Frontend
- **React 18** - Librería de UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **Tailwind CSS** - Framework CSS utility-first
- **React Router** - Enrutamiento
- **Axios** - Cliente HTTP

### DevOps
- **Docker** - Contenedores
- **Docker Compose** - Orquestación de contenedores
- **Nginx** - Reverse proxy (producción)

## Características Principales

### Gestión de Proyectos
- ✅ Crear, editar y eliminar proyectos
- ✅ Organización por proyectos con iconos/emojis
- ✅ Vista colapsable de proyectos
- ✅ Asociación de múltiples tareas por proyecto

### Gestión de Tareas
- ✅ CRUD completo de tareas
- ✅ Estados: Sin empezar, En curso, Completado
- ✅ Prioridades: Baja, Media, Alta
- ✅ Asignación de responsables
- ✅ Fechas límite (deadlines)
- ✅ Recordatorios personalizables (X horas antes del deadline)
- ✅ Resúmenes de tareas
- ✅ Filtrado y búsqueda

### Bot de Telegram
- ✅ Notificaciones de tareas nuevas asignadas
- ✅ Recordatorios automáticos antes del deadline
- ✅ Comandos para gestión de tareas
- ✅ Resúmenes diarios y semanales
- ✅ Vincular cuenta de usuario con Telegram
- ✅ Marcar tareas como completadas desde Telegram

### Autenticación
- ✅ Registro de usuarios (email, contraseña, teléfono)
- ✅ Login con JWT tokens
- ✅ Asociación de teléfono para notificaciones Telegram

## Estructura del Proyecto

```
control-proyectos-sva/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── api/               # Endpoints de la API
│   │   │   └── v1/
│   │   │       ├── endpoints/ # Rutas organizadas
│   │   │       └── api.py     # Router principal
│   │   ├── core/              # Configuración core
│   │   │   ├── config.py      # Settings
│   │   │   ├── security.py    # JWT, hash
│   │   │   └── database.py    # Conexión BD
│   │   ├── models/            # Modelos SQLAlchemy
│   │   ├── schemas/           # Schemas Pydantic
│   │   ├── services/          # Lógica de negocio
│   │   ├── telegram/          # Bot de Telegram
│   │   ├── workers/           # Celery workers
│   │   ├── tests/             # Tests
│   │   └── main.py            # App principal
│   ├── alembic/               # Migraciones
│   ├── requirements.txt       # Dependencias Python
│   └── Dockerfile             # Dockerfile backend
├── frontend/                   # Frontend React
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   ├── pages/             # Páginas
│   │   ├── services/          # API client
│   │   ├── hooks/             # Custom hooks
│   │   ├── utils/             # Utilidades
│   │   ├── types/             # TypeScript types
│   │   ├── App.tsx            # Componente raíz
│   │   └── main.tsx           # Entry point
│   ├── package.json           # Dependencias Node
│   ├── vite.config.ts         # Config Vite
│   └── Dockerfile             # Dockerfile frontend
├── database/
│   └── schema.sql             # Schema inicial BD
├── docs/                       # Documentación
│   ├── architecture.md        # Arquitectura
│   ├── api.md                 # Documentación API
│   └── user-guide.md          # Guía de usuario
├── docker-compose.yml          # Docker Compose desarrollo
├── docker-compose.prod.yml     # Docker Compose producción
├── .env.example               # Variables de entorno ejemplo
├── .gitignore                 # Archivos ignorados por Git
├── README.md                  # Este archivo
└── CLAUDE.md                  # Tracking de fases
```

## Instalación y Configuración

### Prerrequisitos

- Docker 20.10+
- Docker Compose 2.0+
- Git

### Configuración Inicial

1. **Clonar el repositorio** (o crear el proyecto desde cero)

```bash
cd control-proyectos-sva
```

2. **Configurar variables de entorno**

```bash
cp .env.example .env
```

Editar `.env` con tus valores:

```env
# Database
MYSQL_ROOT_PASSWORD=tu_password_root_seguro
MYSQL_DATABASE=proyectos_sva_db
MYSQL_USER=sva_user
MYSQL_PASSWORD=tu_password_seguro

# Backend
SECRET_KEY=tu_secret_key_jwt_muy_largo_y_seguro
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram Bot
TELEGRAM_BOT_TOKEN=tu_token_de_botfather

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

3. **Generar SECRET_KEY seguro**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

4. **Crear bot de Telegram**

- Hablar con [@BotFather](https://t.me/botfather) en Telegram
- Crear nuevo bot con `/newbot`
- Copiar el token y agregarlo a `.env`

### Iniciar con Docker

```bash
# Construir e iniciar todos los servicios
docker-compose up --build

# O en modo detached (background)
docker-compose up -d --build
```

### Acceder a la aplicación

- **Frontend Web**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Documentación API (Swagger)**: http://localhost:8000/docs
- **Documentación API (ReDoc)**: http://localhost:8000/redoc

### Detener servicios

```bash
docker-compose down

# Para eliminar también los volúmenes (¡BORRA DATOS!)
docker-compose down -v
```

## Desarrollo

### Backend (FastAPI)

```bash
# Entrar al contenedor backend
docker-compose exec backend bash

# Crear nueva migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head

# Ejecutar tests
pytest

# Ver logs
docker-compose logs -f backend
```

### Frontend (React)

```bash
# Entrar al contenedor frontend
docker-compose exec frontend sh

# Instalar nueva dependencia
npm install nombre-paquete

# Ejecutar tests
npm test

# Build producción
npm run build

# Ver logs
docker-compose logs -f frontend
```

### Base de Datos

```bash
# Conectar a MySQL
docker-compose exec mysql mysql -u sva_user -p proyectos_sva_db

# Backup de base de datos
docker-compose exec mysql mysqldump -u root -p proyectos_sva_db > backup.sql

# Restaurar backup
docker-compose exec -T mysql mysql -u root -p proyectos_sva_db < backup.sql
```

### Redis

```bash
# Conectar a Redis CLI
docker-compose exec redis redis-cli

# Ver todas las keys
KEYS *

# Monitor en tiempo real
MONITOR
```

## API Endpoints Principales

### 🔑 Autenticación (`/api/v1/auth`)
- `POST /register` - Registrar nuevo usuario
- `POST /login` - Login (retorna JWT token)

### 👤 Usuarios (`/api/v1/users`)
- `GET /me` - Obtener perfil actual
- `PUT /me` - Actualizar perfil
- `POST /me/change-password` - Cambiar contraseña
- `GET /` - Listar usuarios
- `GET /{user_id}` - Obtener usuario por UUID

### 📁 Proyectos (`/api/v1/projects`)
- `GET /` - Listar proyectos del usuario
- `GET /with-stats` - Listar con estadísticas de tareas
- `POST /` - Crear proyecto
- `GET /{project_id}` - Obtener proyecto por UUID
- `PUT /{project_id}` - Actualizar proyecto
- `DELETE /{project_id}` - Eliminar proyecto
- `PATCH /{project_id}/archive` - Archivar proyecto
- `PATCH /{project_id}/unarchive` - Desarchivar proyecto

### ✅ Tareas (`/api/v1/tasks`)
- `GET /` - Listar tareas con filtros (estado, prioridad, responsable, proyecto)
- `POST /` - Crear tarea
- `GET /{task_id}` - Obtener tarea por UUID
- `PUT /{task_id}` - Actualizar tarea
- `DELETE /{task_id}` - Eliminar tarea
- `PATCH /{task_id}/status` - Cambiar estado
- `PATCH /{task_id}/complete` - Marcar como completada

**📖 Documentación interactiva completa:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 🔐 Seguridad con UUIDs

⚠️ **Importante**: Este proyecto usa **UUIDs (formato CHAR(36))** en lugar de IDs enteros para todos los recursos.

**Ejemplo de UUID**: `5f49c726-4751-44cb-ad18-8162719c340a`

**Beneficios**:
- Previene enumeración de recursos
- Mayor seguridad en APIs públicas
- IDs imposibles de predecir

**Uso en API calls**:
```bash
# ✅ Correcto - UUID válido
curl -X GET "http://localhost:8000/api/v1/projects/5f49c726-4751-44cb-ad18-8162719c340a" \
  -H "Authorization: Bearer $TOKEN"

# ❌ Incorrecto - ID entero (no soportado)
curl -X GET "http://localhost:8000/api/v1/projects/123" \
  -H "Authorization: Bearer $TOKEN"

# ❌ Incorrecto - String inválido
curl -X PUT "http://localhost:8000/api/v1/tasks/{task_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"responsible_id": "invalid"}' # Error de validación

# ✅ Correcto - Establecer responsible_id a null
curl -X PUT "http://localhost:8000/api/v1/tasks/{task_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"responsible_id": null}' # Válido
```

**Validación en el sistema**:
1. ✅ Formato UUID validado en schemas Pydantic
2. ✅ Existencia del recurso validada en endpoints
3. ✅ Foreign key constraints en base de datos

## Comandos del Bot de Telegram

- `/start` - Vincular cuenta de usuario
- `/tareas` - Listar todas tus tareas pendientes
- `/completar [id]` - Marcar tarea como completada
- `/hoy` - Ver tareas con deadline hoy
- `/pendientes` - Ver tareas sin empezar
- `/semana` - Ver tareas de esta semana
- `/help` - Ver ayuda

## Sistema de Recordatorios

Los recordatorios se configuran por tarea:

1. Al crear/editar una tarea, especifica `reminder_hours_before`
2. El sistema enviará notificación vía Telegram X horas antes del deadline
3. Configuración de resúmenes:
   - **Diario**: 8:00 AM - Tareas del día
   - **Semanal**: Lunes 9:00 AM - Tareas de la semana

## Testing

### Backend
```bash
# Ejecutar todos los tests
docker-compose exec backend pytest

# Con coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Ver reporte de coverage
open htmlcov/index.html
```

### Frontend
```bash
# Ejecutar tests
docker-compose exec frontend npm test

# Coverage
docker-compose exec frontend npm run test:coverage
```

## Deployment en Producción (OKE Oracle)

### Preparación

1. **Build imágenes de producción**

```bash
docker-compose -f docker-compose.prod.yml build
```

2. **Configurar variables de entorno de producción**

Crear `.env.prod` con valores seguros

3. **Push a Oracle Container Registry**

```bash
# Tag imágenes
docker tag control-proyectos-backend:latest <region>.ocir.io/<tenancy>/proyectos-backend:latest
docker tag control-proyectos-frontend:latest <region>.ocir.io/<tenancy>/proyectos-frontend:latest

# Push
docker push <region>.ocir.io/<tenancy>/proyectos-backend:latest
docker push <region>.ocir.io/<tenancy>/proyectos-frontend:latest
```

4. **Deploy en OKE**

Ver documentación detallada en `docs/deployment.md`

## Contribuir

### Flujo de trabajo

1. Crear branch para feature: `git checkout -b feature/nueva-funcionalidad`
2. Hacer commits descriptivos
3. Ejecutar tests: `pytest` y `npm test`
4. Push y crear Pull Request
5. Code review
6. Merge a main

### Convenciones

- **Commits**: Usar conventional commits (feat, fix, docs, etc.)
- **Código**: Seguir PEP 8 (Python) y ESLint (TypeScript)
- **Tests**: Mantener coverage > 80%

## Troubleshooting

### Problema: Puerto ya en uso

```bash
# Ver qué proceso usa el puerto 8000
sudo lsof -i :8000

# Cambiar puerto en docker-compose.yml
```

### Problema: Base de datos no conecta

```bash
# Ver logs de MySQL
docker-compose logs mysql

# Recrear volumen
docker-compose down -v
docker-compose up -d mysql
```

### Problema: Bot no recibe mensajes (Fase 3)

1. Verificar token en `.env`
2. Revisar logs: `docker-compose logs backend`
3. Verificar webhook: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`

### Problema: Error UUID inválido al actualizar tareas

**Error**: `"Value error, responsible_id debe ser un UUID válido"`

**Causa**: Se está enviando un string que no es un UUID válido.

**Solución**:
```bash
# ❌ Incorrecto
{"responsible_id": "string"}
{"responsible_id": "123"}

# ✅ Correcto
{"responsible_id": "5f49c726-4751-44cb-ad18-8162719c340a"}
{"responsible_id": null}
```

### Problema: "Usuario responsable no encontrado"

**Causa**: El UUID es válido pero no existe en la base de datos.

**Solución**:
1. Listar usuarios disponibles: `GET /api/v1/users`
2. Verificar que el UUID del usuario exista
3. Usar un UUID de usuario existente o establecer a `null`

## 🗓️ Roadmap del Proyecto

### ✅ Fase 0: Setup Inicial (Completada - 2024-11-10)
- [x] Estructura del proyecto
- [x] Docker Compose con MySQL, Redis, Backend, Frontend
- [x] Base de datos inicial con schema UUID
- [x] Configuración FastAPI
- [x] Configuración React + TypeScript + Vite

### ✅ Fase 1: Backend API Core (Completada - 2024-11-10/11)
- [x] API de autenticación JWT
- [x] CRUD completo de usuarios
- [x] CRUD completo de proyectos
- [x] CRUD completo de tareas
- [x] Migración a UUIDs
- [x] Validación de UUIDs en schemas y endpoints
- [x] Sistema de permisos (owner vs responsible)
- [x] 17 endpoints implementados
- [x] Documentación Swagger/ReDoc

### ✅ Fase 2: Frontend Web (Completada 100% - 2024-11-11)
- [x] **Sistema de autenticación** ✅
  - [x] Página de Login
  - [x] Página de Registro
  - [x] Manejo de JWT en localStorage
  - [x] Interceptor Axios para auth headers
  - [x] Protección de rutas (PrivateRoute)
  - [x] AuthContext con React Context API
- [x] **Layout Principal** ✅
  - [x] Sidebar con navegación (4 secciones)
  - [x] Header con perfil de usuario
  - [x] Menú dropdown de perfil
  - [x] Notificaciones (badge)
  - [x] Responsive design (hamburger menu móvil)
  - [x] Búsqueda global
- [x] **Servicios de API** ✅
  - [x] projectService (8 métodos)
  - [x] taskService (7 métodos)
  - [x] authService completo
- [x] **Componentes Reutilizables** ✅
  - [x] Modal (4 tamaños, ESC, overlay)
  - [x] Button (5 variantes, loading)
  - [x] Input, Textarea
  - [x] EmojiPicker (72 emojis)
  - [x] Select, Badge, UserAutocomplete
- [x] **Gestión de Proyectos** ✅ COMPLETO
  - [x] Lista con cards y estadísticas
  - [x] Crear proyecto con emoji
  - [x] Editar proyecto
  - [x] Eliminar con confirmación
  - [x] Archivar/desarchivar
  - [x] Barra de progreso visual
- [x] **Gestión de Tareas** ✅ COMPLETO
  - [x] TaskForm (crear/editar)
  - [x] Lista y Vista Kanban
  - [x] Filtros avanzados
  - [x] Búsqueda en tiempo real
  - [x] Selector de responsable (UserAutocomplete)
  - [x] DatePicker para deadline
  - [x] Indicadores de urgencia
- [x] **Dashboard con datos reales** ✅ COMPLETO

### ✅ Fase 3: Bot de Telegram (Completada - 2024-11-11/12)
- [x] Configuración del bot con BotFather
- [x] Sistema de vinculación de cuentas (código 6 caracteres, expira 15 min)
- [x] Notificaciones push (nueva tarea, cambio estado, completada)
- [x] Comandos básicos: /start, /tareas, /completar, /hoy, /pendientes, /semana, /help
- [x] Endpoints API (generate-code, status, unlink)
- [x] Servicios (LinkService, TaskService, NotificationService)
- [x] 10 archivos creados en backend/app/bot/

### ✅ Fase 4: Sistema de Recordatorios (Completada - 2024-11-12)
- [x] Configuración Celery + Redis broker
- [x] Worker de recordatorios (check_upcoming_deadlines cada hora)
- [x] Resúmenes diarios (8:00 AM) con estadísticas
- [x] Resúmenes semanales (Lunes 9:00 AM) con productividad
- [x] 4 archivos creados en backend/app/workers/
- [x] 3 tareas programadas activas (Celery Beat)
- [x] Integración completa con Telegram Bot
- [x] 2 servicios Docker (celery_worker, celery_beat)

### ⏳ Fase 5: Cache y Optimización (Pendiente)
- [ ] Implementar Redis cache en endpoints
- [ ] Rate limiting (100 req/min por IP)
- [ ] Optimización de queries con índices
- [ ] Lazy loading en frontend
- [ ] Resúmenes diarios (8:00 AM)
- [ ] Resúmenes semanales (Lunes 9:00 AM)

### ⏳ Fase 5: Cache y Optimización (Pendiente)
- [ ] Cache con Redis (proyectos, tareas)
- [ ] Rate limiting
- [ ] Optimización de queries SQL
- [ ] Lazy loading en frontend

### ⏳ Fase 6: Testing y Documentación (Pendiente)
- [ ] Tests backend (pytest) - Coverage > 80%
- [ ] Tests frontend (Vitest)
- [ ] Documentación técnica completa
- [ ] Manual de usuario

### ⏳ Fase 7: Deployment en OKE (Pendiente)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Deploy a Oracle Kubernetes Engine
- [ ] SSL/TLS con Let's Encrypt
- [ ] Monitoreo y logs centralizados
- [ ] Backups automáticos

**Progreso Global**: 57% (4 de 7 fases completadas, Fase 4 en progreso)

## Licencia

Proyecto privado - SVA

## Contacto

Para dudas o soporte, contactar al equipo de desarrollo.

---

**Última actualización**: 2024-11-12 18:30
**Versión**: 1.5.0 (Fase 3 Completada 100% - Bot de Telegram Funcional)
**Próxima milestone**: Fase 4 - Sistema de Recordatorios (Celery)

## 🎯 Próximos Pasos - Fase 4: Sistema de Recordatorios

Para iniciar la Fase 4 (sesión actual):

1. **Configuración Celery**
   - Crear celery_app.py con Redis broker
   - Configurar Celery Beat scheduler
   - Agregar servicio en docker-compose.yml

2. **Worker de Recordatorios**
   - Implementar check_upcoming_deadlines (ejecutar cada hora)
   - Buscar tareas próximas a vencer según reminder_hours_before
   - Enviar notificación vía Telegram
   - Registrar en tabla notifications
   - Evitar duplicados

3. **Resúmenes Programados**
   - send_daily_summary (8:00 AM): Tareas del día por usuario
   - send_weekly_summary (Lunes 9:00 AM): Tareas de la semana + estadísticas

4. **Estructura de Archivos**
   - backend/app/workers/__init__.py
   - backend/app/workers/celery_app.py
   - backend/app/workers/reminder_tasks.py
   - backend/app/workers/summary_tasks.py
