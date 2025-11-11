# Control de Desarrollo - Sistema de Gestión de Proyectos SVA

Este archivo registra el progreso del desarrollo del sistema por fases, decisiones técnicas y pendientes.

## Información del Proyecto

- **Nombre**: Sistema de Gestión de Proyectos y Tareas SVA
- **Fecha Inicio**: Noviembre 10, 2024
- **Duración Estimada**: 10 semanas
- **Estado Actual**: FASE 2 EN PROGRESO (65%) - Sistema de Proyectos Completado
- **Última Actualización**: 2024-11-11 20:00 UTC

---

## Stack Tecnológico Confirmado

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy
- **Migraciones**: Alembic
- **Base de Datos**: MySQL 8.0
- **Cache/Broker**: Redis 7.0
- **Workers**: Celery
- **Autenticación**: JWT + bcrypt
- **Bot**: python-telegram-bot

### Frontend
- **Framework**: React 18
- **Lenguaje**: TypeScript
- **Build Tool**: Vite
- **Estilos**: Tailwind CSS
- **HTTP Client**: Axios
- **Router**: React Router v6

### DevOps
- **Contenedores**: Docker
- **Orquestación**: Docker Compose
- **Desarrollo**: Servidor local
- **Producción**: Oracle Kubernetes Engine (OKE)

---

## Modelo de Base de Datos

### Tablas Principales

#### `users`
- `id` - **CHAR(36)** (UUID), PK ⚠️ Cambiado a UUID para seguridad
- `email` - VARCHAR(255), UNIQUE, NOT NULL
- `password_hash` - VARCHAR(255), NOT NULL
- `full_name` - VARCHAR(255), NOT NULL
- `phone_number` - VARCHAR(20), UNIQUE
- `telegram_chat_id` - BIGINT, NULLABLE
- `is_active` - BOOLEAN, DEFAULT TRUE
- `created_at` - TIMESTAMP, DEFAULT CURRENT_TIMESTAMP
- `updated_at` - TIMESTAMP, ON UPDATE CURRENT_TIMESTAMP

#### `projects`
- `id` - **CHAR(36)** (UUID), PK ⚠️ Cambiado a UUID
- `name` - VARCHAR(255), NOT NULL
- `description` - TEXT
- `emoji_icon` - VARCHAR(10)
- `owner_id` - **CHAR(36)** (UUID), FK -> users(id) ⚠️ Cambiado a UUID
- `is_archived` - BOOLEAN, DEFAULT FALSE
- `created_at` - TIMESTAMP
- `updated_at` - TIMESTAMP

#### `tasks`
- `id` - **CHAR(36)** (UUID), PK ⚠️ Cambiado a UUID
- `project_id` - **CHAR(36)** (UUID), FK -> projects(id), ON DELETE CASCADE ⚠️
- `title` - VARCHAR(500), NOT NULL
- `description` - TEXT
- `status` - ENUM('sin_empezar', 'en_curso', 'completado'), DEFAULT 'sin_empezar'
- `priority` - ENUM('baja', 'media', 'alta'), DEFAULT 'media'
- `responsible_id` - **CHAR(36)** (UUID), FK -> users(id) ⚠️ Cambiado a UUID
- `deadline` - DATETIME
- `reminder_hours_before` - INT, DEFAULT 24 (horas antes del deadline para recordatorio)
- `completed_at` - DATETIME, NULLABLE
- `created_by` - **CHAR(36)** (UUID), FK -> users(id) ⚠️ Cambiado a UUID
- `created_at` - TIMESTAMP
- `updated_at` - TIMESTAMP

#### `notifications`
- `id` - **CHAR(36)** (UUID), PK ⚠️ Cambiado a UUID
- `user_id` - **CHAR(36)** (UUID), FK -> users(id) ⚠️ Cambiado a UUID
- `task_id` - **CHAR(36)** (UUID), FK -> tasks(id), NULLABLE ⚠️ Cambiado a UUID
- `type` - ENUM('nueva_tarea', 'recordatorio', 'completada', 'resumen_diario', 'resumen_semanal', 'cambio_estado')
- `message` - TEXT
- `sent_at` - TIMESTAMP
- `read_at` - TIMESTAMP, NULLABLE
- `created_at` - TIMESTAMP

#### `telegram_link_codes`
- `id` - **CHAR(36)** (UUID), PK ⚠️ Cambiado a UUID
- `user_id` - **CHAR(36)** (UUID), FK -> users(id) ⚠️ Cambiado a UUID
- `code` - VARCHAR(10), UNIQUE, NOT NULL
- `expires_at` - TIMESTAMP
- `used_at` - TIMESTAMP, NULLABLE
- `created_at` - TIMESTAMP

