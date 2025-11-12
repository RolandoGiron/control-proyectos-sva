"""
Schemas para integración con Telegram
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TelegramLinkCodeResponse(BaseModel):
    """Respuesta al generar código de vinculación"""
    code: str = Field(..., description="Código de vinculación (6 caracteres)")
    expires_at: datetime = Field(..., description="Fecha de expiración del código")
    bot_username: str = Field(..., description="Username del bot para vincular")

    model_config = {"from_attributes": True}


class TelegramLinkStatusResponse(BaseModel):
    """Estado de vinculación de Telegram"""
    is_linked: bool = Field(..., description="Si la cuenta está vinculada")
    chat_id: Optional[int] = Field(None, description="ID del chat de Telegram si está vinculado")

    model_config = {"from_attributes": True}
