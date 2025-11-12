"""
Servicio de vinculación de cuentas de Telegram
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db_context
from app.models.user import User
from app.models.area import Area  # Importar Area para evitar error de mapper
from app.models.telegram_link_code import TelegramLinkCode

logger = logging.getLogger(__name__)


class LinkService:
    """Servicio para vincular cuentas de Telegram con usuarios del sistema"""

    async def verify_and_link(self, code: str, chat_id: int) -> dict:
        """
        Verificar código de vinculación y vincular cuenta

        Args:
            code: Código de vinculación generado por el usuario
            chat_id: ID del chat de Telegram

        Returns:
            dict con success: bool, user_name: str (si success), error: str (si no success)
        """
        try:
            with get_db_context() as db:
                # Buscar código de vinculación
                link_code = db.query(TelegramLinkCode).filter(
                    TelegramLinkCode.code == code
                ).first()

                if not link_code:
                    return {
                        'success': False,
                        'error': 'Código de vinculación inválido.'
                    }

                # Verificar que el código no haya sido usado
                if link_code.used_at:
                    return {
                        'success': False,
                        'error': 'Este código ya ha sido utilizado.'
                    }

                # Verificar que el código no haya expirado
                if link_code.expires_at < datetime.utcnow():
                    return {
                        'success': False,
                        'error': 'Este código ha expirado. Genera uno nuevo desde tu perfil.'
                    }

                # Obtener usuario
                user = db.query(User).filter(User.id == link_code.user_id).first()

                if not user:
                    return {
                        'success': False,
                        'error': 'Usuario no encontrado.'
                    }

                # Vincular cuenta
                user.telegram_chat_id = chat_id
                link_code.used_at = datetime.utcnow()

                db.commit()
                db.refresh(user)

                logger.info(f"Cuenta vinculada: {user.email} -> chat_id: {chat_id}")

                return {
                    'success': True,
                    'user_name': user.full_name,
                    'user_email': user.email
                }

        except Exception as e:
            logger.error(f"Error al vincular cuenta: {e}")
            return {
                'success': False,
                'error': 'Error al vincular cuenta. Intenta nuevamente.'
            }
