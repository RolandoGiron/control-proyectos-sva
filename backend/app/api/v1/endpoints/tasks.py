"""
Endpoints de Tareas
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models import User, Project, Task
from app.models.task import TaskStatus, TaskPriority
from app.schemas import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse, TaskWithDetails

router = APIRouter()


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    project_id: Optional[str] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    responsible_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar tareas con filtros

    Args:
        project_id: Filtrar por proyecto
        status: Filtrar por estado
        priority: Filtrar por prioridad
        responsible_id: Filtrar por responsable
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Lista de tareas
    """
    # Query base: tareas de proyectos del usuario O tareas asignadas al usuario
    query = db.query(Task).join(Project).filter(
        or_(
            Project.owner_id == current_user.id,
            Task.responsible_id == current_user.id
        )
    )

    # Aplicar filtros
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if responsible_id:
        query = query.filter(Task.responsible_id == responsible_id)

    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    return tasks


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Crear nueva tarea

    Args:
        task_data: Datos de la tarea a crear
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Tarea creada

    Raises:
        HTTPException: Si el proyecto no existe o no pertenece al usuario
    """
    # Verificar que el proyecto existe y pertenece al usuario
    project = db.query(Project).filter(
        Project.id == task_data.project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    # Verificar que el responsable existe (si se especificó)
    if task_data.responsible_id:
        responsible = db.query(User).filter(User.id == task_data.responsible_id).first()
        if not responsible:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario responsable no encontrado"
            )

    # Crear tarea
    db_task = Task(
        project_id=task_data.project_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        responsible_id=task_data.responsible_id,
        deadline=task_data.deadline,
        reminder_hours_before=task_data.reminder_hours_before,
        created_by=current_user.id,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # TODO: Enviar notificación Telegram al responsable (Fase 3)

    return db_task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtener tarea por ID

    Args:
        task_id: ID de la tarea
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Tarea encontrada

    Raises:
        HTTPException: Si la tarea no existe o el usuario no tiene acceso
    """
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        or_(
            Project.owner_id == current_user.id,
            Task.responsible_id == current_user.id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Actualizar tarea

    Args:
        task_id: ID de la tarea
        task_update: Datos a actualizar
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Tarea actualizada

    Raises:
        HTTPException: Si la tarea no existe o el usuario no es el dueño del proyecto
    """
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id  # Solo el dueño del proyecto puede editar
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )

    # Actualizar campos - usar exclude_unset para distinguir entre None enviado vs campo no enviado
    update_data = task_update.model_dump(exclude_unset=True)

    if 'title' in update_data:
        task.title = update_data['title']
    if 'description' in update_data:
        task.description = update_data['description']
    if 'status' in update_data:
        old_status = task.status
        task.status = update_data['status']
        # Si se marca como completada, registrar fecha
        if update_data['status'] == TaskStatus.COMPLETADO and old_status != TaskStatus.COMPLETADO:
            task.completed_at = datetime.utcnow()
        elif update_data['status'] != TaskStatus.COMPLETADO:
            task.completed_at = None
    if 'priority' in update_data:
        task.priority = update_data['priority']
    if 'responsible_id' in update_data:
        # Validar que el usuario exista si se proporciona un ID (no null)
        if update_data['responsible_id']:
            responsible = db.query(User).filter(User.id == update_data['responsible_id']).first()
            if not responsible:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usuario responsable no encontrado"
                )
        task.responsible_id = update_data['responsible_id']
    if 'deadline' in update_data:
        task.deadline = update_data['deadline']
    if 'reminder_hours_before' in update_data:
        task.reminder_hours_before = update_data['reminder_hours_before']

    db.commit()
    db.refresh(task)

    return task


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: str,
    status_update: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Actualizar solo el estado de la tarea (responsable o dueño)

    Args:
        task_id: ID de la tarea
        status_update: Nuevo estado
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Tarea actualizada

    Raises:
        HTTPException: Si la tarea no existe o el usuario no tiene permiso
    """
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        or_(
            Project.owner_id == current_user.id,
            Task.responsible_id == current_user.id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )

    old_status = task.status
    task.status = status_update.status

    # Actualizar completed_at
    if status_update.status == TaskStatus.COMPLETADO and old_status != TaskStatus.COMPLETADO:
        task.completed_at = datetime.utcnow()
    elif status_update.status != TaskStatus.COMPLETADO:
        task.completed_at = None

    db.commit()
    db.refresh(task)

    # TODO: Enviar notificación Telegram si fue completada (Fase 3)

    return task


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Marcar tarea como completada (atajo)

    Args:
        task_id: ID de la tarea
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Tarea completada

    Raises:
        HTTPException: Si la tarea no existe o el usuario no tiene permiso
    """
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        or_(
            Project.owner_id == current_user.id,
            Task.responsible_id == current_user.id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )

    task.status = TaskStatus.COMPLETADO
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Eliminar tarea (solo dueño del proyecto)

    Args:
        task_id: ID de la tarea
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Raises:
        HTTPException: Si la tarea no existe o el usuario no es el dueño
    """
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )

    db.delete(task)
    db.commit()

    return None
