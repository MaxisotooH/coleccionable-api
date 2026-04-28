import os
from typing import Any, Dict, Union

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from coleccionable_API.config import get_settings
from coleccionable_API.database import get_mongo_db

router = APIRouter()
_static_dir = os.path.join(os.path.dirname(__file__), "..", "static")


@router.get("/")
async def root() -> Dict[str, str]:
    return {
        "status": "online",
        "api": "Sistema de Gestión de Inventario - Coleccionables",
        "dashboard": "/dashboard",
        "docs": "/docs",
        "version": "1.0.0",
    }


@router.get("/diagnostico", tags=["Sistema"])
async def diagnostico() -> Dict[str, Union[str, int]]:
    """Diagnóstico de conexión a MongoDB (sin detalles sensibles)."""
    settings = get_settings()
    db = get_mongo_db()
    if db is None:
        return {"status": "DB no conectada", "database": settings.mongodb_db_name, "connection": "inactiva"}
    try:
        count = await db.productos.count_documents({})
        return {
            "status": "MongoDB conectada",
            "database": settings.mongodb_db_name,
            "productos_en_bd": count,
            "connection": "activa",
        }
    except Exception as e:  # noqa: BLE001 — diagnóstico debe explicar fallo al usuario admin
        return {
            "status": "Error al consultar",
            "database": settings.mongodb_db_name,
            "error": str(e)[:200],
        }


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False, tags=["Sistema"])
def get_dashboard() -> str:
    path = os.path.join(_static_dir, "index.html")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        raise HTTPException(
            status_code=500, detail="No se pudo cargar el dashboard"
        ) from e
