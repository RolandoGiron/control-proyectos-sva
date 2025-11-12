"""
Endpoints para gestión de áreas
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.area import Area
from app.models.project import Project
from app.models.task import Task
from app.schemas.area import AreaCreate, AreaUpdate, AreaResponse, AreaWithStats

router = APIRouter()


@router.get("/", response_model=list[AreaResponse])
def list_areas(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Listar todas las áreas.
    Cualquier usuario autenticado puede ver las áreas.
    """
    query = db.query(Area)

    if is_active is not None:
        query = query.filter(Area.is_active == is_active)

    areas = query.offset(skip).limit(limit).all()
    return areas


@router.get("/with-stats", response_model=list[AreaWithStats])
def list_areas_with_stats(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Listar áreas con estadísticas (total de usuarios y proyectos).
    """
    query = db.query(Area)

    if is_active is not None:
        query = query.filter(Area.is_active == is_active)

    areas = query.offset(skip).limit(limit).all()

    # Agregar estadísticas
    areas_with_stats = []
    for area in areas:
        total_users = db.query(func.count(User.id)).filter(User.area_id == area.id).scalar()
        total_projects = db.query(func.count(Project.id)).filter(Project.area_id == area.id).scalar()

        # Contar tareas a través de los proyectos del área
        total_tasks = db.query(func.count(Task.id)).join(
            Project, Task.project_id == Project.id
        ).filter(Project.area_id == area.id).scalar()

        tasks_sin_empezar = db.query(func.count(Task.id)).join(
            Project, Task.project_id == Project.id
        ).filter(Project.area_id == area.id, Task.status == 'sin_empezar').scalar()

        tasks_en_curso = db.query(func.count(Task.id)).join(
            Project, Task.project_id == Project.id
        ).filter(Project.area_id == area.id, Task.status == 'en_curso').scalar()

        tasks_completado = db.query(func.count(Task.id)).join(
            Project, Task.project_id == Project.id
        ).filter(Project.area_id == area.id, Task.status == 'completado').scalar()

        area_dict = {
            "id": area.id,
            "name": area.name,
            "description": area.description,
            "color": area.color,
            "icon": area.icon,
            "is_active": area.is_active,
            "created_at": area.created_at,
            "updated_at": area.updated_at,
            "total_users": total_users,
            "total_projects": total_projects,
            "total_tasks": total_tasks,
            "tasks_sin_empezar": tasks_sin_empezar,
            "tasks_en_curso": tasks_en_curso,
            "tasks_completado": tasks_completado,
            "stats": {
                "total_projects": total_projects,
                "total_tasks": total_tasks,
                "tasks_sin_empezar": tasks_sin_empezar,
                "tasks_en_curso": tasks_en_curso,
                "tasks_completado": tasks_completado
            }
        }
        areas_with_stats.append(area_dict)

    return areas_with_stats


@router.get("/{area_id}", response_model=AreaResponse)
def get_area(
    area_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener un área por ID.
    """
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área no encontrada"
        )
    return area


@router.post("/", response_model=AreaResponse, status_code=status.HTTP_201_CREATED)
def create_area(
    area_in: AreaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear una nueva área.
    Solo administradores pueden crear áreas.
    """
    # Verificar que el usuario sea administrador
    if current_user.role != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear áreas"
        )

    # Verificar que no exista un área con el mismo nombre
    existing_area = db.query(Area).filter(Area.name == area_in.name).first()
    if existing_area:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un área con ese nombre"
        )

    # Crear área
    area = Area(**area_in.model_dump())
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


@router.put("/{area_id}", response_model=AreaResponse)
def update_area(
    area_id: str,
    area_in: AreaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar un área.
    Solo administradores pueden actualizar áreas.
    """
    # Verificar que el usuario sea administrador
    if current_user.role != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden actualizar áreas"
        )

    # Buscar área
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área no encontrada"
        )

    # Si se está actualizando el nombre, verificar que no exista otro con el mismo nombre
    if area_in.name is not None and area_in.name != area.name:
        existing_area = db.query(Area).filter(Area.name == area_in.name).first()
        if existing_area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un área con ese nombre"
            )

    # Actualizar solo los campos proporcionados
    update_data = area_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(area, field, value)

    db.commit()
    db.refresh(area)
    return area


@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_area(
    area_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Eliminar un área.
    Solo administradores pueden eliminar áreas.
    """
    # Verificar que el usuario sea administrador
    if current_user.role != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar áreas"
        )

    # Buscar área
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área no encontrada"
        )

    # Verificar que no haya usuarios asignados al área
    users_count = db.query(func.count(User.id)).filter(User.area_id == area_id).scalar()
    if users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el área porque tiene {users_count} usuario(s) asignado(s)"
        )

    # Verificar que no haya proyectos asignados al área
    projects_count = db.query(func.count(Project.id)).filter(Project.area_id == area_id).scalar()
    if projects_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el área porque tiene {projects_count} proyecto(s) asignado(s)"
        )

    db.delete(area)
    db.commit()
    return None
