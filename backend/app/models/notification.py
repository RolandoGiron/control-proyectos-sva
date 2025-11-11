"""
Modelo de Notificación
"""
import uuid
from sqlalchemy import Column, String, Text, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Tipos de notificaciones"""
    NUEVA_TAREA = "nueva_tarea"
    RECORDATORIO = "recordatorio"
    COMPLETADA = "completada"
    RESUMEN_DIARIO = "resumen_diario"
    RESUMEN_SEMANAL = "resumen_semanal"
    CAMBIO_ESTADO = "cambio_estado"


class Notification(Base):
    """Modelo de Notificación"""

    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    task_id = Column(
        String(36),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    type = Column(Enum(NotificationType, values_callable=lambda obj: [e.value for e in obj]), nullable=False, index=True)
    message = Column(Text, nullable=False)
    sent_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    read_at = Column(TIMESTAMP, nullable=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Relaciones
    user = relationship("User", back_populates="notifications")
    task = relationship("Task", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type.value}', user_id={self.user_id})>"
