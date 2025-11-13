"""
Script de inicialización de la base de datos

Este script:
1. Espera a que MySQL esté disponible
2. Ejecuta las migraciones de Alembic
3. Crea datos iniciales si es necesario
"""
import time
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from alembic.config import Config
from alembic import command

from app.core.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def wait_for_db(max_retries: int = 30, retry_interval: int = 2) -> bool:
    """
    Espera a que la base de datos esté disponible.

    Args:
        max_retries: Número máximo de intentos
        retry_interval: Segundos entre intentos

    Returns:
        True si la DB está disponible, False si se agotaron los intentos
    """
    logger.info("Esperando a que MySQL esté disponible...")

    engine = create_engine(settings.database_url)

    for attempt in range(1, max_retries + 1):
        try:
            # Intentar conectar
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"✓ MySQL está disponible (intento {attempt}/{max_retries})")
            return True
        except OperationalError as e:
            logger.warning(
                f"✗ MySQL no disponible (intento {attempt}/{max_retries}): {e}"
            )
            if attempt < max_retries:
                time.sleep(retry_interval)

    logger.error("✗ No se pudo conectar a MySQL después de todos los intentos")
    return False


def run_migrations() -> bool:
    """
    Ejecuta las migraciones de Alembic.

    Returns:
        True si las migraciones se ejecutaron correctamente
    """
    try:
        logger.info("Ejecutando migraciones de Alembic...")

        # Configurar Alembic
        alembic_cfg = Config("alembic.ini")

        # Ejecutar migraciones
        command.upgrade(alembic_cfg, "head")

        logger.info("✓ Migraciones ejecutadas correctamente")
        return True
    except Exception as e:
        logger.error(f"✗ Error al ejecutar migraciones: {e}")
        return False


def create_initial_data():
    """
    Crea datos iniciales en la base de datos si es necesario.

    Por ahora solo verifica que las tablas existan.
    En el futuro se pueden agregar áreas por defecto, usuarios admin, etc.
    """
    try:
        logger.info("Verificando datos iniciales...")

        engine = create_engine(settings.database_url)

        with engine.connect() as conn:
            # Verificar que las tablas existan
            result = conn.execute(text(
                "SELECT COUNT(*) as count FROM information_schema.tables "
                "WHERE table_schema = :db_name AND table_name = 'areas'"
            ), {"db_name": settings.MYSQL_DATABASE})

            count = result.scalar()

            if count > 0:
                logger.info("✓ Tabla 'areas' existe")
            else:
                logger.warning("✗ Tabla 'areas' no existe")
                return False

        # Aquí se pueden agregar datos iniciales si se requiere:
        # - Áreas por defecto
        # - Usuario administrador
        # - Configuraciones del sistema

        logger.info("✓ Base de datos inicializada correctamente")
        return True

    except Exception as e:
        logger.error(f"✗ Error al verificar/crear datos iniciales: {e}")
        return False


def main():
    """Función principal de inicialización"""
    logger.info("=" * 60)
    logger.info("INICIALIZANDO BASE DE DATOS")
    logger.info("=" * 60)

    # 1. Esperar a que MySQL esté disponible
    if not wait_for_db():
        logger.error("No se pudo conectar a MySQL. Abortando.")
        sys.exit(1)

    # 2. Ejecutar migraciones
    if not run_migrations():
        logger.error("Error al ejecutar migraciones. Abortando.")
        sys.exit(1)

    # 3. Crear datos iniciales
    if not create_initial_data():
        logger.warning("Advertencia: No se pudieron verificar/crear datos iniciales")
        # No abortamos aquí, solo es una advertencia

    logger.info("=" * 60)
    logger.info("✓ INICIALIZACIÓN COMPLETADA")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
