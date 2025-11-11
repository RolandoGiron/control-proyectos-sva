"""
Modelo de Código de Vinculación de Telegram
"""
import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TelegramLinkCode(Base):
    """Modelo de código temporal para vincular Telegram con usuario"""

    __tablename__ = "telegram_link_codes"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    code = Column(String(10), unique=True, nullable=False, index=True)
    expires_at = Column(TIMESTAMP, nullable=False, index=True)
    used_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Relaciones
    user = relationship("User", back_populates="telegram_link_codes")

    def __repr__(self):
        return f"<TelegramLinkCode(id={self.id}, code='{self.code}', user_id={self.user_id})>"