#### `task_comments` (opcional - fase futura)
- `id` - **CHAR(36)** (UUID), PK ⚠️ Cambiado a UUID
- `task_id` - **CHAR(36)** (UUID), FK -> tasks(id) ⚠️ Cambiado a UUID
- `user_id` - **CHAR(36)** (UUID), FK -> users(id) ⚠️ Cambiado a UUID
- `content` - TEXT
- `created_at` - TIMESTAMP

---

## Fases del Proyecto

### ✅ FASE 0: Configuración del Proyecto (Semana 1)

**Objetivo**: Preparar entorno de desarrollo completo con Docker

**Duración**: 1 semana
**Estado**: ✅ COMPLETADA
**Progreso**: 100%
**Fecha Inicio**: 2024-11-10
**Fecha Fin**: 2024-11-10

#### Checklist

- [x] Crear estructura de directorios
- [x] Crear README.md
- [x] Crear CLAUDE.md (este archivo)
- [x] Crear schema.sql con todas las tablas (con UUIDs)
- [x] Configurar backend FastAPI
  - [x] main.py
  - [x] core/config.py
  - [x] core/database.py
  - [x] core/security.py
  - [x] requirements.txt
  - [x] Dockerfile
- [x] Configurar frontend React
  - [x] package.json
  - [x] tsconfig.json
  - [x] vite.config.ts
  - [x] tailwind.config.js
  - [x] Estructura básica de componentes
  - [x] Dockerfile
- [x] Crear docker-compose.yml
  - [x] Servicio MySQL
  - [x] Servicio Redis
  - [x] Servicio Backend
  - [x] Servicio Frontend
  - [x] Servicio Celery Worker (comentado para fase 4)
- [x] Crear .env.example
- [x] Crear .gitignore
- [x] Probar stack completo
  - [x] MySQL conecta
  - [x] Redis funciona
  - [x] Backend responde en localhost:8000
  - [x] Frontend carga en localhost:5173
  - [x] Swagger docs accesible en localhost:8000/docs

#### Notas Técnicas

- Docker desde el inicio para facilitar deployment posterior
- Usar docker-compose para desarrollo local
- Preparar docker-compose.prod.yml para OKE en fase 7
- Configurar volúmenes para persistencia de datos
- Usar redes Docker para comunicación entre servicios
- **Migración a UUIDs desde el inicio** para seguridad mejorada

#### Decisiones

- ✅ FastAPI elegido por performance y documentación automática
- ✅ React + Vite por velocidad de desarrollo y HMR
- ✅ MySQL por familiaridad del equipo y robustez
- ✅ Redis para cache y Celery broker
- ✅ TypeScript para type safety en frontend
- ✅ **UUIDs en lugar de IDs enteros** para prevenir enumeración de recursos

#### Problemas Encontrados

- ✅ **Resuelto**: Enum mismatch entre Python y MySQL (solucionado con `values_callable`)

---

### ✅ FASE 1: Backend API Core (Semana 2-3)

**Objetivo**: Desarrollar API REST con autenticación y CRUD completo

**Duración**: 1 día (acelerado)
**Estado**: ✅ COMPLETADA
**Progreso**: 100%
**Fecha Inicio**: 2024-11-10
**Fecha Fin**: 2024-11-11

#### Checklist

- [x] **Módulo de Autenticación**
  - [x] Registro de usuarios (POST /api/v1/auth/register)
    - [x] Validación de email
    - [x] Validación de teléfono
    - [x] Hash de contraseña con bcrypt
    - [x] Validación de contraseña fuerte (8+ chars, mayúscula, número)
  - [x] Login (POST /api/v1/auth/login)
    - [x] Validar credenciales
    - [x] Generar JWT token
    - [x] Retornar datos del usuario
  - [x] Middleware de autenticación (get_current_user)
  - [x] Dependency @Depends(get_current_user) para rutas protegidas

- [x] **Módulo de Usuarios**
  - [x] Obtener perfil (GET /api/v1/users/me)
  - [x] Actualizar perfil (PUT /api/v1/users/me)
  - [x] Cambiar contraseña (POST /api/v1/users/me/change-password)
  - [x] Listar usuarios (GET /api/v1/users)
  - [x] Obtener usuario por ID (GET /api/v1/users/{user_id})

- [x] **Módulo de Proyectos**
  - [x] Listar proyectos (GET /api/v1/projects)
  - [x] Listar proyectos con estadísticas (GET /api/v1/projects/with-stats)
  - [x] Crear proyecto (POST /api/v1/projects)
  - [x] Obtener proyecto (GET /api/v1/projects/{id})
  - [x] Actualizar proyecto (PUT /api/v1/projects/{id})
  - [x] Eliminar proyecto (DELETE /api/v1/projects/{id})
  - [x] Archivar proyecto (PATCH /api/v1/projects/{id}/archive)
  - [x] Desarchivar proyecto (PATCH /api/v1/projects/{id}/unarchive)
  - [x] Validación de propiedad (solo owner puede modificar)

