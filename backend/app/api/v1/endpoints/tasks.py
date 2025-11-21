"""
Endpoints de Tareas
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models import User, Project, Task
from app.models.task import TaskStatus, TaskPriority
from app.schemas import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse, TaskWithDetails
from app.bot.notifications import send_task_assignment_notification, send_task_reassignment_notification

router = APIRouter()


@router.get("/", response_model=list[TaskWithDetails])
def list_tasks(
    project_id: Optional[str] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    responsible_id: Optional[str] = Query(None),
    include_archived: bool = Query(False, description="Incluir tareas archivadas en el listado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar tareas con filtros e información detallada (proyecto, responsable, creador)

    Args:
        project_id: Filtrar por proyecto
        status: Filtrar por estado
        priority: Filtrar por prioridad
        responsible_id: Filtrar por responsable
        include_archived: Incluir tareas archivadas (por defecto False)
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Lista de tareas con información detallada
    """
    # Query base:
    # - Administradores ven todas las tareas
    # - Otros usuarios ven solo tareas de sus proyectos O tareas asignadas a ellos
    query = db.query(Task).join(Project)

    if current_user.role != "administrador":
        query = query.filter(
            or_(
                Project.owner_id == current_user.id,
                Task.responsible_id == current_user.id
            )
        )

    # Por defecto, excluir tareas archivadas
    if not include_archived:
        query = query.filter(Task.is_archived == False)

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

    # Enriquecer tareas con información adicional
    tasks_with_details = []
    for task in tasks:
        # Obtener información del proyecto
        project = db.query(Project).filter(Project.id == task.project_id).first()

        # Obtener información del responsable
        responsible_name = None
        if task.responsible_id:
            responsible = db.query(User).filter(User.id == task.responsible_id).first()
            if responsible:
                responsible_name = responsible.full_name

        # Obtener información del creador
        creator = db.query(User).filter(User.id == task.created_by).first()
        creator_name = creator.full_name if creator else None

        # Crear diccionario con todos los campos
        task_dict = {
            **task.__dict__,
            "project_name": project.name if project else None,
            "responsible_name": responsible_name,
            "creator_name": creator_name,
        }

        tasks_with_details.append(task_dict)

    return tasks_with_details


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
    # Verificar que el proyecto existe
    # Los administradores pueden crear tareas en cualquier proyecto
    # Los demás usuarios solo en sus propios proyectos
    if current_user.role == "administrador":
        # Administradores: solo verificar que el proyecto existe
        project = db.query(Project).filter(Project.id == task_data.project_id).first()
    else:
        # Otros usuarios: verificar que el proyecto les pertenece
        project = db.query(Project).filter(
            Project.id == task_data.project_id,
            Project.owner_id == current_user.id
        ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado o no tienes permiso para crear tareas en él"
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

    # Enviar notificación Telegram al responsable
    if task_data.responsible_id:
        try:
            send_task_assignment_notification(db_task, responsible, current_user, db)
        except Exception as e:
            # Log error pero no fallar la creación de la tarea
            logger.error(f"Error al enviar notificación de Telegram: {str(e)}")

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
    # Los administradores pueden ver cualquier tarea
    # Otros usuarios solo ven tareas de sus proyectos o asignadas a ellos
    query = db.query(Task).join(Project).filter(Task.id == task_id)

    if current_user.role != "administrador":
        query = query.filter(
            or_(
                Project.owner_id == current_user.id,
                Task.responsible_id == current_user.id
            )
        )

    task = query.first()

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
        HTTPException: Si la tarea no existe o el usuario no tiene permiso
    """
    # Los administradores pueden editar cualquier tarea
    # Otros usuarios pueden editar tareas de sus proyectos o asignadas a ellos
    query = db.query(Task).join(Project).filter(Task.id == task_id)

    if current_user.role != "administrador":
        query = query.filter(
            or_(
                Project.owner_id == current_user.id,
                Task.responsible_id == current_user.id
            )
        )

    task = query.first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o no tienes permiso para editarla"
        )

    # Actualizar campos - usar exclude_unset para distinguir entre None enviado vs campo no enviado
    update_data = task_update.model_dump(exclude_unset=True)

    # Guardar responsable anterior para notificación
    old_responsible_id = task.responsible_id
    old_responsible = None
    if old_responsible_id:
        old_responsible = db.query(User).filter(User.id == old_responsible_id).first()

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
        new_responsible = None
        if update_data['responsible_id']:
            new_responsible = db.query(User).filter(User.id == update_data['responsible_id']).first()
            if not new_responsible:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usuario responsable no encontrado"
                )
        task.responsible_id = update_data['responsible_id']

        # Enviar notificación si cambió el responsable
        if old_responsible_id != update_data['responsible_id'] and new_responsible:
            try:
                send_task_reassignment_notification(
                    task, old_responsible, new_responsible, current_user, db
                )
            except Exception as e:
                # Log error pero no fallar la actualización
                logger.error(f"Error al enviar notificación de Telegram: {str(e)}")
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
    Actualizar solo el estado de la tarea (responsable, dueño o administrador)

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
    # Los administradores pueden cambiar el estado de cualquier tarea
    # Otros usuarios solo pueden cambiar tareas de sus proyectos o asignadas a ellos
    query = db.query(Task).join(Project).filter(Task.id == task_id)

    if current_user.role != "administrador":
        query = query.filter(
            or_(
                Project.owner_id == current_user.id,
                Task.responsible_id == current_user.id
            )
        )

    task = query.first()

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
    # Los administradores pueden completar cualquier tarea
    # Otros usuarios solo pueden completar tareas de sus proyectos o asignadas a ellos
    query = db.query(Task).join(Project).filter(Task.id == task_id)

    if current_user.role != "administrador":
        query = query.filter(
            or_(
                Project.owner_id == current_user.id,
                Task.responsible_id == current_user.id
            )
        )

    task = query.first()

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
    Eliminar tarea (dueño del proyecto, responsable de la tarea o administrador)

    Args:
        task_id: ID de la tarea
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Raises:
        HTTPException: Si la tarea no existe o el usuario no tiene permiso
    """
    task = db.query(Task).join(Project).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )

    # Verificar permisos:
    # - Administrador: puede eliminar cualquier tarea
    # - Dueño del proyecto: puede eliminar tareas de su proyecto
    # - Responsable: puede eliminar tareas asignadas a él
    has_permission = (
        current_user.role == "administrador" or
        task.project.owner_id == current_user.id or
        task.responsible_id == current_user.id
    )

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar esta tarea"
        )

    db.delete(task)
    db.commit()

    return None


