"""
Telegram Bot - Handlers de comandos
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from app.bot.link_service import LinkService
from app.bot.task_service import TaskService

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler del comando /start
    Permite vincular la cuenta de Telegram con la cuenta del sistema
    """
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "Usuario"

    # Si hay un código de vinculación en los argumentos
    if context.args:
        code = context.args[0].upper()
        link_service = LinkService()

        result = await link_service.verify_and_link(code, chat_id)

        if result['success']:
            await update.message.reply_text(
                f"✅ <b>Cuenta vinculada exitosamente!</b>\n\n"
                f"Hola {result['user_name']}, tu cuenta de Telegram ha sido vinculada correctamente.\n\n"
                f"Ahora recibirás notificaciones sobre:\n"
                f"• Nuevas tareas asignadas\n"
                f"• Cambios de estado en tus tareas\n"
                f"• Recordatorios de deadlines\n\n"
                f"Usa /help para ver todos los comandos disponibles.",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                f"❌ <b>Error al vincular cuenta</b>\n\n"
                f"{result['error']}\n\n"
                f"Por favor, genera un nuevo código desde tu perfil en la aplicación web.",
                parse_mode='HTML'
            )
    else:
        # Bienvenida sin código
        await update.message.reply_text(
            f"👋 <b>Bienvenido al Bot de Gestión de Proyectos SVA</b>\n\n"
            f"Para vincular tu cuenta, necesitas un código de vinculación.\n\n"
            f"<b>Pasos para vincular:</b>\n"
            f"1. Inicia sesión en la aplicación web\n"
            f"2. Ve a tu perfil\n"
            f"3. Genera un código de vinculación\n"
            f"4. Envía el comando: /start CODIGO\n\n"
            f"Usa /help para ver todos los comandos disponibles.",
            parse_mode='HTML'
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /help o /ayuda"""
    chat_id = update.effective_chat.id
    task_service = TaskService()

    # Verificar si el usuario está vinculado para personalizar la ayuda
    user = await task_service.get_user_by_chat_id(chat_id)
    is_admin = user and user.get('role') == 'administrador'

    help_text = "📋 <b>Comandos Disponibles</b>\n\n"
    help_text += "<b>/start CODIGO</b> - Vincular tu cuenta de Telegram\n"

    # Descripción personalizada según rol
    if is_admin:
        help_text += "<b>/tareas</b> - Ver próximas 15 tareas a vencer (todos los usuarios)\n"
        help_text += "<b>/pendientes</b> - Ver todas las tareas sin empezar (todos)\n"
        help_text += "<b>/vencidas</b> - Ver todas las tareas vencidas (todos)\n"
    else:
        help_text += "<b>/tareas</b> - Ver todas tus tareas asignadas\n"
        help_text += "<b>/pendientes</b> - Ver tus tareas sin empezar\n"
        help_text += "<b>/vencidas</b> - Ver tus tareas vencidas\n"

    help_text += "<b>/hoy</b> - Ver tareas con deadline para hoy\n"
    help_text += "<b>/semana</b> - Ver tareas de esta semana\n"
    help_text += "<b>/completar [ID]</b> - Marcar una tarea como completada\n"
    help_text += "<b>/ayuda</b> o <b>/help</b> - Mostrar esta ayuda\n\n"

    if is_admin:
        help_text += "👨‍💼 <b>Modo Administrador Activo</b>\n"
        help_text += "Tienes acceso a ver tareas de todos los usuarios.\n\n"

    help_text += "💡 <b>Tip:</b> Recibirás notificaciones automáticas cuando:\n"
    help_text += "• Te asignen una nueva tarea\n"
    help_text += "• Cambien el estado de tus tareas\n"
    help_text += "• Se complete una tarea en tus proyectos\n"
    help_text += "• Se acerque el deadline de una tarea"

    await update.message.reply_text(help_text, parse_mode='HTML')


async def tareas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler del comando /tareas
    - Usuario normal: Ver todas sus tareas asignadas (no completadas)
    - Administrador: Ver próximas 15 tareas a vencer de todos los usuarios
    """
    chat_id = update.effective_chat.id
    task_service = TaskService()

    # Verificar que el usuario esté vinculado
    user = await task_service.get_user_by_chat_id(chat_id)
    if not user:
        await update.message.reply_text(
            "❌ Tu cuenta no está vinculada.\n"
            "Usa /start CODIGO para vincular tu cuenta.",
            parse_mode='HTML'
        )
        return

    # Obtener tareas según rol
    tasks = await task_service.get_user_tasks(user['id'], user['role'])

    if not tasks:
        if user['role'] == 'administrador':
            await update.message.reply_text(
                "✅ No hay tareas próximas a vencer.",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                "✅ No tienes tareas pendientes.\n"
                "¡Buen trabajo!",
                parse_mode='HTML'
            )
        return

    # Formatear tareas
    if user['role'] == 'administrador':
        message = f"📋 <b>Próximas Tareas a Vencer ({len(tasks)})</b>\n\n"
    else:
        message = f"📋 <b>Tus Tareas ({len(tasks)})</b>\n\n"

    for task in tasks[:15]:  # Máximo 15 tareas
        status_emoji = {
            'sin_empezar': '⚪',
            'en_curso': '🔵',
            'completado': '✅'
        }.get(task['status'], '⚪')

        priority_emoji = {
            'baja': '🟢',
            'media': '🟡',
            'alta': '🔴'
        }.get(task['priority'], '🟡')

        message += (
            f"{status_emoji} {priority_emoji} <b>{task['title']}</b>\n"
            f"   Proyecto: {task['project_name']}\n"
        )

        # Si es admin, mostrar responsable
        if user['role'] == 'administrador' and task.get('responsible_name'):
            message += f"   👤 Responsable: {task['responsible_name']}\n"

        message += f"   Estado: {task['status_display']}\n"

        if task.get('deadline'):
            message += f"   📅 Deadline: {task['deadline_display']}\n"

        message += f"   ID: <code>{task['id'][:8]}</code>\n\n"

    if len(tasks) > 15:
        message += f"\n... y {len(tasks) - 15} tareas más."

    await update.message.reply_text(message, parse_mode='HTML')


async def completar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /completar [ID] - Marcar tarea como completada"""
    chat_id = update.effective_chat.id
    task_service = TaskService()

    # Verificar que el usuario esté vinculado
    user = await task_service.get_user_by_chat_id(chat_id)
    if not user:
        await update.message.reply_text(
            "❌ Tu cuenta no está vinculada.\n"
            "Usa /start CODIGO para vincular tu cuenta."
        )
        return

    # Verificar que se proporcionó un ID
    if not context.args:
        await update.message.reply_text(
            "❌ Debes proporcionar el ID de la tarea.\n\n"
            "Uso: /completar ID\n"
            "Ejemplo: /completar 12345678"
        )
        return

    task_id = context.args[0]

    # Intentar completar la tarea
    result = await task_service.complete_task(user['id'], task_id)

    if result['success']:
        await update.message.reply_text(
            f"✅ <b>Tarea completada!</b>\n\n"
            f"{result['task_title']}\n\n"
            f"¡Excelente trabajo!",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            f"❌ {result['error']}",
            parse_mode='HTML'
        )


async def hoy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /hoy - Ver tareas con deadline hoy"""
    chat_id = update.effective_chat.id
    task_service = TaskService()

    # Verificar que el usuario esté vinculado
    user = await task_service.get_user_by_chat_id(chat_id)
    if not user:
        await update.message.reply_text(
            "❌ Tu cuenta no está vinculada.\n"
            "Usa /start CODIGO para vincular tu cuenta."
        )
        return

    # Obtener tareas de hoy
    tasks = await task_service.get_today_tasks(user['id'])

    if not tasks:
        await update.message.reply_text(
            "✅ No tienes tareas con deadline para hoy.\n"
            "¡Disfruta tu día!",
            parse_mode='HTML'
        )
        return

    # Formatear tareas
    message = f"📅 <b>Tareas para Hoy ({len(tasks)})</b>\n\n"

    for task in tasks:
        status_emoji = {
            'sin_empezar': '⚪',
            'en_curso': '🔵',
            'completado': '✅'
        }.get(task['status'], '⚪')

        priority_emoji = {
            'baja': '🟢',
            'media': '🟡',
            'alta': '🔴'
        }.get(task['priority'], '🟡')

        message += (
            f"{status_emoji} {priority_emoji} <b>{task['title']}</b>\n"
            f"   Proyecto: {task['project_name']}\n"
            f"   ID: <code>{task['id'][:8]}</code>\n\n"
        )

    await update.message.reply_text(message, parse_mode='HTML')


async def pendientes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler del comando /pendientes - Ver tareas sin empezar
    - Usuario normal: Sus tareas sin empezar
    - Administrador: Todas las tareas sin empezar de todos los usuarios
    """
    chat_id = update.effective_chat.id
    task_service = TaskService()

    # Verificar que el usuario esté vinculado
    user = await task_service.get_user_by_chat_id(chat_id)
    if not user:
        await update.message.reply_text(
            "❌ Tu cuenta no está vinculada.\n"
            "Usa /start CODIGO para vincular tu cuenta."
        )
        return

    # Obtener tareas pendientes según rol
    tasks = await task_service.get_pending_tasks(user['id'], user['role'])

    if not tasks:
        if user['role'] == 'administrador':
            await update.message.reply_text(
                "✅ No hay tareas sin empezar en el sistema.",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                "✅ No tienes tareas pendientes sin empezar.",
                parse_mode='HTML'
            )
        return

    # Formatear tareas
    if user['role'] == 'administrador':
        message = f"⚪ <b>Tareas Sin Empezar - Todos ({len(tasks)})</b>\n\n"
    else:
        message = f"⚪ <b>Tareas Sin Empezar ({len(tasks)})</b>\n\n"

    for task in tasks[:15]:  # Máximo 15 tareas
        priority_emoji = {
            'baja': '🟢',
            'media': '🟡',
            'alta': '🔴'
        }.get(task['priority'], '🟡')

        message += (
            f"{priority_emoji} <b>{task['title']}</b>\n"
            f"   Proyecto: {task['project_name']}\n"
        )

        # Si es admin, mostrar responsable
        if user['role'] == 'administrador' and task.get('responsible_name'):
            message += f"   👤 Responsable: {task['responsible_name']}\n"

        if task.get('deadline'):
            message += f"   📅 Deadline: {task['deadline_display']}\n"

        message += f"   ID: <code>{task['id'][:8]}</code>\n\n"

    if len(tasks) > 15:
        message += f"\n... y {len(tasks) - 15} tareas más."

    await update.message.reply_text(message, parse_mode='HTML')


async def semana_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /semana - Ver tareas de esta semana"""
    chat_id = update.effective_chat.id
    task_service = TaskService()

    # Verificar que el usuario esté vinculado
    user = await task_service.get_user_by_chat_id(chat_id)
    if not user:
        await update.message.reply_text(
            "❌ Tu cuenta no está vinculada.\n"
            "Usa /start CODIGO para vincular tu cuenta."
        )
        return

    # Obtener tareas de la semana
    tasks = await task_service.get_week_tasks(user['id'])

    if not tasks:
        await update.message.reply_text(
            "✅ No tienes tareas con deadline esta semana.",
            parse_mode='HTML'
        )
        return

    # Formatear tareas
    message = f"📅 <b>Tareas de Esta Semana ({len(tasks)})</b>\n\n"

    for task in tasks[:10]:
        status_emoji = {
            'sin_empezar': '⚪',
            'en_curso': '🔵',
            'completado': '✅'
        }.get(task['status'], '⚪')

        priority_emoji = {
            'baja': '🟢',
            'media': '🟡',
            'alta': '🔴'
        }.get(task['priority'], '🟡')

        message += (
            f"{status_emoji} {priority_emoji} <b>{task['title']}</b>\n"
            f"   Proyecto: {task['project_name']}\n"
            f"   📅 {task['deadline_display']}\n"
            f"   ID: <code>{task['id'][:8]}</code>\n\n"
        )

    if len(tasks) > 10:
        message += f"\n... y {len(tasks) - 10} tareas más."

    await update.message.reply_text(message, parse_mode='HTML')


async def vencidas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler del comando /vencidas - Ver tareas vencidas
    - Usuario normal: Sus tareas vencidas
    - Administrador: Todas las tareas vencidas de todos los usuarios
    """
    chat_id = update.effective_chat.id
    task_service = TaskService()

    # Verificar que el usuario esté vinculado
    user = await task_service.get_user_by_chat_id(chat_id)
    if not user:
        await update.message.reply_text(
            "❌ Tu cuenta no está vinculada.\n"
            "Usa /start CODIGO para vincular tu cuenta."
        )
        return

    # Obtener tareas vencidas según rol
    tasks = await task_service.get_overdue_tasks(user['id'], user['role'])

    if not tasks:
        if user['role'] == 'administrador':
            await update.message.reply_text(
                "✅ No hay tareas vencidas en el sistema.\n"
                "¡Excelente trabajo del equipo!",
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                "✅ No tienes tareas vencidas.\n"
                "¡Excelente trabajo!",
                parse_mode='HTML'
            )
        return

    # Formatear tareas
    if user['role'] == 'administrador':
        message = f"⚠️ <b>Tareas Vencidas - Todos ({len(tasks)})</b>\n\n"
    else:
        message = f"⚠️ <b>Tareas Vencidas ({len(tasks)})</b>\n\n"

    for task in tasks[:15]:  # Máximo 15 tareas
        status_emoji = {
            'sin_empezar': '⚪',
            'en_curso': '🔵',
            'completado': '✅'
        }.get(task['status'], '⚪')

        priority_emoji = {
            'baja': '🟢',
            'media': '🟡',
            'alta': '🔴'
        }.get(task['priority'], '🟡')

        message += (
            f"{status_emoji} {priority_emoji} <b>{task['title']}</b>\n"
            f"   Proyecto: {task['project_name']}\n"
        )

        # Si es admin, mostrar responsable
        if user['role'] == 'administrador' and task.get('responsible_name'):
            message += f"   👤 Responsable: {task['responsible_name']}\n"

        message += f"   Estado: {task['status_display']}\n"

        if task.get('deadline'):
            message += f"   📅 Deadline: {task['deadline_display']}\n"

        message += f"   ID: <code>{task['id'][:8]}</code>\n\n"

    if len(tasks) > 15:
        message += f"\n... y {len(tasks) - 15} tareas más."

    await update.message.reply_text(message, parse_mode='HTML')


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para comandos desconocidos"""
    await update.message.reply_text(
        "❌ Comando no reconocido.\n\n"
        "Usa /help para ver los comandos disponibles."
    )