- [x] **Módulo de Tareas**
  - [x] Listar tareas (GET /api/v1/tasks)
    - [x] Filtro por proyecto
    - [x] Filtro por estado
    - [x] Filtro por responsable
    - [x] Filtro por prioridad
    - [x] Paginación (skip/limit)
  - [x] Crear tarea (POST /api/v1/tasks)
    - [x] Validación de proyecto existe y pertenece al usuario
    - [x] Validación de responsable existe
    - [x] Asignación automática de created_by
  - [x] Obtener tarea (GET /api/v1/tasks/{id})
  - [x] Actualizar tarea (PUT /api/v1/tasks/{id})
    - [x] Validación de UUID format en responsible_id
    - [x] Validación de usuario existe
    - [x] Soporte para establecer responsible_id como null
  - [x] Eliminar tarea (DELETE /api/v1/tasks/{id})
  - [x] Cambiar estado (PATCH /api/v1/tasks/{id}/status)
  - [x] Marcar completada (PATCH /api/v1/tasks/{id}/complete)
  - [x] Validación de permisos (owner o responsible)

- [x] **Migración a UUIDs**
  - [x] Actualización de schema.sql a CHAR(36)
  - [x] Migración de todos los modelos SQLAlchemy
  - [x] Actualización de todos los schemas Pydantic
  - [x] Actualización de endpoints para aceptar UUIDs
  - [x] Validación de formato UUID en schemas
  - [x] Testing completo de operaciones con UUIDs

- [x] **Documentación API**
  - [x] Swagger UI configurado en /docs
  - [x] ReDoc configurado en /redoc
  - [x] Schemas Pydantic documentados
  - [x] Todos los endpoints documentados con descripciones

#### Entregables
- ✅ API REST completamente funcional con UUIDs
- ✅ Documentación Swagger/ReDoc completa
- ✅ Validaciones robustas en todos los endpoints
- ✅ Testing manual exitoso de todos los endpoints

#### Endpoints Implementados

**Autenticación** (`/api/v1/auth`)
- `POST /register` - Registrar nuevo usuario
- `POST /login` - Login y obtener JWT token

**Usuarios** (`/api/v1/users`)
- `GET /me` - Obtener perfil actual
- `PUT /me` - Actualizar perfil
- `POST /me/change-password` - Cambiar contraseña
- `GET /` - Listar usuarios
- `GET /{user_id}` - Obtener usuario por UUID

**Proyectos** (`/api/v1/projects`)
- `GET /` - Listar proyectos del usuario
- `GET /with-stats` - Listar con estadísticas de tareas
- `POST /` - Crear proyecto
- `GET /{project_id}` - Obtener proyecto por UUID
- `PUT /{project_id}` - Actualizar proyecto
- `DELETE /{project_id}` - Eliminar proyecto
- `PATCH /{project_id}/archive` - Archivar
- `PATCH /{project_id}/unarchive` - Desarchivar

**Tareas** (`/api/v1/tasks`)
- `GET /` - Listar tareas con filtros
- `POST /` - Crear tarea
- `GET /{task_id}` - Obtener tarea por UUID
- `PUT /{task_id}` - Actualizar tarea
- `DELETE /{task_id}` - Eliminar tarea
- `PATCH /{task_id}/status` - Cambiar estado
- `PATCH /{task_id}/complete` - Marcar completada

---

### 🔄 FASE 2: Frontend Web (Semana 4-5)

**Objetivo**: Interfaz web responsive basada en diseño propuesto

**Duración**: 2 semanas
**Estado**: 🟡 EN PROGRESO
**Progreso**: 65%
**Fecha Inicio**: 2024-11-11
**Fecha Estimada Fin**: 2024-11-25

#### Checklist

- [x] **Sistema de Autenticación** ✅ COMPLETADO
  - [x] Página de Login
  - [x] Página de Registro
  - [x] Manejo de JWT en localStorage
  - [x] Interceptor Axios para auth headers
  - [x] Protección de rutas (PrivateRoute)
  - [x] Auto-logout en token expirado
  - [x] AuthContext con React Context API
  - [x] authService con CRUD completo

- [x] **Layout Principal** ✅ COMPLETADO
  - [x] Sidebar con navegación (4 secciones)
  - [x] Header con perfil de usuario
  - [x] Menú dropdown de perfil
  - [x] Notificaciones (badge)
  - [x] Barra de búsqueda
  - [x] Responsive (hamburger menu móvil)
  - [x] Overlay para cerrar sidebar en móvil
  - [x] Footer con copyright

