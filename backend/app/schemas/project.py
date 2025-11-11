"""
Schemas Pydantic para Proyecto
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Schema base de proyecto"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    emoji_icon: Optional[str] = Field("📁", max_length=10)


class ProjectCreate(ProjectBase):
    """Schema para crear proyecto"""
    pass


class ProjectUpdate(BaseModel):
    """Schema para actualizar proyecto"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    emoji_icon: Optional[str] = Field(None, max_length=10)
    is_archived: Optional[bool] = None


class ProjectResponse(ProjectBase):
    """Schema de respuesta de proyecto"""
    id: str
    owner_id: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectWithStats(ProjectResponse):
    """Schema de proyecto con estadísticas de tareas"""
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    pending_tasks: int = 0
    overdue_tasks: int = 0

    model_config = {"from_attributes": True}
