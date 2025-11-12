"""
Tareas de Celery para recordatorios de deadlines
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List

from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.task import Task
from app.models.user import User
from app.models.notification import Notification
from app.bot.notifications import send_telegram_notification

logger = logging.getLogger(__name__)


def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # No cerrar aquí, se cierra en el task


import asyncio

@celery_app.task(bind=True, name='app.workers.reminder_tasks.check_upcoming_deadlines')
def check_upcoming_deadlines(self):
    """
    Verifica tareas con deadlines próximos y envía recordatorios.

    Se ejecuta cada hora y busca tareas que:
    - Tienen deadline configurado
    - No están completadas
    - El deadline está dentro del rango reminder_hours_before
    - No se ha enviado recordatorio previamente

    Returns:
        dict: Resumen de recordatorios enviados
    """
    db = SessionLocal()
    try:
        logger.info("🔔 Iniciando verificación de deadlines próximos...")

        # Obtener hora actual en UTC
        now_utc = datetime.utcnow()

        # Buscar todas las tareas con deadline y no completadas
        tasks_with_deadline = db.query(Task).filter(
            Task.deadline.isnot(None),
            Task.status != 'completado',
            Task.reminder_hours_before.isnot(None),
            Task.responsible_id.isnot(None)
        ).all()

        reminders_sent = 0
        errors = 0

        for task in tasks_with_deadline:
            try:
                # Calcular cuándo enviar el recordatorio
                reminder_time = task.deadline - timedelta(hours=task.reminder_hours_before)

                # Verificar si es momento de enviar el recordatorio
                # Rango: entre la hora del recordatorio y 1 hora después
                if reminder_time <= now_utc < (reminder_time + timedelta(hours=1)):

                    # Verificar si ya se envió recordatorio para esta tarea
                    existing_reminder = db.query(Notification).filter(
                        Notification.task_id == task.id,
                        Notification.type == 'recordatorio',
                        Notification.sent_at >= reminder_time - timedelta(hours=1)
                    ).first()

                    if existing_reminder:
                        logger.debug(f"Recordatorio ya enviado para tarea {task.id}")
                        continue

                    # Obtener usuario responsable
                    user = db.query(User).filter(User.id == task.responsible_id).first()

                    if not user:
                        logger.warning(f"Usuario responsable no encontrado para tarea {task.id}")
                        continue

                    if not user.telegram_chat_id:
                        logger.info(f"Usuario {user.email} no tiene Telegram vinculado, omitiendo recordatorio")
                        continue

                    # Calcular tiempo restante
                    time_left = task.deadline - now_utc
                    hours_left = int(time_left.total_seconds() / 3600)

                    # Construir mensaje
                    if hours_left <= 1:
                        urgency = "⚠️ URGENTE"
                        time_msg = "menos de 1 hora"
                    elif hours_left <= 24:
                        urgency = "⏰"
                        time_msg = f"{hours_left} horas"
                    else:
                        days_left = hours_left // 24
                        urgency = "📅"
                        time_msg = f"{days_left} día{'s' if days_left > 1 else ''}"

                    message = (
                        f"{urgency} <b>Recordatorio de Tarea</b>\n\n"
                        f"<b>Tarea:</b> {task.title}\n"
                        f"<b>Proyecto:</b> {task.project.name if task.project else 'Sin proyecto'}\n"
                        f"<b>Prioridad:</b> {task.priority.capitalize()}\n"
                        f"<b>Deadline:</b> {task.deadline.strftime('%d/%m/%Y %H:%M')}\n"
                        f"<b>Tiempo restante:</b> {time_msg}\n\n"
                    )

                    if task.description:
                        message += f"<b>Descripción:</b> {task.description[:200]}{'...' if len(task.description) > 200 else ''}\n\n"

                    message += f"💡 Usa /tareas para ver todas tus tareas pendientes."

                    # Enviar notificación por Telegram (ejecutar async de forma síncrona)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        success = loop.run_until_complete(
                            send_telegram_notification(
                                user_id=user.id,
                                message=message,
                                db=db
                            )
                        )
                    finally:
                        loop.close()

                    if success:
                        # Registrar notificación en BD
                        notification = Notification(
                            user_id=user.id,
                            task_id=task.id,
                            type='recordatorio',
                            message=f"Recordatorio: {task.title} - Deadline en {time_msg}",
                            sent_at=now_utc
                        )
                        db.add(notification)
                        db.commit()

                        reminders_sent += 1
                        logger.info(f"✅ Recordatorio enviado para tarea '{task.title}' a {user.email}")
                    else:
                        errors += 1
                        logger.error(f"❌ Error al enviar recordatorio para tarea {task.id}")

            except Exception as e:
                errors += 1
                logger.error(f"Error procesando tarea {task.id}: {str(e)}")
                continue

        # Resumen final
        summary = {
            'status': 'completed',
            'reminders_sent': reminders_sent,
            'errors': errors,
            'total_tasks_checked': len(tasks_with_deadline),
            'timestamp': now_utc.isoformat()
        }

        logger.info(
            f"✅ Verificación completada: {reminders_sent} recordatorios enviados, "
            f"{errors} errores, {len(tasks_with_deadline)} tareas verificadas"
        )

        return summary

    except Exception as e:
        logger.error(f"❌ Error en check_upcoming_deadlines: {str(e)}")
        raise
    finally:
        db.close()


# Ya no necesitamos estas funciones wrapper
