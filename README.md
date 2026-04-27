# Sistema de Gestión de Inventario - Coleccionables API

API RESTful para la gestión de inventario de coleccionables construida con FastAPI y MongoDB Atlas.

## Características

- ✅ CRUD completo (Create, Read, Update, Delete)
- ✅ Búsqueda por atributos
- ✅ Validación de datos con Pydantic
- ✅ Base de datos MongoDB Atlas
- ✅ Documentación automática con Swagger

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/productos` | Crear producto |
| GET | `/productos/{sku}` | Obtener producto por SKU |
| GET | `/productos/buscar/atributo?clave=X&valor=Y` | Buscar por atributo |
| PUT | `/productos/{sku}?stock_nuevo=X&precio_nuevo=Y` | Actualizar producto |
| DELETE | `/productos/{sku}` | Eliminar producto |

## Instalación Local

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno (Windows)
.\.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar servidor
uvicorn coleccionable_API.main:app --reload --port 8000
```

La API estará disponible en `http://127.0.0.1:8000/docs`

## Deploy en Render

### Opción 1: Usando Dashboard de Render (Recomendado)

1. **Crear cuenta en [render.com](https://render.com)**
2. **Conectar repositorio de GitHub**
   - New Web Service
   - Connect a GitHub repository
   - Seleccionar este repositorio
3. **Configurar el servicio:**
   - Name: `coleccionable-api`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn coleccionable_API.main:app --host 0.0.0.0 --port $PORT`
4. **Variables de entorno:**
   - `MONGO_URL`: Tu URI de MongoDB Atlas
5. **Deploy**

### Opción 2: Usando render.yaml (Infraestructura como Código)

El archivo `render.yaml` está configurado. Solo sube a GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/tu-usuario/coleccionable-api.git
git push -u origin main
```

Render leerá automáticamente `render.yaml` y desplegará según esas especificaciones.

## Variables de Entorno

Copia `.env.example` a `.env` y configura:

```env
MONGO_URL=mongodb+srv://usuario:contraseña@cluster0.xxxxx.mongodb.net/?appName=Cluster0
```

## Estructura del Proyecto

```
coleccionable_Api/
├── coleccionable_API/
│   ├── __init__.py
│   └── main.py          # Aplicación FastAPI
├── requirements.txt     # Dependencias Python
├── render.yaml          # Configuración Render
├── .env.example         # Variables de entorno (ejemplo)
├── .gitignore          # Archivos a ignorar en Git
└── README.md           # Este archivo
```

## Ejemplo de Uso (curl)

### Crear Producto
```bash
curl -X POST "http://localhost:8000/productos" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "PKM-001",
    "nombre": "Charizard Holográfico",
    "categoria": "Pokémon",
    "precio_clp": 50000,
    "stock_actual": 5,
    "atributos_especificos": [
      {"k": "rareza", "v": "Holográfico"}
    ]
  }'
```

### Obtener Producto
```bash
curl "http://localhost:8000/productos/PKM-001"
```

### Buscar por Atributo
```bash
curl "http://localhost:8000/productos/buscar/atributo?clave=rareza&valor=Holografico"
```

### Actualizar Stock
```bash
curl -X PUT "http://localhost:8000/productos/PKM-001?stock_nuevo=20"
```

### Eliminar Producto
```bash
curl -X DELETE "http://localhost:8000/productos/PKM-001"
```

## Documentación Interactiva

Accede a la documentación Swagger en:
- **Local:** http://localhost:8000/docs
- **Render:** https://tu-api.onrender.com/docs

## Tecnologías

- **FastAPI** - Framework web asincrónico
- **Uvicorn** - Servidor ASGI
- **Pydantic** - Validación de datos
- **Motor** - Driver MongoDB asincrónico
- **MongoDB Atlas** - Base de datos NoSQL en la nube

## Licencia

MIT
