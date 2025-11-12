"""
Telegram Bot - Clase principal
"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from app.core.config import settings
from app.bot.handlers import (
    start_command,
    help_command,
    tareas_command,
    completar_command,
    hoy_command,
    pendientes_command,
    semana_command,
    unknown_command,
)

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Bot de Telegram para el sistema de proyectos"""

    def __init__(self):
        """Inicializar el bot"""
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.application = None
        logger.info("Inicializando bot de Telegram...")

    def setup_handlers(self):
        """Configurar los manejadores de comandos"""
        logger.info("Configurando handlers del bot...")

        # Comandos
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("ayuda", help_command))
        self.application.add_handler(CommandHandler("tareas", tareas_command))
        self.application.add_handler(CommandHandler("completar", completar_command))
        self.application.add_handler(CommandHandler("hoy", hoy_command))
        self.application.add_handler(CommandHandler("pendientes", pendientes_command))
        self.application.add_handler(CommandHandler("semana", semana_command))

        # Handler para comandos desconocidos (debe ir al final)
        self.application.add_handler(MessageHandler(
            filters.COMMAND,
            unknown_command
        ))

        logger.info("Handlers configurados correctamente")

    async def start(self):
        """Iniciar el bot"""
        try:
            logger.info("Iniciando bot de Telegram...")

            # Crear aplicación
            self.application = Application.builder().token(self.token).build()

            # Configurar handlers
            self.setup_handlers()

            # Inicializar y ejecutar
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )

            logger.info("Bot de Telegram iniciado correctamente")
            logger.info(f"Bot username: @{(await self.application.bot.get_me()).username}")

        except Exception as e:
            logger.error(f"Error al iniciar el bot: {e}")
            raise

    async def stop(self):
        """Detener el bot"""
        try:
            logger.info("Deteniendo bot de Telegram...")

            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()

            logger.info("Bot detenido correctamente")

        except Exception as e:
            logger.error(f"Error al detener el bot: {e}")
            raise

    async def send_message(self, chat_id: int, text: str, parse_mode: str = 'HTML'):
        """
        Enviar mensaje a un chat

        Args:
            chat_id: ID del chat de Telegram
            text: Texto del mensaje
            parse_mode: Formato del mensaje (HTML o Markdown)
        """
        try:
            if not self.application:
                logger.warning("Aplicación no inicializada, no se puede enviar mensaje")
                return False

            await self.application.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode
            )
            logger.info(f"Mensaje enviado a chat_id: {chat_id}")
            return True

        except Exception as e:
            logger.error(f"Error al enviar mensaje a {chat_id}: {e}")
            return False