- [x] **Servicios de API** ✅ COMPLETADO
  - [x] projectService.ts (8 métodos)
  - [x] taskService.ts (7 métodos)
  - [x] apiClient con interceptores
  - [x] Manejo automático de JWT
  - [x] Auto-logout en 401

- [x] **Componentes Reutilizables** ✅ COMPLETADO
  - [x] Modal (con overlay, ESC, tamaños)
  - [x] Button (5 variantes, 3 tamaños, loading)
  - [x] Input (label, error, helper text)
  - [x] Textarea (todas las features de Input)
  - [x] EmojiPicker (72 emojis, grid 6x6)
  - [ ] Select
  - [ ] Badge
  - [ ] Avatar
  - [ ] DatePicker

- [x] **Gestión de Proyectos** ✅ COMPLETADO
  - [x] Lista de proyectos con emojis y estadísticas
  - [x] ProjectCard con progreso visual
  - [x] Formulario crear proyecto
  - [x] Formulario editar proyecto
  - [x] Selector de emoji/icono
  - [x] Eliminar proyecto (con confirmación)
  - [x] Archivar/desarchivar proyectos
  - [x] Modal de confirmación para eliminar
  - [x] Integración completa con backend
  - [x] Manejo de errores
  - [x] Empty states

- [x] **Páginas Base** ✅ COMPLETADO
  - [x] Dashboard con estadísticas
  - [x] Projects (CRUD completo)
  - [x] Tasks (placeholder)
  - [x] Profile (vista de información)
  - [x] Login
  - [x] Register

- [ ] **Gestión de Tareas** ⏳ PENDIENTE
  - [ ] TaskForm (crear/editar)
  - [ ] TaskCard o TaskRow
  - [ ] Lista/Tabla de tareas
  - [ ] Filtros (estado, prioridad, responsable, proyecto)
  - [ ] Búsqueda por texto
  - [ ] Vista Kanban por estados
  - [ ] Vista por proyecto
  - [ ] Selector de responsable (usuarios)
  - [ ] Selector de prioridad
  - [ ] Selector de estado
  - [ ] DatePicker para deadline
  - [ ] Botón marcar completada
  - [ ] Modal confirmación eliminar

- [ ] **Dashboard Mejorado** ⏳ PENDIENTE
  - [ ] Conectar con datos reales del backend
  - [ ] Proyectos recientes (con datos)
  - [ ] Tareas recientes (con datos)
  - [ ] Gráficos de progreso (opcional)

- [ ] **Perfil de Usuario** ⏳ PENDIENTE (Parcial)
  - [x] Ver datos de perfil
  - [ ] Editar perfil (formulario funcional)
  - [ ] Cambiar contraseña (formulario funcional)
  - [ ] Vincular Telegram (mostrar código/QR)

- [x] **Diseño Responsive** ✅ COMPLETADO
  - [x] Mobile (< 640px)
  - [x] Tablet (640px - 1024px)
  - [x] Desktop (> 1024px)
  - [x] Touch-friendly buttons
  - [x] Grid responsivo (1/2/3 columnas)
  - [x] Sidebar colapsable en móvil
  - [x] Búsqueda adaptativa

#### Archivos Creados en Fase 2

**Servicios (`frontend/src/services/`):**
- ✅ `api.ts` - Cliente Axios con interceptores
- ✅ `authService.ts` - Autenticación y perfil
- ✅ `projectService.ts` - CRUD de proyectos
- ✅ `taskService.ts` - CRUD de tareas

**Types (`frontend/src/types/`):**
- ✅ `api.ts` - Interfaces TypeScript completas

**Contextos (`frontend/src/contexts/`):**
- ✅ `AuthContext.tsx` - Context API para auth

**Componentes Comunes (`frontend/src/components/common/`):**
- ✅ `Modal.tsx`
- ✅ `Button.tsx`
- ✅ `Input.tsx`
- ✅ `Textarea.tsx`
- ✅ `EmojiPicker.tsx`

**Componentes de Layout (`frontend/src/components/Layout/`):**
- ✅ `Sidebar.tsx`
- ✅ `Header.tsx`
- ✅ `MainLayout.tsx`

**Componentes de Auth (`frontend/src/components/Auth/`):**
- ✅ `PrivateRoute.tsx`

**Componentes de Proyectos (`frontend/src/components/Projects/`):**
- ✅ `ProjectForm.tsx`
- ✅ `ProjectCard.tsx`

**Páginas (`frontend/src/pages/`):**
- ✅ `Login.tsx`
- ✅ `Register.tsx`
- ✅ `Dashboard.tsx`
- ✅ `Projects.tsx` (CRUD completo)
- ✅ `Tasks.tsx` (placeholder)
- ✅ `Profile.tsx` (vista)

