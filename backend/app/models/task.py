"""
Modelo de Tarea
"""
import uuid
from sqlalchemy import Column, String, Text, Enum, DateTime, TIMESTAMP, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class TaskStatus(str, enum.Enum):
    """Estados de una tarea"""
    SIN_EMPEZAR = "sin_empezar"
    EN_CURSO = "en_curso"
    COMPLETADO = "completado"


class TaskPriority(str, enum.Enum):
    """Prioridades de una tarea"""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class Task(Base):
    """Modelo de Tarea"""

    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        Enum(TaskStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=TaskStatus.SIN_EMPEZAR,
        nullable=False,
        index=True
    )
    priority = Column(
        Enum(TaskPriority, values_callable=lambda obj: [e.value for e in obj]),
        default=TaskPriority.MEDIA,
        nullable=False,
        index=True
    )
    responsible_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    deadline = Column(DateTime, nullable=True, index=True)
    reminder_hours_before = Column(Integer, default=24, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_by = Column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relaciones
    project = relationship("Project", back_populates="tasks")
    responsible = relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[responsible_id]
    )
    creator = relationship(
        "User",
        back_populates="created_tasks",
        foreign_keys=[created_by]
    )
    notifications = relationship("Notification", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status.value}')>"
