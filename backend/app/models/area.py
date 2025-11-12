"""
Modelo de Área
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Area(Base):
    """Modelo de área o departamento"""

    __tablename__ = "areas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=False, default='#3B82F6')
    icon = Column(String(10), nullable=False, default='📁')
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="area")
    projects = relationship("Project", back_populates="area")

    def __repr__(self):
        return f"<Area {self.name}>"
