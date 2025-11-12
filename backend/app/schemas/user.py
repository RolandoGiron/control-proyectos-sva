"""
Schemas Pydantic para Usuario
"""
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

# Tipos literales para role
UserRole = Literal['administrador', 'supervisor', 'analista']


class UserBase(BaseModel):
    """Schema base de usuario"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    role: UserRole = Field('analista', description="Rol del usuario en el sistema")
    area_id: Optional[str] = Field(None, description="ID del área a la que pertenece el usuario")


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validar que la contraseña tenga requisitos mínimos"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        return v


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    telegram_chat_id: Optional[int] = None
    role: Optional[UserRole] = Field(None, description="Rol del usuario en el sistema")
    area_id: Optional[str] = Field(None, description="ID del área a la que pertenece el usuario")


class UserChangePassword(BaseModel):
    """Schema para cambiar contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validar que la contraseña tenga requisitos mínimos"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        return v


class UserResponse(UserBase):
    """Schema de respuesta de usuario"""
    id: str
    telegram_chat_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserInDB(UserResponse):
    """Schema de usuario en base de datos (incluye password_hash)"""
    password_hash: str

    model_config = {"from_attributes": True}
