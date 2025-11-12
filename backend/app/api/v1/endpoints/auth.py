"""
Endpoints de Autenticación
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models import User
from app.schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    LoginResponse,
    Token,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registrar nuevo usuario

    Args:
        user_data: Datos del usuario a crear
        db: Sesión de base de datos

    Returns:
        Usuario creado

    Raises:
        HTTPException: Si el email o teléfono ya existe
    """
    # Verificar si el email ya existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Verificar si el teléfono ya existe (si se proporcionó)
    if user_data.phone_number:
        existing_phone = db.query(User).filter(
            User.phone_number == user_data.phone_number
        ).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de teléfono ya está registrado"
            )

    # Crear usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        role=user_data.role,
        area_id=user_data.area_id,
        is_active=True,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login de usuario

    Args:
        login_data: Credenciales de login
        db: Sesión de base de datos

    Returns:
        Token JWT y datos del usuario

    Raises:
        HTTPException: Si las credenciales son incorrectas
    """
    # Buscar usuario por email
    user = db.query(User).filter(User.email == login_data.email).first()

    # Verificar que el usuario existe y la contraseña es correcta
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que el usuario está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    # Crear token JWT
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "telegram_chat_id": user.telegram_chat_id,
            "role": user.role,
            "area_id": user.area_id,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
    }
