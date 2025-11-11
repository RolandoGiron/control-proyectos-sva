"""
Endpoints de Usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash
from app.api.dependencies import get_current_user
from app.models import User
from app.schemas import UserResponse, UserUpdate, UserChangePassword

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Obtener perfil del usuario actual

    Args:
        current_user: Usuario autenticado

    Returns:
        Datos del usuario actual
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Actualizar perfil del usuario actual

    Args:
        user_update: Datos a actualizar
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Usuario actualizado

    Raises:
        HTTPException: Si el teléfono ya está en uso
    """
    # Verificar si el nuevo teléfono ya existe (si se proporcionó y es diferente)
    if user_update.phone_number and user_update.phone_number != current_user.phone_number:
        existing_phone = db.query(User).filter(
            User.phone_number == user_update.phone_number,
            User.id != current_user.id
        ).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de teléfono ya está registrado"
            )

    # Actualizar campos
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.phone_number is not None:
        current_user.phone_number = user_update.phone_number
    if user_update.telegram_chat_id is not None:
        current_user.telegram_chat_id = user_update.telegram_chat_id

    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cambiar contraseña del usuario actual

    Args:
        password_data: Contraseña actual y nueva
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Raises:
        HTTPException: Si la contraseña actual es incorrecta
    """
    # Verificar contraseña actual
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )

    # Actualizar contraseña
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()

    return None


@router.get("/", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar usuarios (solo para referencia en asignación de tareas)

    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Lista de usuarios
    """
    users = db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtener usuario por ID

    Args:
        user_id: ID del usuario (UUID)
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        Usuario encontrado

    Raises:
        HTTPException: Si el usuario no existe
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user
