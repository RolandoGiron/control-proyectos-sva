"""
Tareas de Celery para resúmenes diarios y semanales
"""
import logging
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, List

from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.models.notification import Notification
from app.models.project import Project
from app.bot.notifications import send_telegram_notification

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='app.workers.summary_tasks.send_daily_summary')
def send_daily_summary(self):
    """
    Envía resumen diario de tareas a todos los usuarios con Telegram vinculado.

    Se ejecuta diariamente a las 8:00 AM y envía:
    - Tareas con deadline hoy
    - Tareas pendientes sin deadline
    - Resumen de estado de tareas del usuario

    Returns:
        dict: Resumen de envíos realizados
    """
    db = SessionLocal()
    try:
        logger.info("📊 Iniciando envío de resúmenes diarios...")

        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # Obtener usuarios con Telegram vinculado
        users_with_telegram = db.query(User).filter(
            User.telegram_chat_id.isnot(None),
            User.is_active == True
        ).all()

        summaries_sent = 0
        errors = 0

        for user in users_with_telegram:
            try:
                # Tareas con deadline hoy
                tasks_today = db.query(Task).filter(
                    Task.responsible_id == user.id,
                    Task.status != TaskStatus.COMPLETADO,
                    Task.deadline >= today_start,
                    Task.deadline < today_end
                ).order_by(Task.deadline).all()

                # Tareas sin empezar
                tasks_not_started = db.query(Task).filter(
                    Task.responsible_id == user.id,
                    Task.status == TaskStatus.SIN_EMPEZAR
                ).count()

                # Tareas en curso
                tasks_in_progress = db.query(Task).filter(
                    Task.responsible_id == user.id,
                    Task.status == TaskStatus.EN_CURSO
                ).count()

                # Tareas vencidas (deadline pasado y no completadas)
                tasks_overdue = db.query(Task).filter(
                    Task.responsible_id == user.id,
                    Task.status != TaskStatus.COMPLETADO,
                    Task.deadline < now
                ).count()

                # Construir mensaje
                message = f"🌅 <b>Buenos días, {user.full_name}!</b>\n\n"
                message += f"📋 <b>Resumen Diario</b> - {today_start.strftime('%d/%m/%Y')}\n\n"

                # Estadísticas generales
                message += f"📊 <b>Estado de tus tareas:</b>\n"
                message += f"• Sin empezar: {tasks_not_started}\n"
                message += f"• En curso: {tasks_in_progress}\n"

                if tasks_overdue > 0:
                    message += f"• ⚠️ Vencidas: {tasks_overdue}\n"

                message += "\n"

                # Tareas con deadline hoy
                if tasks_today:
                    message += f"⏰ <b>Tareas para hoy ({len(tasks_today)}):</b>\n\n"

                    for task in tasks_today[:5]:  # Máximo 5 tareas
                        priority_emoji = {
                            'alta': '🔴',
                            'media': '🟡',
                            'baja': '🟢'
                        }.get(task.priority, '⚪')

                        time_str = task.deadline.strftime('%H:%M') if task.deadline else ''
                        message += f"{priority_emoji} <b>{task.title}</b>\n"
                        message += f"   🕐 {time_str} | {task.project.name if task.project else 'Sin proyecto'}\n"

                    if len(tasks_today) > 5:
                        message += f"\n... y {len(tasks_today) - 5} tarea(s) más\n"
                else:
                    message += "✅ <b>No tienes tareas con deadline para hoy.</b>\n"

                message += "\n💡 Usa /tareas para ver todas tus tareas o /hoy para las de hoy."

                # Enviar notificación (ejecutar async de forma síncrona)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    success = loop.run_until_complete(
                        send_telegram_notification(user.id, message, db)
                    )
                finally:
                    loop.close()

                if success:
                    # Registrar en BD
                    notification = Notification(
                        user_id=user.id,
                        type='resumen_diario',
                        message=f"Resumen diario: {tasks_today.__len__()} tareas hoy, {tasks_overdue} vencidas",
                        sent_at=now
                    )
                    db.add(notification)
                    db.commit()

                    summaries_sent += 1
                    logger.info(f"✅ Resumen diario enviado a {user.email}")
                else:
                    errors += 1
                    logger.error(f"❌ Error al enviar resumen diario a {user.email}")

            except Exception as e:
                errors += 1
                logger.error(f"Error procesando resumen para usuario {user.id}: {str(e)}")
                continue

        summary = {
            'status': 'completed',
            'summaries_sent': summaries_sent,
            'errors': errors,
            'total_users': len(users_with_telegram),
            'timestamp': now.isoformat()
        }

        logger.info(
            f"✅ Resúmenes diarios completados: {summaries_sent} enviados, "
            f"{errors} errores, {len(users_with_telegram)} usuarios"
        )

        return summary

    except Exception as e:
        logger.error(f"❌ Error en send_daily_summary: {str(e)}")
        raise
    finally:
        db.close()