#### Entregables Completados
- ✅ Sistema de autenticación funcional
- ✅ Layout responsive con sidebar y header
- ✅ Gestión completa de proyectos (CRUD)
- ✅ Componentes reutilizables base
- ✅ Integración con backend API
- ⏳ Gestión de tareas (pendiente)
- ⏳ Dashboard con datos reales (pendiente)

---

### ⏳ FASE 3: Bot de Telegram (Semana 6)

**Objetivo**: Bot funcional para notificaciones y comandos

**Duración**: 1 semana
**Estado**: ⚪ PENDIENTE
**Progreso**: 0%

#### Checklist

- [ ] **Configuración**
  - [ ] Crear bot con BotFather
  - [ ] Configurar webhook o polling
  - [ ] Variables de entorno (TELEGRAM_BOT_TOKEN)

- [ ] **Sistema de Vinculación**
  - [ ] Generar código de vinculación en backend
  - [ ] Endpoint /api/v1/telegram/link-code
  - [ ] Comando /start en bot
  - [ ] Verificar código y asociar chat_id
  - [ ] Actualizar user.telegram_chat_id en BD

- [ ] **Notificaciones Push**
  - [ ] Notificar nueva tarea asignada
  - [ ] Notificar cambio de estado
  - [ ] Notificar tarea completada
  - [ ] Formato de mensajes con markdown

- [ ] **Comandos del Bot**
  - [ ] `/start` - Vincular cuenta
  - [ ] `/tareas` - Listar tareas pendientes
  - [ ] `/completar [id]` - Marcar completada
  - [ ] `/hoy` - Tareas con deadline hoy
  - [ ] `/pendientes` - Tareas sin empezar
  - [ ] `/semana` - Tareas de esta semana
  - [ ] `/ayuda` o `/help` - Mostrar comandos

- [ ] **Handlers**
  - [ ] Command handlers
  - [ ] Error handlers
  - [ ] Callback query handlers (botones inline)

- [ ] **Seguridad**
  - [ ] Validar que usuario está vinculado
  - [ ] Rate limiting por usuario
  - [ ] Logging de comandos

#### Entregables
- Bot operativo en Telegram
- Sistema de vinculación funcionando
- Comandos básicos implementados

---

### ⏳ FASE 4: Sistema de Recordatorios (Semana 7)

**Objetivo**: Recordatorios automáticos y resúmenes programados

**Duración**: 1 semana
**Estado**: ⚪ PENDIENTE
**Progreso**: 0%

#### Checklist

- [ ] **Configuración Celery**
  - [ ] Celery app con Redis broker
  - [ ] Celery Beat scheduler
  - [ ] Worker en Docker Compose

- [ ] **Worker de Recordatorios**
  - [ ] Task `check_upcoming_deadlines`
    - [ ] Ejecutar cada hora
    - [ ] Buscar tareas con deadline próximo
    - [ ] Calcular si falta X horas (task.reminder_hours_before)
    - [ ] Enviar notificación vía Telegram
    - [ ] Registrar en tabla notifications
    - [ ] No enviar duplicados
  - [ ] Manejo de zonas horarias

- [ ] **Resúmenes Programados**
  - [ ] Task `send_daily_summary`
    - [ ] Ejecutar diario 8:00 AM
    - [ ] Agrupar tareas por usuario
    - [ ] Formato: "Tienes 5 tareas para hoy"
    - [ ] Lista de tareas con deadlines
    - [ ] Enviar vía Telegram
  - [ ] Task `send_weekly_summary`
    - [ ] Ejecutar lunes 9:00 AM
    - [ ] Tareas de la semana
    - [ ] Estadísticas (completadas vs pendientes)

- [ ] **Configuración de Preferencias**
  - [ ] Tabla user_preferences (opcional)
  - [ ] Horario de resúmenes configurable
  - [ ] Activar/desactivar notificaciones

- [ ] **Logs y Monitoreo**
  - [ ] Logs de tareas ejecutadas
  - [ ] Logs de notificaciones enviadas
  - [ ] Flower para monitoreo Celery (opcional)

#### Entregables
- Recordatorios automáticos funcionando
- Resúmenes diarios y semanales
- Celery workers operativos

---

### ⏳ FASE 5: Cache y Optimización (Semana 8)

**Objetivo**: Implementar Redis cache y optimizaciones de performance

**Duración**: 1 semana
**Estado**: ⚪ PENDIENTE
**Progreso**: 0%

#### Checklist

- [ ] **Implementación de Cache**
  - [ ] Decorador @cached para endpoints
  - [ ] Cache de listado de proyectos (TTL 5 min)
  - [ ] Cache de listado de tareas (TTL 2 min)
  - [ ] Cache de usuario logueado (TTL 15 min)
  - [ ] Invalidación en create/update/delete

