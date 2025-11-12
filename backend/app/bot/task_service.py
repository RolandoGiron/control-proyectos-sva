"""
Servicio de tareas para el bot de Telegram
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from app.core.database import get_db_context
from app.models.user import User
from app.models.area import Area  # Importar Area para evitar error de mapper
from app.models.task import Task, TaskStatus
from app.models.project import Project

logger = logging.getLogger(__name__)


class TaskService:
    """Servicio para gestionar tareas desde el bot de Telegram"""

    async def get_user_by_chat_id(self, chat_id: int) -> dict | None:
        """
        Obtener usuario por chat_id de Telegram

        Args:
            chat_id: ID del chat de Telegram

        Returns:
            dict con datos del usuario o None si no existe
        """
        try:
            with get_db_context() as db:
                user = db.query(User).filter(User.telegram_chat_id == chat_id).first()

                if not user:
                    return None

                return {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role
                }

        except Exception as e:
            logger.error(f"Error al obtener usuario por chat_id: {e}")
            return None

    async def get_user_tasks(self, user_id: str) -> list:
        """
        Obtener todas las tareas del usuario (no completadas)

        Args:
            user_id: ID del usuario

        Returns:
            Lista de tareas
        """
        try:
            with get_db_context() as db:
                tasks = db.query(Task).join(Project).filter(
                    Task.responsible_id == user_id,
                    Task.status != TaskStatus.COMPLETADO
                ).options(
                    joinedload(Task.project)
                ).order_by(
                    Task.deadline.asc().nullslast(),
                    Task.priority.desc()
                ).all()

                return self._format_tasks(tasks)

        except Exception as e:
            logger.error(f"Error al obtener tareas del usuario: {e}")
            return []

    async def get_today_tasks(self, user_id: str) -> list:
        """
        Obtener tareas con deadline para hoy

        Args:
            user_id: ID del usuario

        Returns:
            Lista de tareas
        """
        try:
            with get_db_context() as db:
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                today_end = today_start + timedelta(days=1)

                tasks = db.query(Task).join(Project).filter(
                    Task.responsible_id == user_id,
                    Task.deadline >= today_start,
                    Task.deadline < today_end,
                    Task.status != TaskStatus.COMPLETADO
                ).options(
                    joinedload(Task.project)
                ).order_by(Task.priority.desc()).all()

                return self._format_tasks(tasks)

        except Exception as e:
            logger.error(f"Error al obtener tareas de hoy: {e}")
            return []

    async def get_pending_tasks(self, user_id: str) -> list:
        """
        Obtener tareas sin empezar

        Args:
            user_id: ID del usuario

        Returns:
            Lista de tareas
        """
        try:
            with get_db_context() as db:
                tasks = db.query(Task).join(Project).filter(
                    Task.responsible_id == user_id,
                    Task.status == TaskStatus.SIN_EMPEZAR
                ).options(
                    joinedload(Task.project)
                ).order_by(
                    Task.deadline.asc().nullslast(),
                    Task.priority.desc()
                ).all()

                return self._format_tasks(tasks)

        except Exception as e:
            logger.error(f"Error al obtener tareas pendientes: {e}")
            return []

    async def get_week_tasks(self, user_id: str) -> list:
        """
        Obtener tareas con deadline esta semana

        Args:
            user_id: ID del usuario

        Returns:
            Lista de tareas
        """
        try:
            with get_db_context() as db:
                today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                week_end = today + timedelta(days=7)

                tasks = db.query(Task).join(Project).filter(
                    Task.responsible_id == user_id,
                    Task.deadline >= today,
                    Task.deadline < week_end,
                    Task.status != TaskStatus.COMPLETADO
                ).options(
                    joinedload(Task.project)
                ).order_by(Task.deadline.asc()).all()

                return self._format_tasks(tasks)

        except Exception as e:
            logger.error(f"Error al obtener tareas de la semana: {e}")
            return []

    async def complete_task(self, user_id: str, task_id: str) -> dict:
        """
        Marcar tarea como completada

        Args:
            user_id: ID del usuario
            task_id: ID de la tarea (puede ser ID completo o los primeros 8 caracteres)

        Returns:
            dict con success: bool, task_title: str (si success), error: str (si no success)
        """
        try:
            with get_db_context() as db:
                # Buscar tarea por ID completo o por los primeros 8 caracteres
                if len(task_id) == 8:
                    task = db.query(Task).filter(
                        Task.id.like(f"{task_id}%"),
                        Task.responsible_id == user_id
                    ).first()
                else:
                    task = db.query(Task).filter(
                        Task.id == task_id,
                        Task.responsible_id == user_id
                    ).first()

                if not task:
                    return {
                        'success': False,
                        'error': 'Tarea no encontrada o no eres el responsable.'
                    }

                if task.status == TaskStatus.COMPLETADO:
                    return {
                        'success': False,
                        'error': 'Esta tarea ya está completada.'
                    }

                # Completar tarea
                task.status = TaskStatus.COMPLETADO
                task.completed_at = datetime.utcnow()

                db.commit()

                logger.info(f"Tarea completada por bot: {task.id} por usuario {user_id}")

                return {
                    'success': True,
                    'task_title': task.title
                }

        except Exception as e:
            logger.error(f"Error al completar tarea: {e}")
            return {
                'success': False,
                'error': 'Error al completar la tarea. Intenta nuevamente.'
            }

    def _format_tasks(self, tasks: list) -> list:
        """
        Formatear tareas para el bot

        Args:
            tasks: Lista de objetos Task de SQLAlchemy

        Returns:
            Lista de diccionarios con datos formateados
        """
        formatted_tasks = []

        for task in tasks:
            # Formatear deadline
            deadline_display = None
            if task.deadline:
                deadline = task.deadline
                now = datetime.utcnow()
                days_until = (deadline - now).days

                if days_until < 0:
                    deadline_display = f"{deadline.strftime('%d/%m/%Y')} (Vencido)"
                elif days_until == 0:
                    deadline_display = f"{deadline.strftime('%d/%m/%Y')} (Hoy)"
                elif days_until == 1:
                    deadline_display = f"{deadline.strftime('%d/%m/%Y')} (Mañana)"
                else:
                    deadline_display = deadline.strftime('%d/%m/%Y')

            # Formatear estado
            status_display = {
                TaskStatus.SIN_EMPEZAR: 'Sin Empezar',
                TaskStatus.EN_CURSO: 'En Curso',
                TaskStatus.COMPLETADO: 'Completado'
            }.get(task.status, 'Sin Empezar')

            formatted_tasks.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status.value if hasattr(task.status, 'value') else task.status,
                'status_display': status_display,
                'priority': task.priority.value if hasattr(task.priority, 'value') else task.priority,
                'project_name': task.project.name if task.project else 'Sin proyecto',
                'deadline': task.deadline.isoformat() if task.deadline else None,
                'deadline_display': deadline_display
            })

        return formatted_tasks
