# Guía de Deploy en Render

## Requisitos Previos

1. ✅ Cuenta en GitHub
2. ✅ Cuenta en Render (https://render.com)
3. ✅ Repositorio en GitHub (público o privado)

## Paso 1: Crear repositorio en GitHub

```bash
# En la carpeta del proyecto
git init
git add .
git commit -m "Initial commit: Coleccionable API"
git branch -M main

# Crear repositorio en GitHub (https://github.com/new)
# Copiar el comando que GitHub te da:
git remote add origin https://github.com/TU_USUARIO/coleccionable-api.git
git push -u origin main
```

## Paso 2: Conectar Render con GitHub

1. Ir a https://render.com y crear cuenta (con GitHub es más fácil)
2. Hacer clic en **"New +"** (arriba a la derecha)
3. Seleccionar **"Web Service"**
4. Hacer clic en **"Connect a repository"**
5. Autorizar Render a acceder a GitHub
6. Seleccionar tu repositorio `coleccionable-api`

## Paso 3: Configurar el servicio

Si Render lee el `render.yaml`:
- ✅ La configuración se aplicará automáticamente
- ✅ Presiona "Deploy"

Si no lo lee automáticamente, configura manualmente:

| Campo | Valor |
|-------|-------|
| **Name** | `coleccionable-api` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn coleccionable_API.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free (o pagado si necesitas mayor rendimiento) |

## Paso 4: Configurar variables de entorno

En Render, ve a **"Environment"** y agrega:

```
MONGO_URL = mongodb+srv://Maxisotooh:Facundo.2017@cluster0.bnt1q8w.mongodb.net/?appName=Cluster0
```

⚠️ **IMPORTANTE:** Si tu contraseña contiene caracteres especiales, encódifilos en la URL.

## Paso 5: Deploy

1. Presiona **"Create Web Service"**
2. Render comienza a descargar, instalar y ejecutar
3. Espera a que aparezca el mensaje **"Your service is live"**
4. Copia la URL que genera Render (ej: `https://coleccionable-api.onrender.com`)

## Paso 6: Probar la API

```bash
# Documentación interactiva
https://coleccionable-api.onrender.com/docs

# Crear producto
curl -X POST "https://coleccionable-api.onrender.com/productos" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "PKM-001",
    "nombre": "Charizard",
    "categoria": "Pokemon",
    "precio_clp": 50000,
    "stock_actual": 5,
    "atributos_especificos": [{"k": "rareza", "v": "Holografico"}]
  }'
```

## Troubleshooting

### Error: "Build Command failed"
- Verifica que `requirements.txt` tenga el formato correcto (UTF-8)
- Asegúrate de que todas las dependencias están lisadas

### Error: "Application failed to start"
- Revisa los logs en Render
- Verifica que `MONGO_URL` esté configurada
- Asegúrate de que MongoDB Atlas permite conexiones desde Render (whitelist 0.0.0.0/0)

### La API responde lentamente
- Plan Free de Render entra en modo "sleep" después de inactividad
- Actualiza a un plan pagado para mejor rendimiento

## Actualizaciones futuras

Cada vez que hagas push a GitHub:
```bash
git add .
git commit -m "Descripción del cambio"
git push origin main
```

Render detectará automáticamente el cambio y redesplegará (si lo tienes configurado con "Auto-Deploy").

## URLs Útiles

- Render Dashboard: https://dashboard.render.com
- Mi API: https://coleccionable-api.onrender.com
- Documentación Swagger: https://coleccionable-api.onrender.com/docs
- MongoDB Atlas: https://cloud.mongodb.com

---

¡Tu API está lista para producción! 🚀
