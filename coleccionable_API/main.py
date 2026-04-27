from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Any
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

app = FastAPI(title="Sistema de Gestión de Inventario - Coleccionables")

# Configuración de MongoDB (Usaremos una variable para la URI más adelante)
MONGO_URL = "mongodb+srv://Maxisotooh:Facundo.2017@cluster0.bnt1q8w.mongodb.net/?appName=Cluster0" # Por ahora local, luego será Atlas
client = AsyncIOMotorClient(MONGO_URL)
db = client.tienda_coleccionables

# Modelos (Attribute Pattern) [cite: 118]
class AtributoEspecifico(BaseModel):
    k: str
    v: Any

class Producto(BaseModel):
    sku: str
    nombre: str
    categoria: str
    precio_clp: int
    stock_actual: int
    atributos_especificos: List[AtributoEspecifico]

# Endpoint para CREAR un producto (POST) [cite: 165]
@app.post("/productos", status_code=201)
async def crear_producto(producto: Producto):
    # Convertimos el modelo de Pydantic a diccionario para MongoDB [cite: 160]
    nuevo_prod = producto.dict()
    
    # Verificamos si el SKU ya existe (Índice Único) [cite: 155]
    existe = await db.productos.find_one({"sku": producto.sku})
    if existe:
        raise HTTPException(status_code=409, detail="El SKU ya existe")
    
    result = await db.productos.insert_one(nuevo_prod)
    return {"mensaje": "Producto creado", "id": str(result.inserted_id)}

# Endpoint para BUSCAR por atributo (GET) - DEBE IR PRIMERO para evitar conflicto con {sku}
@app.get("/productos/buscar/atributo", tags=["Consultas"])
async def buscar_por_atributo(clave: str, valor: str):
    """Busca productos por atributo específico usando $elemMatch"""
    query = {"atributos_especificos": {"$elemMatch": {"k": clave, "v": valor}}}
    cursor = db.productos.find(query, {"_id": 0})
    resultados = await cursor.to_list(length=50)
    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron productos con ese atributo")
    return resultados


# Endpoint para ELIMINAR un producto (DELETE) - ANTES de {sku} para evitar conflicto
@app.delete("/productos/{sku}", tags=["Administración"], status_code=200)
async def eliminar_producto(sku: str):
    """Elimina un producto del inventario por su SKU"""
    resultado = await db.productos.delete_one({"sku": sku})
    
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado para eliminar")
    
    return {"mensaje": f"Producto con SKU {sku} eliminado exitosamente"}


# Endpoint para CONSULTAR stock por SKU (GET) [cite: 160]
@app.get("/productos/{sku}", tags=["Consultas"])
async def obtener_producto_por_sku(sku: str):
    """Obtiene un producto específico por su SKU"""
    producto = await db.productos.find_one({"sku": sku}, {"_id": 0})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


# Endpoint para actualizar stock o precio (PUT)
@app.put("/productos/{sku}", tags=["Administración"])
async def actualizar_producto(sku: str, stock_nuevo: int | None = None, precio_nuevo: int | None = None):
    """Actualiza el stock y/o precio de un producto existente"""
    # Preparamos los campos a actualizar
    campos_update = {}
    if stock_nuevo is not None:
        campos_update["stock_actual"] = stock_nuevo
    if precio_nuevo is not None:
        campos_update["precio_clp"] = precio_nuevo
    
    if not campos_update:
        raise HTTPException(status_code=400, detail="Debes proporcionar al menos un campo para actualizar")
    
    # Añadimos la fecha de actualización automática
    campos_update["ultima_actualizacion"] = datetime.utcnow()

    # Ejecutamos la actualización en MongoDB
    resultado = await db.productos.update_one(
        {"sku": sku}, 
        {"$set": campos_update}
    )

    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return {"mensaje": "Producto actualizado correctamente"}