- [ ] **Rate Limiting**
  - [ ] Middleware de rate limiting
  - [ ] Límite por IP (100 req/min)
  - [ ] Límite por usuario autenticado (200 req/min)
  - [ ] Rate limit en bot Telegram (10 cmd/min)

- [ ] **Optimización de Queries**
  - [ ] Índices en BD
    - [ ] users(email)
    - [ ] users(phone_number)
    - [ ] tasks(project_id)
    - [ ] tasks(responsible_id)
    - [ ] tasks(deadline)
    - [ ] tasks(status)
  - [ ] Eager loading con joinedload()
  - [ ] Select only needed columns
  - [ ] Paginación eficiente

- [ ] **Optimización Frontend**
  - [ ] Lazy loading de componentes
  - [ ] Memoización con useMemo/useCallback
  - [ ] Debounce en búsquedas
  - [ ] Infinite scroll en listas largas (opcional)

- [ ] **Compresión**
  - [ ] Gzip en responses del backend
  - [ ] Minificación de JS/CSS en build

#### Entregables
- Cache implementado
- Performance mejorado significativamente
- Rate limiting activo

---

### ⏳ FASE 6: Testing y Documentación (Semana 9)

**Objetivo**: Suite de tests completa y documentación final

**Duración**: 1 semana
**Estado**: ⚪ PENDIENTE
**Progreso**: 0%

#### Checklist

- [ ] **Tests Backend**
  - [ ] Tests unitarios (pytest)
    - [ ] test_auth.py
    - [ ] test_users.py
    - [ ] test_projects.py
    - [ ] test_tasks.py
    - [ ] test_telegram.py
  - [ ] Tests de integración
  - [ ] Coverage > 80%
  - [ ] Fixtures reutilizables
  - [ ] Test database separada

- [ ] **Tests Frontend**
  - [ ] Tests de componentes (Vitest)
  - [ ] Tests de hooks
  - [ ] Tests de utilidades
  - [ ] Mocking de API calls

- [ ] **Documentación Técnica**
  - [ ] docs/architecture.md - Diagramas de arquitectura
  - [ ] docs/api.md - Documentación completa de API
  - [ ] docs/database.md - Esquema de BD
  - [ ] docs/deployment.md - Guía de deployment
  - [ ] Comentarios en código (docstrings)

- [ ] **Manual de Usuario**
  - [ ] docs/user-guide.md
    - [ ] Cómo registrarse
    - [ ] Cómo crear proyectos
    - [ ] Cómo gestionar tareas
    - [ ] Cómo vincular Telegram
    - [ ] Cómo usar el bot
  - [ ] Screenshots de la interfaz

- [ ] **README actualizado**
  - [ ] Instrucciones de instalación
  - [ ] Variables de entorno
  - [ ] Comandos Docker
  - [ ] Troubleshooting

#### Entregables
- Coverage de tests > 80%
- Documentación técnica completa
- Manual de usuario con screenshots

---

### ⏳ FASE 7: Deployment y CI/CD (Semana 10)

**Objetivo**: Deploy en producción en OKE Oracle

**Duración**: 1 semana
**Estado**: ⚪ PENDIENTE
**Progreso**: 0%

#### Checklist

- [ ] **Preparación para Producción**
  - [ ] docker-compose.prod.yml
  - [ ] Nginx como reverse proxy
  - [ ] SSL/TLS con Let's Encrypt
  - [ ] Variables de entorno de producción
  - [ ] Secrets management

- [ ] **Oracle Container Registry**
  - [ ] Crear repositorios en OCIR
  - [ ] Build imágenes optimizadas
  - [ ] Tag y push a OCIR
    - [ ] Backend image
    - [ ] Frontend image

- [ ] **Kubernetes en OKE**
  - [ ] Crear namespace
  - [ ] Deployments
    - [ ] backend-deployment.yaml
    - [ ] frontend-deployment.yaml
    - [ ] mysql-statefulset.yaml
    - [ ] redis-deployment.yaml
    - [ ] celery-worker-deployment.yaml
  - [ ] Services
  - [ ] Ingress
  - [ ] ConfigMaps
  - [ ] Secrets
  - [ ] Persistent Volumes (MySQL data)

- [ ] **CI/CD Pipeline** (opcional)
  - [ ] GitHub Actions workflow
  - [ ] Auto-testing en push
  - [ ] Auto-build en merge a main
  - [ ] Auto-deploy a staging

- [ ] **Monitoreo y Logs**
  - [ ] Centralized logging
  - [ ] Health checks endpoints
  - [ ] Prometheus metrics (opcional)
  - [ ] Grafana dashboards (opcional)
  - [ ] Alerting (email/Telegram)

