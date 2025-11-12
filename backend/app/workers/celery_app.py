"""
Configuración de Celery con Redis como broker y backend
"""
import os
from celery import Celery
from celery.schedules import crontab

# Obtener URL de Redis desde variables de entorno
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

# Crear instancia de Celery
celery_app = Celery(
    'control_proyectos_sva',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'app.workers.reminder_tasks',
        'app.workers.summary_tasks'
    ]
)

# Configuración de Celery
celery_app.conf.update(
    # Zona horaria (Centro América - UTC-6)
    timezone='America/Guatemala',
    enable_utc=True,

    # Formato de serialización
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Resultados
    result_expires=3600,  # 1 hora
    result_backend_transport_options={'master_name': 'mymaster'},

    # Workers
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,

    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s',

    # Beat schedule (tareas programadas)
    beat_schedule={
        # Verificar recordatorios cada hora
        'check-upcoming-deadlines': {
            'task': 'app.workers.reminder_tasks.check_upcoming_deadlines',
            'schedule': crontab(minute=0),  # Cada hora en punto
        },

        # Resumen diario a las 8:00 AM (hora local Guatemala)
        'send-daily-summary': {
            'task': 'app.workers.summary_tasks.send_daily_summary',
            'schedule': crontab(hour=8, minute=0),  # 8:00 AM
        },

        # Resumen semanal los lunes a las 9:00 AM
        'send-weekly-summary': {
            'task': 'app.workers.summary_tasks.send_weekly_summary',
            'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Lunes 9:00 AM
        },
    },
)

# Auto-descubrir tareas en los módulos especificados
celery_app.autodiscover_tasks(['app.workers'])

if __name__ == '__main__':
    celery_app.start()
