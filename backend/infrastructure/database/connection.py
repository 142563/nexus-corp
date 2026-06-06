# infrastructure/database/connection.py
# Configura la conexión a PostgreSQL (Neon / local) con SQLAlchemy.
# Maneja automáticamente parámetros SSL de Neon como sslmode y channel_binding.
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

_RAW_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://nexus:nexus2026@localhost:5432/nexuscorp"
)


def _prepare_db_url(url: str) -> tuple[str, dict]:
    """
    Extrae sslmode de la URL y lo pasa como connect_args.
    Elimina channel_binding que no es soportado por todas las versiones de psycopg2 vía URL.
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)

    connect_args = {}
    if "sslmode" in params:
        connect_args["sslmode"] = params.pop("sslmode")[0]

    # channel_binding solo funciona en psycopg2 >= 3.x — se descarta para compatibilidad
    params.pop("channel_binding", None)

    new_query = urlencode({k: v[0] for k, v in params.items()})
    clean_parsed = parsed._replace(query=new_query)
    return urlunparse(clean_parsed), connect_args


DATABASE_URL, _CONNECT_ARGS = _prepare_db_url(_RAW_URL)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args=_CONNECT_ARGS,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
