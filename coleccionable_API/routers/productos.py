import asyncio
import logging
from datetime import datetime, timezone
from typing import Annotated, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from coleccionable_API.database import get_db_required
from coleccionable_API.models import Producto

router = APIRouter()
logger = logging.getLogger(__name__)

Db = Annotated[AsyncIOMotorDatabase, Depends(get_db_required)]


@router.get("/productos", tags=["Consultas"])
async def listar_productos(db: Db, limit: int = 100) -> List[dict[str, Any]]:
    """Lista hasta 100 productos (más recientes primero)."""
    try:
        cur = db.productos.find().sort("_id", -1).limit(limit)
        productos = await cur.to_list(length=limit)
        return [
            {
                "sku": p.get("sku"),
                "nombre": p.get("nombre"),
                "categoria": p.get("categoria"),
                "precio_clp": p.get("precio_clp"),
                "stock_actual": p.get("stock_actual"),
                "atributos_especificos": p.get("atributos_especificos", []),
            }
            for p in productos
        ]
    except Exception as e:  # noqa: BLE001
        logger.exception("listar_productos: %s", e)
        raise HTTPException(status_code=500, detail="Error al listar productos") from e


@router.post("/productos", status_code=201, tags=["Administración"])
async def crear_producto(db: Db, producto: Producto) -> dict[str, str]:
    max_reintentos = 2
    for intento in range(1, max_reintentos + 1):
        try:
            existe = await db.productos.find_one({"sku": producto.sku})
            if existe:
                raise HTTPException(status_code=409, detail="El SKU ya existe")
            nuevo = producto.model_dump()
            nuevo["fecha_creacion"] = datetime.now(timezone.utc).isoformat()
            result = await db.productos.insert_one(nuevo)
            return {
                "mensaje": "Producto creado exitosamente",
                "id": str(result.inserted_id),
            }
        except HTTPException:
            raise
        except Exception as e:  # noqa: BLE001
            if intento < max_reintentos:
                await asyncio.sleep(2)
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Error al crear el producto",
                ) from e
    raise HTTPException(status_code=500, detail="Error al crear el producto")


@router.get("/productos/buscar/atributo", tags=["Consultas"])
async def buscar_por_atributo(
    db: Db,
    clave: str,
    valor: str,
) -> List[dict[str, Any]]:
    query = {"atributos_especificos": {"$elemMatch": {"k": clave, "v": valor}}}
    cur = db.productos.find(query, {"_id": 0})
    resultados = await cur.to_list(length=50)
    if not resultados:
        raise HTTPException(
            status_code=404, detail="No se encontraron productos con ese atributo"
        )
    return resultados


@router.get("/productos/{sku}", tags=["Consultas"])
async def obtener_producto_por_sku(db: Db, sku: str) -> dict[str, Any]:
    producto = await db.productos.find_one({"sku": sku}, {"_id": 0})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.put("/productos/{sku}", tags=["Administración"])
async def actualizar_producto(
    db: Db,
    sku: str,
    stock_nuevo: Optional[int] = None,
    precio_nuevo: Optional[int] = None,
) -> dict[str, str]:
    update: dict[str, Any] = {}
    if stock_nuevo is not None:
        update["stock_actual"] = stock_nuevo
    if precio_nuevo is not None:
        update["precio_clp"] = precio_nuevo
    if not update:
        raise HTTPException(
            status_code=400, detail="Debes proporcionar al menos un campo para actualizar"
        )
    update["ultima_actualizacion"] = datetime.now(timezone.utc).isoformat()
    out = await db.productos.update_one({"sku": sku}, {"$set": update})
    if out.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto actualizado correctamente"}


@router.delete("/productos/{sku}", tags=["Administración"], status_code=200)
async def eliminar_producto(db: Db, sku: str) -> dict[str, str]:
    r = await db.productos.delete_one({"sku": sku})
    if r.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado para eliminar")
    return {"mensaje": f"Producto con SKU {sku} eliminado exitosamente"}
