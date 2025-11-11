"""
Schemas Pydantic para Autenticación
"""
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Schema de token JWT"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema de datos dentro del token"""
    user_id: str
    email: str


class LoginRequest(BaseModel):
    """Schema para request de login"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema de respuesta de login"""
    access_token: str
    token_type: str = "bearer"
    user: dict  # UserResponse serializado
