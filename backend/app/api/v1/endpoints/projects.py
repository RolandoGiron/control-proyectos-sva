"""
Endpoints de Proyectos
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models import User, Project, Task
from app.models.task import TaskStatus
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectWithStats

router = APIRouter()


@router.get("/", response_model=list[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_archived: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar proyectos del usuario actual

    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        include_archived: Incluir proyectos archivados
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Lista de proyectos
    """
    query = db.query(Project).filter(Project.owner_id == current_user.id)

    if not include_archived:
        query = query.filter(Project.is_archived == False)

    projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
    return projects


@router.get("/with-stats", response_model=list[ProjectWithStats])
def list_projects_with_stats(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_archived: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar proyectos con estadísticas de tareas

    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        include_archived: Incluir proyectos archivados
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Lista de proyectos con estadísticas
    """
    from datetime import datetime

    query = db.query(Project).filter(Project.owner_id == current_user.id)

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
        owner_id=current_user.id,
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtener proyecto por ID

    Args:
        project_id: ID del proyecto
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Proyecto encontrado

    Raises:
        HTTPException: Si el proyecto no existe o no pertenece al usuario
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Actualizar proyecto

    Args:
        project_id: ID del proyecto
        project_update: Datos a actualizar
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Proyecto actualizado

    Raises:
        HTTPException: Si el proyecto no existe o no pertenece al usuario
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    # Actualizar campos
    if project_update.name is not None:
        project.name = project_update.name
    if project_update.description is not None:
        project.description = project_update.description
    if project_update.emoji_icon is not None:
        project.emoji_icon = project_update.emoji_icon
    if project_update.is_archived is not None:
        project.is_archived = project_update.is_archived

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Eliminar proyecto (y todas sus tareas en cascada)

    Args:
        project_id: ID del proyecto
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Raises:
        HTTPException: Si el proyecto no existe o no pertenece al usuario
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    db.delete(project)
    db.commit()

    return None


@router.patch("/{project_id}/archive", response_model=ProjectResponse)
def archive_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Archivar proyecto

    Args:
        project_id: ID del proyecto
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Proyecto archivado

    Raises:
        HTTPException: Si el proyecto no existe o no pertenece al usuario
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    project.is_archived = True
    db.commit()
    db.refresh(project)

    return project


@router.patch("/{project_id}/unarchive", response_model=ProjectResponse)
def unarchive_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Desarchivar proyecto

    Args:
        project_id: ID del proyecto
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Proyecto desarchivado

    Raises:
        HTTPException: Si el proyecto no existe o no pertenece al usuario
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    project.is_archived = False
    db.commit()
    db.refresh(project)

    return project
