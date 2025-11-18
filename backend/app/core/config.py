"""
Configuración central de la aplicación
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno"""

    # Información de la aplicación
    APP_NAME: str = "Sistema de Gestión de Proyectos SVA"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Base de datos MySQL
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "sva_user"
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str = "proyectos_sva_db"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # JWT y Seguridad
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: Optional[str] = None  # Para producción

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # CORS - Permitir todos los orígenes en desarrollo
    # En producción, especificar solo los dominios permitidos
    CORS_ORIGINS: list[str] = ["*"]  # Permitir todos los orígenes

    # Configuración de recordatorios
    DEFAULT_REMINDER_HOURS: int = 24

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def build_celery_broker(cls, v: Optional[str], info) -> str:
        if v:
            return v
        # Construir desde Redis config
        redis_password = info.data.get("REDIS_PASSWORD")
        redis_host = info.data.get("REDIS_HOST", "redis")
        redis_port = info.data.get("REDIS_PORT", 6379)

        if redis_password:
            return f"redis://:{redis_password}@{redis_host}:{redis_port}/1"
        return f"redis://{redis_host}:{redis_port}/1"

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def build_celery_backend(cls, v: Optional[str], info) -> str:
        if v:
            return v
        # Usar mismo Redis con diferente DB
        redis_password = info.data.get("REDIS_PASSWORD")
        redis_host = info.data.get("REDIS_HOST", "redis")
        redis_port = info.data.get("REDIS_PORT", 6379)

        if redis_password:
            return f"redis://:{redis_password}@{redis_host}:{redis_port}/2"
        return f"redis://{redis_host}:{redis_port}/2"

    @property
    def database_url(self) -> str:
        """Construir URL de conexión a MySQL"""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )

    @property
    def redis_url(self) -> str:
        """Construir URL de conexión a Redis"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()
