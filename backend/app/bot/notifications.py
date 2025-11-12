"""
Servicio de notificaciones push via Telegram
"""
import logging
from typing import Optional
from datetime import datetime
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.project import Project

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio para enviar notificaciones push via Telegram"""

    def __init__(self, bot):
        """
        Inicializar servicio de notificaciones

        Args:
            bot: Instancia de TelegramBot
        """
        self.bot = bot

    async def notify_new_task(self, task: Task, responsible: User, creator: User):
        """
        Notificar al responsable sobre una nueva tarea asignada

        Args:
            task: Tarea recién creada
            responsible: Usuario responsable
            creator: Usuario que creó la tarea
        """
        if not responsible.telegram_chat_id:
            logger.info(f"Usuario {responsible.email} no tiene Telegram vinculado")
            return

        # Formatear deadline
        deadline_text = "Sin deadline"
        if task.deadline:
            deadline_text = task.deadline.strftime('%d/%m/%Y %H:%M')

        # Emoji de prioridad
        priority_emoji = {
            'baja': '🟢',
            'media': '🟡',
            'alta': '🔴'
        }.get(task.priority.value if hasattr(task.priority, 'value') else task.priority, '🟡')

        message = (
            f"📋 <b>Nueva Tarea Asignada</b>\n\n"
            f"{priority_emoji} <b>{task.title}</b>\n\n"
            f"📁 Proyecto: {task.project.name if task.project else 'Sin proyecto'}\n"
            f"👤 Asignada por: {creator.full_name}\n"
            f"📅 Deadline: {deadline_text}\n\n"
        )

        if task.description:
            # Truncar descripción si es muy larga
            desc = task.description[:200]
            if len(task.description) > 200:
                desc += "..."
            message += f"📝 Descripción:\n{desc}\n\n"

        message += f"💡 ID: <code>{task.id[:8]}</code>"

        await self.bot.send_message(
            chat_id=responsible.telegram_chat_id,
            text=message
        )

        logger.info(f"Notificación de nueva tarea enviada a {responsible.email}")

    async def notify_task_status_change(
        self,
        task: Task,
        old_status: TaskStatus,
        new_status: TaskStatus,
        changed_by: User
    ):
        """
        Notificar sobre cambio de estado de tarea

        Args:
            task: Tarea modificada
            old_status: Estado anterior
            new_status: Estado nuevo
            changed_by: Usuario que cambió el estado
        """
        # Notificar al responsable (si no fue él quien cambió)
        if task.responsible and task.responsible.telegram_chat_id:
            if task.responsible_id != changed_by.id:
                await self._send_status_change_notification(
                    task, old_status, new_status, changed_by,
                    task.responsible.telegram_chat_id,
                    f"del estado de tu tarea"
                )

        # Notificar al dueño del proyecto (si no fue él quien cambió y no es el responsable)
        if (task.project and task.project.owner and
            task.project.owner.telegram_chat_id and
            task.project.owner_id != changed_by.id and
            task.project.owner_id != task.responsible_id):
            await self._send_status_change_notification(
                task, old_status, new_status, changed_by,
                task.project.owner.telegram_chat_id,
                f"del estado de una tarea en tu proyecto"
            )

    async def _send_status_change_notification(
        self,
        task: Task,
        old_status: TaskStatus,
        new_status: TaskStatus,
        changed_by: User,
        chat_id: int,
        context: str
    ):
        """
        Enviar notificación de cambio de estado

        Args:
            task: Tarea modificada
            old_status: Estado anterior
            new_status: Estado nuevo
            changed_by: Usuario que cambió
            chat_id: Chat de Telegram destino
            context: Contexto del mensaje
        """
        status_emoji = {
            TaskStatus.SIN_EMPEZAR: '⚪',
            TaskStatus.EN_CURSO: '🔵',
            TaskStatus.COMPLETADO: '✅'
        }

        status_display = {
            TaskStatus.SIN_EMPEZAR: 'Sin Empezar',
            TaskStatus.EN_CURSO: 'En Curso',
            TaskStatus.COMPLETADO: 'Completado'
        }

        old_emoji = status_emoji.get(old_status, '⚪')
        new_emoji = status_emoji.get(new_status, '⚪')
        old_text = status_display.get(old_status, 'Sin Empezar')
        new_text = status_display.get(new_status, 'Sin Empezar')

        message = (
            f"🔄 <b>Cambio de Estado</b>\n\n"
            f"Se actualizó {context}:\n\n"
            f"<b>{task.title}</b>\n"
            f"📁 Proyecto: {task.project.name if task.project else 'Sin proyecto'}\n\n"
            f"{old_emoji} {old_text} → {new_emoji} {new_text}\n\n"
            f"👤 Actualizado por: {changed_by.full_name}\n"
            f"💡 ID: <code>{task.id[:8]}</code>"
        )

        await self.bot.send_message(
            chat_id=chat_id,
            text=message
        )

        logger.info(f"Notificación de cambio de estado enviada al chat {chat_id}")

    async def notify_task_completed(self, task: Task, completed_by: User):
        """
        Notificar sobre tarea completada

        Args:
            task: Tarea completada
            completed_by: Usuario que completó la tarea
        """
        # Notificar al dueño del proyecto (si no fue él quien completó)
        if (task.project and task.project.owner and
            task.project.owner.telegram_chat_id and
            task.project.owner_id != completed_by.id):

            message = (
                f"✅ <b>Tarea Completada</b>\n\n"
                f"Se completó una tarea en tu proyecto:\n\n"
                f"<b>{task.title}</b>\n"
                f"📁 Proyecto: {task.project.name}\n\n"
                f"👤 Completada por: {completed_by.full_name}\n"
                f"⏱️ Completada: {task.completed_at.strftime('%d/%m/%Y %H:%M') if task.completed_at else 'Ahora'}\n"
                f"💡 ID: <code>{task.id[:8]}</code>"
            )

            await self.bot.send_message(
                chat_id=task.project.owner.telegram_chat_id,
                text=message
            )

            logger.info(f"Notificación de tarea completada enviada a {task.project.owner.email}")

    async def notify_deadline_reminder(self, task: Task, hours_remaining: int):
        """
        Enviar recordatorio de deadline próximo

        Args:
            task: Tarea con deadline próximo
            hours_remaining: Horas restantes hasta el deadline
        """
        if not task.responsible or not task.responsible.telegram_chat_id:
            logger.info(f"Tarea {task.id} no tiene responsable con Telegram vinculado")
            return

        # Emoji según urgencia
        if hours_remaining <= 2:
            urgency_emoji = "🚨"
            urgency_text = "¡MUY URGENTE!"
        elif hours_remaining <= 24:
            urgency_emoji = "⚠️"
            urgency_text = "Urgente"
        else:
            urgency_emoji = "⏰"
            urgency_text = "Recordatorio"

        # Formatear tiempo restante
        if hours_remaining < 1:
            time_text = "menos de 1 hora"
        elif hours_remaining == 1:
            time_text = "1 hora"
        elif hours_remaining < 24:
            time_text = f"{hours_remaining} horas"
        elif hours_remaining == 24:
            time_text = "1 día"
        else:
            days = hours_remaining // 24
            time_text = f"{days} días"

        priority_emoji = {
            'baja': '🟢',
            'media': '🟡',
            'alta': '🔴'
        }.get(task.priority.value if hasattr(task.priority, 'value') else task.priority, '🟡')

        message = (
            f"{urgency_emoji} <b>{urgency_text}: Deadline Próximo</b>\n\n"
            f"{priority_emoji} <b>{task.title}</b>\n\n"
            f"📁 Proyecto: {task.project.name if task.project else 'Sin proyecto'}\n"
            f"📅 Deadline: {task.deadline.strftime('%d/%m/%Y %H:%M')}\n"
            f"⏳ Tiempo restante: <b>{time_text}</b>\n\n"
        )

        # Mostrar estado actual
        status_display = {
            'sin_empezar': '⚪ Sin Empezar',
            'en_curso': '🔵 En Curso',
            'completado': '✅ Completado'
        }
        status = task.status.value if hasattr(task.status, 'value') else task.status
        message += f"Estado actual: {status_display.get(status, '⚪ Sin Empezar')}\n\n"

        if task.description:
            desc = task.description[:150]
            if len(task.description) > 150:
                desc += "..."
            message += f"📝 {desc}\n\n"

        message += f"💡 ID: <code>{task.id[:8]}</code>"

        await self.bot.send_message(
            chat_id=task.responsible.telegram_chat_id,
            text=message
        )

        logger.info(f"Recordatorio de deadline enviado a {task.responsible.email}")


# ==============================================================================
# Helper function para Celery workers
# ==============================================================================

async def send_telegram_notification(user_id: str, message: str, db):
    """
    Envía notificación directa por Telegram sin necesidad de instancia del bot.

    Esta función es usada por los workers de Celery para enviar notificaciones.

    Args:
        user_id: UUID del usuario
        message: Mensaje a enviar (puede incluir HTML)
        db: Sesión de base de datos

    Returns:
        bool: True si se envió exitosamente, False en caso contrario
    """
    try:
        from telegram import Bot
        import os

        # Obtener usuario
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.error(f"Usuario {user_id} no encontrado")
            return False

        if not user.telegram_chat_id:
            logger.info(f"Usuario {user.email} no tiene Telegram vinculado")
            return False

        # Obtener token del bot
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN no configurado")
            return False

        # Crear instancia del bot y enviar mensaje
        bot = Bot(token=bot_token)
        await bot.send_message(
            chat_id=user.telegram_chat_id,
            text=message,
            parse_mode='HTML'
        )

        logger.info(f"Notificación enviada exitosamente a {user.email}")
        return True

    except Exception as e:
        logger.error(f"Error al enviar notificación a usuario {user_id}: {str(e)}")
        return False
