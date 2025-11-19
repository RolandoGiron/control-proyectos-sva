"""
Endpoints de Proyectos
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.core.permissions import can_access_project, can_modify_project
from app.models import User, Project, Task
from app.models.task import TaskStatus
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectWithStats

router = APIRouter()


@router.get("/", response_model=list[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_archived: bool = Query(False),
    area_id: Optional[str] = Query(None, description="Filtrar por área (opcional)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar proyectos según el rol del usuario:
    - Administrador: Ve todos los proyectos
    - Supervisor: Ve proyectos de su área
    - Analista: Ve proyectos que le pertenecen O donde tiene tareas asignadas

    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        include_archived: Incluir proyectos archivados
        area_id: Filtrar por área (solo para administradores y supervisores)
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Lista de proyectos según permisos
    """
    query = db.query(Project)

    # Aplicar filtros según rol
    if current_user.role == 'administrador':
        # Administrador ve todos los proyectos
        if area_id:
            query = query.filter(Project.area_id == area_id)
    elif current_user.role == 'supervisor':
        # Supervisor ve proyectos de su área
        if current_user.area_id:
            query = query.filter(Project.area_id == current_user.area_id)
        else:
            # Si no tiene área asignada, no ve ningún proyecto
            query = query.filter(False)
    else:
        # Analista ve proyectos que le pertenecen O donde tiene tareas asignadas
        query = query.outerjoin(Task, Project.id == Task.project_id).filter(
            or_(
                Project.owner_id == current_user.id,
                Task.responsible_id == current_user.id
            )
        ).distinct()

    if not include_archived:
        query = query.filter(Project.is_archived == False)

    projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
    return projects


@router.get("/with-stats", response_model=list[ProjectWithStats])
def list_projects_with_stats(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_archived: bool = Query(False),
    area_id: Optional[str] = Query(None, description="Filtrar por área (opcional)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar proyectos con estadísticas de tareas según el rol del usuario

    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        include_archived: Incluir proyectos archivados
        area_id: Filtrar por área (solo para administradores y supervisores)
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Lista de proyectos con estadísticas según permisos
    """
    from datetime import datetime

    query = db.query(Project)

    # Aplicar filtros según rol
    if current_user.role == 'administrador':
        if area_id:
            query = query.filter(Project.area_id == area_id)
    elif current_user.role == 'supervisor':
        if current_user.area_id:
            query = query.filter(Project.area_id == current_user.area_id)
        else:
            query = query.filter(False)
    else:
        # Analista ve proyectos que le pertenecen O donde tiene tareas asignadas
        query = query.outerjoin(Task, Project.id == Task.project_id).filter(
            or_(
                Project.owner_id == current_user.id,
                Task.responsible_id == current_user.id
            )
        ).distinct()

    if not include_archived:
        query = query.filter(Project.is_archived == False)

    projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()

    # Agregar estadísticas a cada proyecto
    projects_with_stats = []
    for project in projects:
        # Contar tareas por estado
        total_tasks = db.query(func.count(Task.id)).filter(Task.project_id == project.id).scalar()
        completed_tasks = db.query(func.count(Task.id)).filter(
            Task.project_id == project.id,
            Task.status == TaskStatus.COMPLETADO
        ).scalar()
        in_progress_tasks = db.query(func.count(Task.id)).filter(
            Task.project_id == project.id,
            Task.status == TaskStatus.EN_CURSO
        ).scalar()
        pending_tasks = db.query(func.count(Task.id)).filter(
            Task.project_id == project.id,
            Task.status == TaskStatus.SIN_EMPEZAR
        ).scalar()
        overdue_tasks = db.query(func.count(Task.id)).filter(
            Task.project_id == project.id,
            Task.deadline < datetime.utcnow(),
            Task.status != TaskStatus.COMPLETADO
        ).scalar()

        project_dict = {
            **project.__dict__,
            "total_tasks": total_tasks or 0,
            "completed_tasks": completed_tasks or 0,
            "in_progress_tasks": in_progress_tasks or 0,
            "pending_tasks": pending_tasks or 0,
            "overdue_tasks": overdue_tasks or 0,
        }
        projects_with_stats.append(project_dict)

    return projects_with_stats


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Crear nuevo proyecto

    Args:
        project_data: Datos del proyecto a crear
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Proyecto creado
    """
    db_project = Project(
        name=project_data.name,
        description=project_data.description,
        emoji_icon=project_data.emoji_icon,
        area_id=project_data.area_id,
        owner_id=current_user.id,
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project: Project = Depends(can_access_project),
):
    """
    Obtener proyecto por ID (con validación de permisos por rol)

    Returns:
        Proyecto encontrado

    Raises:
        HTTPException: Si el proyecto no existe o el usuario no tiene acceso
    """
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_update: ProjectUpdate,
    project: Project = Depends(can_modify_project),
    db: Session = Depends(get_db),
):
    """
    Actualizar proyecto (con validación de permisos por rol)

    Args:
        project_update: Datos a actualizar
        project: Proyecto validado por permisos
        db: Sesión de base de datos

    Returns:
        Proyecto actualizado
    """
    # Actualizar solo los campos proporcionados
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project: Project = Depends(can_modify_project),
    db: Session = Depends(get_db),
):
    """
    Eliminar proyecto (y todas sus tareas en cascada)
    Con validación de permisos por rol

    Args:
        project: Proyecto validado por permisos
        db: Sesión de base de datos
    """
    db.delete(project)
    db.commit()

    return None


@router.patch("/{project_id}/archive", response_model=ProjectResponse)
def archive_project(
    project: Project = Depends(can_modify_project),
    db: Session = Depends(get_db),
):
    """
    Archivar proyecto (con validación de permisos por rol)

    Args:
        project: Proyecto validado por permisos
        db: Sesión de base de datos

    Returns:
        Proyecto archivado
    """
    project.is_archived = True
    db.commit()
    db.refresh(project)

    return project


@router.patch("/{project_id}/unarchive", response_model=ProjectResponse)
def unarchive_project(
    project: Project = Depends(can_modify_project),
    db: Session = Depends(get_db),
):
    """
    Desarchivar proyecto (con validación de permisos por rol)

    Args:
        project: Proyecto validado por permisos
        db: Sesión de base de datos

    Returns:
        Proyecto desarchivado
    """
    project.is_archived = False
    db.commit()
    db.refresh(project)

    return project