@celery_app.task(bind=True, name='app.workers.summary_tasks.send_weekly_summary')
def send_weekly_summary(self):
    """
    Envía resumen semanal de tareas a todos los usuarios con Telegram vinculado.

    Se ejecuta los lunes a las 9:00 AM y envía:
    - Tareas completadas la semana pasada
    - Tareas pendientes para esta semana
    - Estadísticas de productividad

    Returns:
        dict: Resumen de envíos realizados
    """
    db = SessionLocal()
    try:
        logger.info("📊 Iniciando envío de resúmenes semanales...")

        now = datetime.utcnow()

        # Inicio de esta semana (lunes 00:00)
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        # Fin de esta semana (domingo 23:59)
        week_end = week_start + timedelta(days=7)

        # Inicio de semana pasada
        last_week_start = week_start - timedelta(days=7)

        # Obtener usuarios con Telegram vinculado
        users_with_telegram = db.query(User).filter(
            User.telegram_chat_id.isnot(None),
            User.is_active == True
        ).all()

        summaries_sent = 0
        errors = 0

        for user in users_with_telegram:
            try:
                # Tareas completadas la semana pasada
                tasks_completed_last_week = db.query(Task).filter(
                    Task.responsible_id == user.id,
                    Task.status == TaskStatus.COMPLETADO,
                    Task.completed_at >= last_week_start,
                    Task.completed_at < week_start
                ).count()

                # Tareas para esta semana
                tasks_this_week = db.query(Task).filter(
                    Task.responsible_id == user.id,
                    Task.status != TaskStatus.COMPLETADO,
                    Task.deadline >= week_start,
                    Task.deadline < week_end
                ).order_by(Task.deadline).all()

                # Tareas vencidas
                tasks_overdue = db.query(Task).filter(
                    Task.responsible_id == user.id,
                    Task.status != TaskStatus.COMPLETADO,
                    Task.deadline < now
                ).count()

                # Total de tareas asignadas
                total_tasks = db.query(Task).filter(
                    Task.responsible_id == user.id
                ).count()

                # Total completadas (histórico)
                total_completed = db.query(Task).filter(
                    Task.responsible_id == user.id,
                    Task.status == TaskStatus.COMPLETADO
                ).count()

                # Tasa de completación
                completion_rate = (total_completed / total_tasks * 100) if total_tasks > 0 else 0

                # Construir mensaje
                message = f"📈 <b>Resumen Semanal</b>\n\n"
                message += f"Hola {user.full_name},\n\n"

                # Semana pasada
                message += f"📅 <b>Semana Pasada:</b>\n"
                message += f"✅ Completaste {tasks_completed_last_week} tarea(s)\n\n"

                # Esta semana
                if tasks_this_week:
                    message += f"📋 <b>Esta Semana ({len(tasks_this_week)} tareas):</b>\n\n"

                    for task in tasks_this_week[:7]:  # Máximo 7 tareas
                        priority_emoji = {
                            'alta': '🔴',
                            'media': '🟡',
                            'baja': '🟢'
                        }.get(task.priority, '⚪')

                        day_name = task.deadline.strftime('%A %d/%m') if task.deadline else 'Sin fecha'
                        message += f"{priority_emoji} <b>{task.title}</b>\n"
                        message += f"   📅 {day_name} | {task.project.name if task.project else 'Sin proyecto'}\n"

                    if len(tasks_this_week) > 7:
                        message += f"\n... y {len(tasks_this_week) - 7} tarea(s) más\n"
                else:
                    message += "✅ <b>No tienes tareas programadas para esta semana.</b>\n"

                message += "\n"

                # Estadísticas
                message += f"📊 <b>Estadísticas Generales:</b>\n"
                message += f"• Total de tareas: {total_tasks}\n"
                message += f"• Completadas: {total_completed} ({completion_rate:.1f}%)\n"

                if tasks_overdue > 0:
                    message += f"• ⚠️ Vencidas: {tasks_overdue}\n"

                message += "\n💡 Usa /semana para ver detalles de la semana actual."

                # Enviar notificación (ejecutar async de forma síncrona)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    success = loop.run_until_complete(
                        send_telegram_notification(user.id, message, db)
                    )
                finally:
                    loop.close()

                if success:
                    # Registrar en BD
                    notification = Notification(
                        user_id=user.id,
                        type='resumen_semanal',
                        message=f"Resumen semanal: {tasks_completed_last_week} completadas, {len(tasks_this_week)} para esta semana",
                        sent_at=now
                    )
                    db.add(notification)
                    db.commit()

                    summaries_sent += 1
                    logger.info(f"✅ Resumen semanal enviado a {user.email}")
                else:
                    errors += 1
                    logger.error(f"❌ Error al enviar resumen semanal a {user.email}")

            except Exception as e:
                errors += 1
                logger.error(f"Error procesando resumen semanal para usuario {user.id}: {str(e)}")
                continue

        summary = {
            'status': 'completed',
            'summaries_sent': summaries_sent,
            'errors': errors,
            'total_users': len(users_with_telegram),
            'timestamp': now.isoformat()
        }

        logger.info(
            f"✅ Resúmenes semanales completados: {summaries_sent} enviados, "
            f"{errors} errores, {len(users_with_telegram)} usuarios"
        )

        return summary

    except Exception as e:
        logger.error(f"❌ Error en send_weekly_summary: {str(e)}")
        raise
    finally:
        db.close()


# Ya no necesitamos el wrapper
