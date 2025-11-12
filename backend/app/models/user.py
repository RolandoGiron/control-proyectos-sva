"""
Modelo de Usuario
"""
import uuid
from sqlalchemy import Column, String, Boolean, BigInteger, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """Modelo de Usuario del sistema"""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    telegram_chat_id = Column(BigInteger, unique=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    role = Column(
        Enum('administrador', 'supervisor', 'analista', name='user_role'),
        nullable=False,
        default='analista',
        index=True
    )
    area_id = Column(String(36), ForeignKey('areas.id', ondelete='SET NULL'), nullable=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relaciones
    area = relationship("Area", back_populates="users")
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.created_by")
    assigned_tasks = relationship("Task", back_populates="responsible", foreign_keys="Task.responsible_id")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    telegram_link_codes = relationship("TelegramLinkCode", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.full_name}')>"
