"""
API endpoints para integración con Telegram
"""
import secrets
import string
import logging
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.telegram_link_code import TelegramLinkCode
from app.schemas.telegram import (
    TelegramLinkCodeResponse,
    TelegramLinkStatusResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def generate_link_code(length: int = 6) -> str:
    """
    Generar código aleatorio para vinculación

    Args:
        length: Longitud del código

    Returns:
        Código alfanumérico en mayúsculas
    """
    alphabet = string.ascii_uppercase + string.digits
    # Excluir caracteres confusos: 0, O, I, 1
    alphabet = alphabet.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@router.post("/generate-code", response_model=TelegramLinkCodeResponse)
async def generate_telegram_link_code(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Generar código de vinculación para Telegram

    - El código expira en 15 minutos
    - Solo puede haber un código activo por usuario
    - Los códigos anteriores se invalidan al generar uno nuevo
    """
    try:
        # Invalidar códigos anteriores no usados
        old_codes = db.query(TelegramLinkCode).filter(
            TelegramLinkCode.user_id == current_user.id,
            TelegramLinkCode.used_at.is_(None)
        ).all()

        for old_code in old_codes:
            db.delete(old_code)

        # Generar nuevo código único
        max_attempts = 10
        code = None
        for _ in range(max_attempts):
            candidate = generate_link_code()
            # Verificar que no existe
            exists = db.query(TelegramLinkCode).filter(
                TelegramLinkCode.code == candidate
            ).first()
            if not exists:
                code = candidate
                break

        if not code:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo generar un código único"
            )

        # Crear registro de código
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        link_code = TelegramLinkCode(
            user_id=current_user.id,
            code=code,
            expires_at=expires_at
        )

        db.add(link_code)
        db.commit()
        db.refresh(link_code)

        logger.info(f"Código de vinculación generado para usuario {current_user.email}: {code}")

        return TelegramLinkCodeResponse(
            code=code,
            expires_at=expires_at,
            bot_username="control_proyecto_hg_bot"
        )

    except Exception as e:
        logger.error(f"Error al generar código de vinculación: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al generar código de vinculación"
        )


@router.get("/status", response_model=TelegramLinkStatusResponse)
async def get_telegram_link_status(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Obtener estado de vinculación de Telegram

    Retorna si la cuenta está vinculada y el chat_id si aplica
    """
    is_linked = current_user.telegram_chat_id is not None

    return TelegramLinkStatusResponse(
        is_linked=is_linked,
        chat_id=current_user.telegram_chat_id
    )


@router.delete("/unlink", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_telegram_account(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Desvincular cuenta de Telegram

    Elimina el chat_id del usuario y invalida todos los códigos de vinculación
    """
    try:
        # Eliminar chat_id
        current_user.telegram_chat_id = None

        # Invalidar códigos pendientes
        db.query(TelegramLinkCode).filter(
            TelegramLinkCode.user_id == current_user.id,
            TelegramLinkCode.used_at.is_(None)
        ).delete()

        db.commit()

        logger.info(f"Cuenta de Telegram desvinculada para usuario {current_user.email}")

    except Exception as e:
        logger.error(f"Error al desvincular Telegram: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al desvincular cuenta de Telegram"
        )
