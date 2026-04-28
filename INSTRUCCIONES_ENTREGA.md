# 📦 INSTRUCCIONES DE ENTREGA - COLECCIONABLE API

## 🚀 OPCIÓN 1: EJECUTAR LOCALMENTE (RECOMENDADO - 100% FUNCIONAL)

### Requisitos:
- Python 3.13+
- Git

### Pasos para ejecutar:

```bash
# 1. Clonar el repositorio
git clone https://github.com/MaxisotooH/coleccionable-api.git
cd coleccionable-api

# 2. Crear e activar entorno virtual (opcional pero recomendado)
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la API
python -m uvicorn coleccionable_API.main:app --host 127.0.0.1 --port 8001 --reload

# 5. Abrir en navegador
# Accede a: http://127.0.0.1:8001/dashboard
```

### ✅ QUÉ VAS A VER:
- Dashboard Pokémon con tema profesional
- 4 Pokémon ya cargados (Charmander, Pikachu, Arcanine, Charizard)
- CRUD completo funcional:
  - ✅ Crear nuevos Pokémon
  - ✅ Listar todos los Pokémon
  - ✅ Buscar por atributos
  - ✅ Editar stock y precio
  - ✅ Eliminar Pokémon

---

## 📋 OPCIÓN 2: VER EL CÓDIGO EN GITHUB

```
Repositorio: https://github.com/MaxisotooH/coleccionable-api
```

Incluye:
- ✅ Código fuente completo
- ✅ TESTING_REPORT.md (6 tests pasados)
- ✅ requirements.txt (todas las dependencias)
- ✅ render.yaml (configuración de deploy)

---

## 🌐 OPCIÓN 3: USAR RENDER (EN LA NUBE)

```
Link: https://coleccionable-api.onrender.com/dashboard
```

**Nota:** Para que funcione en Render, es necesario configurar manualmente la variable de entorno MONGODB_URI. Si el link no carga los productos, ejecuta localmente (Opción 1).

---

## 📊 ESTRUCTURA DEL PROYECTO

```
coleccionable_API/
├── main.py                          # FastAPI principal con endpoints
├── __init__.py
└── static/
    ├── index.html                   # Dashboard HTML
    ├── script.js                    # Lógica JavaScript (CRUD)
    └── style.css                    # Estilos Pokémon
requirements.txt                      # Dependencias Python
TESTING_REPORT.md                     # Documentación de tests
render.yaml                           # Configuración Render
```

---

## 🛠️ STACK TECNOLÓGICO

**Backend:**
- FastAPI (framework web)
- MongoDB Atlas (base de datos en la nube)
- Motor (driver async para MongoDB)
- Python 3.13

**Frontend:**
- HTML5, CSS3, JavaScript vanilla
- Google Fonts (Press Start 2P, Righteous)
- Diseño Pokémon personalizado

**Deployment:**
- Render (hosting gratuito)
- GitHub (control de versiones)

---

## ✅ CHECKLIST FUNCIONAL

- ✅ Dashboard carga correctamente
- ✅ Se conecta a MongoDB
- ✅ Listar productos (GET /productos)
- ✅ Crear producto (POST /productos)
- ✅ Editar stock y precio (PUT /productos/{sku})
- ✅ Buscar por atributo (GET /productos/buscar/atributo)
- ✅ Eliminar producto (DELETE /productos/{sku})
- ✅ Atributos dinámicos funcionales
- ✅ Persistencia en MongoDB verificada
- ✅ Tema Pokémon implementado
- ✅ Responsive design
- ✅ Tests validados (6/6 pasados)
- ✅ Código en GitHub actualizado

---

## 📝 DOCUMENTACIÓN ADICIONAL

Ver `TESTING_REPORT.md` para:
- Resultados de 6 tests CRUD completos
- Arquitectura detallada
- Endpoints API documentados
- Instrucciones de configuración

---

## 🎯 RESUMEN

La forma **MÁS RÁPIDA Y SEGURA** de demostrar el proyecto es:

1. Clona el repo: `git clone https://github.com/MaxisotooH/coleccionable-api.git`
2. Instala dependencias: `pip install -r requirements.txt`
3. Ejecuta: `python -m uvicorn coleccionable_API.main:app --host 127.0.0.1 --port 8001 --reload`
4. Abre: http://127.0.0.1:8001/dashboard
5. ¡Disfruta el dashboard Pokémon funcional!

---

**Autor:** Maxisotooh  
**Fecha:** Abril 28, 2026  
**Estado:** ✅ LISTO PARA ENTREGA