@router.patch("/{task_id}/archive", response_model=TaskResponse)
def archive_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Archivar tarea (solo dueño del proyecto o administrador)

    Args:
        task_id: ID de la tarea
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Tarea archivada

    Raises:
        HTTPException: Si la tarea no existe o el usuario no tiene permiso
    """
    # Los administradores pueden archivar cualquier tarea
    # Otros usuarios solo pueden archivar tareas de sus proyectos
    query = db.query(Task).join(Project).filter(Task.id == task_id)

    if current_user.role != "administrador":
        query = query.filter(Project.owner_id == current_user.id)

    task = query.first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o no tienes permiso para archivarla"
        )

    task.is_archived = True
    db.commit()
    db.refresh(task)

    return task


@router.patch("/{task_id}/unarchive", response_model=TaskResponse)
def unarchive_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Desarchivar tarea (solo dueño del proyecto o administrador)

    Args:
        task_id: ID de la tarea
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Tarea desarchivada

    Raises:
        HTTPException: Si la tarea no existe o el usuario no tiene permiso
    """
    # Los administradores pueden desarchivar cualquier tarea
    # Otros usuarios solo pueden desarchivar tareas de sus proyectos
    query = db.query(Task).join(Project).filter(Task.id == task_id)

    if current_user.role != "administrador":
        query = query.filter(Project.owner_id == current_user.id)

    task = query.first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o no tienes permiso para desarchivarla"
        )

    task.is_archived = False
    db.commit()
    db.refresh(task)

    return task
