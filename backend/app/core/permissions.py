"""
Middleware y dependencias para control de permisos por rol
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.task import Task


def require_role(allowed_roles: list[str]):
    """
    Dependencia que requiere que el usuario tenga uno de los roles especificados.

    Args:
        allowed_roles: Lista de roles permitidos (ej: ['administrador', 'supervisor'])

    Returns:
        Función de dependencia que valida el rol del usuario

    Ejemplo:
        @router.get("/admin-only")
        def admin_endpoint(current_user: User = Depends(require_role(['administrador']))):
            return {"message": "Acceso permitido"}
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de los siguientes roles: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependencia que requiere que el usuario sea administrador.
    """
    if current_user.role != 'administrador':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de administrador"
        )
    return current_user


def require_supervisor_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependencia que requiere que el usuario sea supervisor o administrador.
    """
    if current_user.role not in ['administrador', 'supervisor']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de supervisor o administrador"
        )
    return current_user


def can_access_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    """
    Verifica si el usuario puede acceder a un proyecto según su rol:
    - Administrador: Acceso a todos los proyectos
    - Supervisor: Acceso a proyectos de su área
    - Analista: Acceso solo a sus propios proyectos

    Returns:
        El proyecto si el usuario tiene acceso

    Raises:
        HTTPException 403 si no tiene acceso
        HTTPException 404 si el proyecto no existe
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    # Administrador tiene acceso a todo
    if current_user.role == 'administrador':
        return project

    # Supervisor tiene acceso a proyectos de su área
    if current_user.role == 'supervisor':
        if current_user.area_id and project.area_id == current_user.area_id:
            return project
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este proyecto (diferente área)"
        )

    # Analista solo tiene acceso a sus propios proyectos
    if project.owner_id == current_user.id:
        return project

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes acceso a este proyecto"
    )


def can_modify_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    """
    Verifica si el usuario puede modificar un proyecto:
    - Administrador: Puede modificar todos los proyectos
    - Supervisor: Puede modificar proyectos de su área
    - Analista: Solo puede modificar sus propios proyectos
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    # Administrador puede modificar todo
    if current_user.role == 'administrador':
        return project

    # Supervisor puede modificar proyectos de su área
    if current_user.role == 'supervisor':
        if current_user.area_id and project.area_id == current_user.area_id:
            return project
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes modificar este proyecto (diferente área)"
        )

    # Analista solo puede modificar sus propios proyectos
    if project.owner_id == current_user.id:
        return project

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No puedes modificar este proyecto"
    )


def can_access_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Task:
    """
    Verifica si el usuario puede acceder a una tarea según su rol:
    - Administrador: Acceso a todas las tareas
    - Supervisor: Acceso a tareas de proyectos de su área
    - Analista: Acceso a tareas de sus proyectos o tareas asignadas a él
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )

    # Administrador tiene acceso a todo
    if current_user.role == 'administrador':
        return task

    # Cargar el proyecto asociado
    project = db.query(Project).filter(Project.id == task.project_id).first()

    # Supervisor tiene acceso a tareas de proyectos de su área
    if current_user.role == 'supervisor':
        if current_user.area_id and project and project.area_id == current_user.area_id:
            return task
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta tarea (diferente área)"
        )

    # Analista tiene acceso si:
    # 1. Es el dueño del proyecto
    # 2. Es el creador de la tarea
    # 3. Es el responsable de la tarea
    if (project and project.owner_id == current_user.id) or \
       task.created_by == current_user.id or \
       task.responsible_id == current_user.id:
        return task

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes acceso a esta tarea"
    )


def can_modify_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Task:
    """
    Verifica si el usuario puede modificar una tarea:
    - Administrador: Puede modificar todas las tareas
    - Supervisor: Puede modificar tareas de proyectos de su área
    - Analista: Puede modificar tareas de sus proyectos o tareas donde es responsable
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )

    # Administrador puede modificar todo
    if current_user.role == 'administrador':
        return task

    # Cargar el proyecto asociado
    project = db.query(Project).filter(Project.id == task.project_id).first()

    # Supervisor puede modificar tareas de proyectos de su área
    if current_user.role == 'supervisor':
        if current_user.area_id and project and project.area_id == current_user.area_id:
            return task
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes modificar esta tarea (diferente área)"
        )

    # Analista puede modificar si es dueño del proyecto o responsable de la tarea
    if (project and project.owner_id == current_user.id) or \
       task.responsible_id == current_user.id:
        return task

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No puedes modificar esta tarea"
    )