- [ ] **Backup y Disaster Recovery**
  - [ ] Backup automático de MySQL
  - [ ] Script de restore
  - [ ] Backup de volúmenes

- [ ] **Seguridad**
  - [ ] Security headers
  - [ ] CORS configurado
  - [ ] Rate limiting en nginx
  - [ ] WAF básico (opcional)
  - [ ] Análisis de vulnerabilidades

#### Entregables
- Aplicación desplegada en OKE
- CI/CD pipeline activo
- Monitoreo configurado
- Backups automáticos

---

## Métricas de Progreso Global

| Fase | Duración | Estado | Progreso | Fecha Inicio | Fecha Fin |
|------|----------|--------|----------|--------------|-----------|
| Fase 0 | 1 día | ✅ Completada | 100% | 2024-11-10 | 2024-11-10 |
| Fase 1 | 1 día | ✅ Completada | 100% | 2024-11-10 | 2024-11-11 |
| Fase 2 | 2 sem | 🟡 En progreso | 65% | 2024-11-11 | ~2024-11-25 |
| Fase 3 | 1 sem | ⚪ Pendiente | 0% | - | - |
| Fase 4 | 1 sem | ⚪ Pendiente | 0% | - |  - |
| Fase 5 | 1 sem | ⚪ Pendiente | 0% | - | - |
| Fase 6 | 1 sem | ⚪ Pendiente | 0% | - | - |
| Fase 7 | 1 sem | ⚪ Pendiente | 0% | - | - |
| **TOTAL** | **~8 sem** | **🟡** | **33%** | **2024-11-10** | **~2025-01-05** |

---

## Decisiones Técnicas Importantes

### 2024-11-10: Elección de Stack
- **Decisión**: FastAPI + React + MySQL + Redis
- **Razón**: Balance entre performance, productividad y escalabilidad
- **Alternativas consideradas**: Django, Flask, Vue.js, PostgreSQL
- **Impacto**: Toda la arquitectura del proyecto

### 2024-11-10: Docker desde el inicio
- **Decisión**: Usar Docker y Docker Compose desde fase 0
- **Razón**: Facilita deployment posterior a OKE, consistencia de entornos
- **Impacto**: Configuración inicial más compleja pero deployment simplificado

### 2024-11-10: Recordatorios personalizables
- **Decisión**: Campo `reminder_hours_before` en cada tarea (no fijo 24/48h)
- **Razón**: Flexibilidad solicitada por el cliente
- **Impacto**: Lógica más compleja en worker de recordatorios

### 2024-11-10: Migración a UUIDs
- **Decisión**: Usar CHAR(36) UUID en lugar de INT AUTO_INCREMENT para todos los IDs
- **Razón**: Seguridad - prevenir enumeración de recursos, mejor para APIs públicas
- **Alternativas consideradas**: INT AUTO_INCREMENT (descartado por seguridad), BINARY(16) (descartado por legibilidad)
- **Impacto**: Mayor seguridad, IDs más largos (36 chars), generación server-side con `uuid.uuid4()`
- **Implementación**:
  - Database: CHAR(36) en todas las PKs y FKs
  - SQLAlchemy: `default=lambda: str(uuid.uuid4())`
  - Pydantic: str type con @field_validator para validación de formato
  - API: Validación de formato UUID + existencia en BD

---

## Problemas y Soluciones

### Problema: IntegrityError con responsible_id='string'
- **Fecha**: 2024-11-11
- **Descripción**: Al actualizar tareas vía PUT /api/v1/tasks/{id}, si se enviaba un string inválido como 'string' en responsible_id, se producía IntegrityError violando la foreign key constraint porque no había validación de formato UUID ni existencia del usuario.
- **Error Completo**: `pymysql.err.IntegrityError: (1452, 'Cannot add or update a child row: a foreign key constraint fails (proyectos_sva_db.tasks, CONSTRAINT fk_tasks_responsible FOREIGN KEY (responsible_id) REFERENCES users (id))')`
- **Solución**:
  1. Agregado `@field_validator` en TaskCreate y TaskUpdate (schemas/task.py) para validar formato UUID
  2. Agregada validación en endpoint update_task (endpoints/tasks.py) que verifica que el usuario existe en BD
  3. Cambiado a usar `model_dump(exclude_unset=True)` para distinguir entre null enviado vs campo omitido
- **Testing realizado**:
  - UUID inválido → Rechazado con error de validación
  - UUID válido inexistente → Rechazado con "Usuario responsable no encontrado"
  - UUID válido existente → Actualizado correctamente
  - Valor null → Actualizado a null correctamente
- **Lecciones aprendidas**: Validación en múltiples capas (Pydantic + endpoint + BD) es esencial. La distinción entre "campo no enviado" vs "campo con null" requiere `exclude_unset=True`.

