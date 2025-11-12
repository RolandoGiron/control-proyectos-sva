"""
Script para iniciar el bot de Telegram
"""
import asyncio
import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.bot.bot import TelegramBot
from app.core.config import settings

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main():
    """Función principal para ejecutar el bot"""
    logger.info("=" * 60)
    logger.info("Iniciando Sistema de Bot de Telegram")
    logger.info("=" * 60)

    # Verificar que el token esté configurado
    if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.error("❌ TELEGRAM_BOT_TOKEN no está configurado correctamente")
        logger.error("Por favor, configura el token en el archivo .env")
        return

    # Crear e iniciar el bot
    bot = TelegramBot()

    try:
        await bot.start()
        logger.info("✅ Bot iniciado correctamente")
        logger.info("Presiona Ctrl+C para detener el bot")

        # Mantener el bot ejecutándose
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("\n🛑 Deteniendo bot...")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        raise
    finally:
        await bot.stop()
        logger.info("✅ Bot detenido correctamente")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
