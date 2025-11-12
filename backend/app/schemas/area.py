"""
Schemas Pydantic para Área
"""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class AreaBase(BaseModel):
    """Schema base de área"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del área")
    description: str | None = Field(None, description="Descripción del área")
    color: str = Field('#3B82F6', max_length=7, description="Color del área en formato hex")
    icon: str = Field('📁', max_length=10, description="Ícono emoji del área")
    is_active: bool = Field(True, description="Si el área está activa")


class AreaCreate(AreaBase):
    """Schema para crear área"""
    pass


class AreaUpdate(BaseModel):
    """Schema para actualizar área"""
    name: str | None = Field(None, min_length=1, max_length=100, description="Nombre del área")
    description: str | None = Field(None, description="Descripción del área")
    color: str | None = Field(None, max_length=7, description="Color del área en formato hex")
    icon: str | None = Field(None, max_length=10, description="Ícono emoji del área")
    is_active: bool | None = Field(None, description="Si el área está activa")


class AreaResponse(AreaBase):
    """Schema de respuesta de área"""
    id: str = Field(..., description="ID del área (UUID)")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        from_attributes = True


class AreaWithStats(AreaResponse):
    """Schema de área con estadísticas"""
    total_users: int = Field(0, description="Total de usuarios en el área")
    total_projects: int = Field(0, description="Total de proyectos en el área")
    total_tasks: int = Field(0, description="Total de tareas en el área")
    tasks_sin_empezar: int = Field(0, description="Tareas sin empezar")
    tasks_en_curso: int = Field(0, description="Tareas en curso")
    tasks_completado: int = Field(0, description="Tareas completadas")

    class Config:
        from_attributes = True
