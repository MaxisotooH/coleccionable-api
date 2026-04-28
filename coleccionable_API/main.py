from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Sistema de Gestión de Inventario - Coleccionables")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta de archivos estáticos
static_dir = os.path.join(os.path.dirname(__file__), "static")

# Configuración de MongoDB desde variables de entorno
MONGO_URL = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://Maxisotooh:Facundo.2017@cluster0.bnt1q8w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tls=true&authSource=admin"
)
DB_NAME = os.getenv("MONGODB_DB_NAME", "tienda_coleccionables")
client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None

@app.on_event("startup")
async def startup_db_client():
    """Conectar a MongoDB al iniciar con reintentos"""
    global client, db
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"🔄 Intento de conexión a MongoDB... ({retry_count + 1}/{max_retries})")
            client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=10000)
            # Verificar conexión
            await client.admin.command('ismaster')
            db = client[DB_NAME]
            print("✅ Conectado a MongoDB Atlas exitosamente")
            return
        except Exception as e:
            retry_count += 1
            print(f"⚠️ Intento {retry_count} falló: {e}")
            if retry_count < max_retries:
                import asyncio
                await asyncio.sleep(2)
            else:
                print(f"❌ No se pudo conectar a MongoDB después de {max_retries} intentos")
                print("⚠️ La aplicación se iniciará sin base de datos.")
                return

@app.on_event("shutdown")
async def shutdown_db_client():
    """Cerrar conexión a MongoDB"""
    global client
    if client:
        client.close()
        print("❌ Desconectado de MongoDB")

# Modelos
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

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "status": "online",
        "api": "Sistema de Gestión de Inventario - Coleccionables",
        "dashboard": "/dashboard",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Sirve el dashboard HTML"""
    try:
        with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sirviendo dashboard: {str(e)}")

# Montar archivos estáticos
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# LISTAR productos
@app.get("/productos", tags=["Consultas"])
async def listar_productos(limit: int = 100):
    """Lista hasta 100 productos recientemente agregados"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Base de datos no disponible")
        
        cursor = db.productos.find().sort("_id", -1).limit(limit)
        productos = await cursor.to_list(length=limit)
        
        return [{"sku": p.get("sku"), "nombre": p.get("nombre"), "categoria": p.get("categoria"), 
                 "precio_clp": p.get("precio_clp"), "stock_actual": p.get("stock_actual"),
                 "atributos_especificos": p.get("atributos_especificos", [])} for p in productos]
    except Exception as e:
        print(f"Error en listar_productos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# CREAR producto
@app.post("/productos", status_code=201)
async def crear_producto(producto: Producto):
    """Crea un nuevo producto"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Base de datos no disponible")
        
        # Verificar si el SKU ya existe
        existe = await db.productos.find_one({"sku": producto.sku})
        if existe:
            raise HTTPException(status_code=409, detail="El SKU ya existe")
        
        nuevo_prod = producto.dict()
        nuevo_prod["fecha_creacion"] = datetime.utcnow().isoformat()
        
        result = await db.productos.insert_one(nuevo_prod)
        return {"mensaje": "Producto creado exitosamente", "id": str(result.inserted_id)}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en crear_producto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# BUSCAR por atributo
@app.get("/productos/buscar/atributo", tags=["Consultas"])
async def buscar_por_atributo(clave: str, valor: str):
    """Busca productos por atributo específico"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Base de datos no disponible")
        
        query = {"atributos_especificos": {"$elemMatch": {"k": clave, "v": valor}}}
        cursor = db.productos.find(query, {"_id": 0})
        resultados = await cursor.to_list(length=50)
        
        if not resultados:
            raise HTTPException(status_code=404, detail="No se encontraron productos con ese atributo")
        
        return resultados
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en buscar_por_atributo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# OBTENER producto por SKU
@app.get("/productos/{sku}", tags=["Consultas"])
async def obtener_producto_por_sku(sku: str):
    """Obtiene un producto específico por su SKU"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Base de datos no disponible")
        
        producto = await db.productos.find_one({"sku": sku}, {"_id": 0})
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        return producto
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en obtener_producto_por_sku: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ACTUALIZAR producto
@app.put("/productos/{sku}", tags=["Administración"])
async def actualizar_producto(sku: str, stock_nuevo: Optional[int] = None, precio_nuevo: Optional[int] = None):
    """Actualiza el stock y/o precio de un producto"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Base de datos no disponible")
        
        campos_update = {}
        if stock_nuevo is not None:
            campos_update["stock_actual"] = stock_nuevo
        if precio_nuevo is not None:
            campos_update["precio_clp"] = precio_nuevo
        
        if not campos_update:
            raise HTTPException(status_code=400, detail="Debes proporcionar al menos un campo para actualizar")
        
        campos_update["ultima_actualizacion"] = datetime.utcnow().isoformat()
        
        resultado = await db.productos.update_one(
            {"sku": sku}, 
            {"$set": campos_update}
        )
        
        if resultado.matched_count == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        return {"mensaje": "Producto actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en actualizar_producto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ELIMINAR producto
@app.delete("/productos/{sku}", tags=["Administración"], status_code=200)
async def eliminar_producto(sku: str):
    """Elimina un producto del inventario"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Base de datos no disponible")
        
        resultado = await db.productos.delete_one({"sku": sku})
        
        if resultado.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado para eliminar")
        
        return {"mensaje": f"Producto con SKU {sku} eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en eliminar_producto: {e}")
        raise HTTPException(status_code=500, detail=str(e))