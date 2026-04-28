import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from coleccionable_API.config import Settings, get_settings

logger = logging.getLogger(__name__)

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

MONGO_OPTIONS: dict = {
    "serverSelectionTimeoutMS": 15_000,
    "socketTimeoutMS": 15_000,
    "connectTimeoutMS": 15_000,
    "retryWrites": True,
    "w": "majority",
    "maxPoolSize": 10,
    "minPoolSize": 2,
}


def get_mongo_db() -> Optional[AsyncIOMotorDatabase]:
    return _db


def get_db_required() -> AsyncIOMotorDatabase:
    if _db is None:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no disponible. Intente más tarde.",
        )
    return _db


def _get_app_settings() -> Settings:
    return get_settings()


def _mongo_uri_valid(uri: str) -> bool:
    return uri.startswith(("mongodb://", "mongodb+srv://"))


async def connect_mongo() -> None:
    global _client, _db
    settings = _get_app_settings()
    uri = (settings.mongodb_uri or "").strip()
    if not uri:
        logger.warning(
            "MONGODB_URI no definida: la app arranca sin conexión a base de datos."
        )
        return
    if not _mongo_uri_valid(uri):
        logger.error(
            "MONGODB_URI inválida: debe empezar con mongodb:// o mongodb+srv:// "
            "(revisa comillas, espacios o nombre de variable en .env)."
        )
        return
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Conectando a MongoDB (intento %s/%s)", attempt, max_retries)
            _client = AsyncIOMotorClient(uri, **MONGO_OPTIONS)
            await _client.admin.command("ismaster", timeoutMS=15_000)
            _db = _client[settings.mongodb_db_name]
            logger.info("Conectado a MongoDB, base: %s", settings.mongodb_db_name)
            return
        except asyncio.CancelledError:
            if _client is not None:
                _client.close()
            _client = None
            _db = None
            raise
        except Exception as e:
            logger.warning("Conexión MongoDB falló: %s", e)
            if _client is not None:
                _client.close()
                _client = None
                _db = None
            if attempt < max_retries:
                wait = 3 + attempt
                logger.info("Reintentando en %ss", wait)
                with contextlib.suppress(asyncio.CancelledError):
                    await asyncio.sleep(wait)
            else:
                logger.error(
                    "No se pudo conectar a MongoDB tras %s intentos. "
                    "Revisa IP allowlist en Atlas, URI y red.",
                    max_retries,
                )


async def close_mongo() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
        logger.info("Conexión MongoDB cerrada")
    _client = None
    _db = None


@asynccontextmanager
async def lifespan_mongo(_app: FastAPI):
    """Arranca el HTTP de inmediato; Mongo conecta en segundo plano."""
    task: asyncio.Task[None] = asyncio.create_task(connect_mongo(), name="mongo_connect")
    try:
        yield
    finally:
        if not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        await close_mongo()
