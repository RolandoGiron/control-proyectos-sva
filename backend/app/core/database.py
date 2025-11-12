"""
Configuración de la base de datos y sesiones SQLAlchemy
"""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# Engine de SQLAlchemy
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verificar conexión antes de usar
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,  # Log SQL queries en modo debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos.
    Se usa en endpoints de FastAPI.

    Yields:
        Session: Sesión de SQLAlchemy

    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager para obtener sesión de base de datos.
    Se usa en servicios y workers fuera de FastAPI.

    Yields:
        Session: Sesión de SQLAlchemy

    Example:
        with get_db_context() as db:
            users = db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