### Problema: Enum mismatch Python vs MySQL
- **Fecha**: 2024-11-10
- **Descripción**: Los enums en Python usaban formato SNAKE_UPPER (SIN_EMPEZAR) pero MySQL esperaba snake_lower (sin_empezar), causando errores de inserción.
- **Solución**: Usar `values_callable=lambda obj: [e.value for e in obj]` en la definición de columnas Enum de SQLAlchemy, donde e.value='sin_empezar' (lowercase).
- **Lecciones aprendidas**: Siempre sincronizar formatos de enums entre ORM y schema SQL.

---

## Pendientes y Notas

### Pendientes Generales
- [ ] Decidir librería de componentes UI (opcional: shadcn/ui, Headless UI, MUI)
- [ ] Definir naming convention para commits (Conventional Commits)
- [ ] Configurar pre-commit hooks (black, flake8, eslint)
- [ ] Definir política de branches (gitflow, trunk-based)

### Notas Importantes
- Usar UTC en base de datos para timestamps
- Considerar i18n (internacionalización) en fase futura
- Evaluar agregar WebSockets para notificaciones en tiempo real (fase futura)
- Posible feature: Comentarios en tareas (fase futura)
- Posible feature: Archivos adjuntos en tareas (fase futura)
- Posible feature: Etiquetas/tags en tareas (fase futura)

### Preguntas sin Resolver
- ¿Roles de usuario? (admin, manager, user) - Definir en Fase 1
- ¿Múltiples responsables por tarea? - Por ahora NO, uno solo
- ¿Subtareas? - Fase futura
- ¿Estimaciones de tiempo? - Fase futura

---

## Changelog

### [0.3.0] - 2024-11-11 20:00
#### Agregado - Fase 2 (Progreso 65%)
- ✅ Sistema de autenticación frontend completo (Login, Register, AuthContext)
- ✅ Layout principal con Sidebar y Header responsive
- ✅ Gestión completa de proyectos (CRUD)
  - ProjectCard con estadísticas y barra de progreso
  - ProjectForm para crear/editar
  - Modal de confirmación para eliminar
  - Funcionalidad de archivar/desarchivar
  - EmojiPicker con 72 emojis
- ✅ Componentes reutilizables (Modal, Button, Input, Textarea, EmojiPicker)
- ✅ Servicios de API (projectService, taskService, authService)
- ✅ Páginas: Dashboard, Projects, Tasks (placeholder), Profile
- ✅ Protección de rutas con PrivateRoute
- ✅ Interceptor Axios para JWT automático
- ✅ Diseño responsive completo (móvil, tablet, desktop)

#### Por Hacer - Continuar Mañana
- ⏳ Gestión de tareas (TaskForm, TaskCard, filtros, vista Kanban)
- ⏳ Dashboard con datos reales del backend
- ⏳ Perfil de usuario (editar, cambiar contraseña)
- ⏳ Componentes pendientes (Select, Badge, Avatar, DatePicker)

### [0.2.0] - 2024-11-11
#### Agregado
- ✅ Fase 1 completada: API REST completa con autenticación JWT
- 17 endpoints implementados (auth, users, projects, tasks)
- Validación de formato UUID en todos los schemas
- Validación de existencia de UUIDs en endpoints
- Soporte para establecer responsible_id como null
- Sistema de permisos (owner vs responsible)

#### Cambiado
- Migración completa a UUIDs (CHAR(36)) en lugar de IDs enteros
- Actualizado model_dump(exclude_unset=True) para manejo correcto de null

#### Corregido
- IntegrityError al enviar responsible_id inválido
- Validación de UUID en TaskCreate y TaskUpdate
- Manejo de null en campos opcionales

### [0.1.0] - 2024-11-10
#### Agregado
- ✅ Fase 0 completada: Configuración del proyecto
- Estructura inicial del proyecto
- README.md completo
- CLAUDE.md para tracking
- Docker Compose con MySQL, Redis, Backend, Frontend
- Schema SQL con todas las tablas (con UUIDs)
- Backend FastAPI configurado
- Frontend React + TypeScript + Vite configurado
- Swagger docs en /docs y ReDoc en /redoc

#### Corregido
- Enum mismatch entre Python (SNAKE_UPPER) y MySQL (snake_lower)

---

## Referencias Útiles

### Documentación
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [python-telegram-bot](https://docs.python-telegram-bot.org/)
- [Docker Docs](https://docs.docker.com/)
- [Celery Docs](https://docs.celeryq.dev/)

### Recursos
- Diseño de referencia: `PantallaPropuesta.png`

---

**Última actualización**: 2024-11-11 22:30 UTC
**Próxima revisión**: Fin de Fase 2 (2 semanas)
