"""
Schemas Pydantic para Tarea
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import uuid

from app.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """Schema base de tarea"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.SIN_EMPEZAR
    priority: TaskPriority = TaskPriority.MEDIA
    responsible_id: Optional[str] = None
    deadline: Optional[datetime] = None
    reminder_hours_before: Optional[int] = Field(24, ge=1, le=168)  # Entre 1 y 168 horas (7 días)


class TaskCreate(TaskBase):
    """Schema para crear tarea"""
    project_id: str

    @field_validator('project_id', 'responsible_id')
    @classmethod
    def validate_uuid(cls, v: Optional[str]) -> Optional[str]:
        """Validar que sea un UUID válido si se proporciona"""
        if v is None:
            return v
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError('Debe ser un UUID válido')


class TaskUpdate(BaseModel):
    """Schema para actualizar tarea"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    responsible_id: Optional[str] = None
    deadline: Optional[datetime] = None
    reminder_hours_before: Optional[int] = Field(None, ge=1, le=168)

    @field_validator('responsible_id')
    @classmethod
    def validate_uuid(cls, v: Optional[str]) -> Optional[str]:
        """Validar que sea un UUID válido si se proporciona"""
        if v is None:
            return v
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError('responsible_id debe ser un UUID válido')


class TaskStatusUpdate(BaseModel):
    """Schema para actualizar solo el estado de una tarea"""
    status: TaskStatus


class TaskResponse(TaskBase):
    """Schema de respuesta de tarea"""
    id: str
    project_id: str
    completed_at: Optional[datetime] = None
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskWithDetails(TaskResponse):
    """Schema de tarea con detalles extendidos"""
    project_name: Optional[str] = None
    responsible_name: Optional[str] = None
    creator_name: Optional[str] = None
    deadline_status: Optional[str] = None  # "Vencido", "Urgente", "En plazo", etc.

    model_config = {"from_attributes": True}
