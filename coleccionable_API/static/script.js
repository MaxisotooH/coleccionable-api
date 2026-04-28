// Configuración
const API_BASE_URL = window.location.origin;

// Elementos del DOM
const navBtns = document.querySelectorAll('.nav-btn');
const tabContents = document.querySelectorAll('.tab-content');
const crearForm = document.getElementById('crearForm');
const agregarAtributoBtn = document.getElementById('agregarAtributo');
const atributosContainer = document.getElementById('atributosContainer');
const recargarProductosBtn = document.getElementById('recargarProductos');
const buscarBtn = document.getElementById('buscarBtn');
const modal = document.getElementById('modalProducto');
const closeModal = document.querySelector('.close');

// Event Listeners - Navegación
navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        
        // Remover active de todos
        navBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(tc => tc.classList.remove('active'));
        
        // Agregar active al seleccionado
        btn.classList.add('active');
        document.getElementById(tab).classList.add('active');

        // Si es listar, cargar productos
        if (tab === 'listar') {
            cargarProductos();
        }
    });
});

// Event Listeners - Formulario
crearForm.addEventListener('submit', crearProducto);

agregarAtributoBtn.addEventListener('click', (e) => {
    e.preventDefault();
    agregarAtributo();
});

document.addEventListener('click', (e) => {
    if (e.target.classList.contains('btn-eliminar-atributo')) {
        e.target.parentElement.remove();
    }
});

// Event Listeners - Otros
recargarProductosBtn.addEventListener('click', cargarProductos);
buscarBtn.addEventListener('click', buscarPorAtributo);
closeModal.addEventListener('click', cerrarModal);
window.addEventListener('click', (e) => {
    if (e.target === modal) cerrarModal();
});

// ==================== FUNCIONES ====================

// 1. CREAR PRODUCTO
async function crearProducto(e) {
    e.preventDefault();
    
    const sku = document.getElementById('sku').value;
    const nombre = document.getElementById('nombre').value;
    const categoria = document.getElementById('categoria').value;
    const precio_clp = parseInt(document.getElementById('precio').value);
    const stock_actual = parseInt(document.getElementById('stock').value);

    // Obtener atributos
    const atributosInputs = document.querySelectorAll('.atributo-item');
    const atributos_especificos = [];
    
    atributosInputs.forEach(item => {
        const key = item.querySelector('.atributo-key').value;
        const value = item.querySelector('.atributo-value').value;
        if (key && value) {
            atributos_especificos.push({ k: key, v: value });
        }
    });

    const producto = {
        sku,
        nombre,
        categoria,
        precio_clp,
        stock_actual,
        atributos_especificos
    };

    try {
        const response = await fetch(`${API_BASE_URL}/productos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(producto)
        });

        let data;
        try {
            data = await response.json();
        } catch (e) {
            data = { detail: `Error del servidor: ${response.statusText}` };
        }

        if (response.ok) {
            mostrarMensaje('crearMensaje', `✅ Producto "${nombre}" creado exitosamente!`, 'success');
            crearForm.reset();
            atributosContainer.innerHTML = `
                <div class="atributo-item">
                    <input type="text" placeholder="Clave (ej: rareza)" class="atributo-key">
                    <input type="text" placeholder="Valor (ej: Holográfico)" class="atributo-value">
                    <button type="button" class="btn-eliminar-atributo">✕</button>
                </div>
            `;
        } else {
            mostrarMensaje('crearMensaje', `❌ Error: ${data.detail || 'Error desconocido'}`, 'error');
        }
    } catch (error) {
        mostrarMensaje('crearMensaje', `❌ Error de conexión: ${error.message}`, 'error');
    }
}

// 2. LISTAR PRODUCTOS
async function cargarProductos() {
    const productosLista = document.getElementById('productosLista');
    productosLista.innerHTML = '<p style="text-align: center; color: #666;">Cargando...</p>';

    try {
        // Obtener todos los productos
        const response = await fetch(`${API_BASE_URL}/productos`);
        
        if (!response.ok) {
            mostrarMensaje('listarMensaje', `❌ Error al cargar productos: ${response.status}`, 'error');
            productosLista.innerHTML = '';
            return;
        }

        let productos;
        try {
            productos = await response.json();
        } catch (e) {
            mostrarMensaje('listarMensaje', `❌ Error procesando respuesta del servidor`, 'error');
            productosLista.innerHTML = '';
            return;
        }
        
        if (Array.isArray(productos) && productos.length === 0) {
            productosLista.innerHTML = '<p style="text-align: center; color: #999;">No hay productos registrados</p>';
            return;
        }

        productosLista.innerHTML = productos.map(p => crearTarjetaProducto(p)).join('');
        
        // Agregar event listeners a los botones
        document.querySelectorAll('.btn-editar').forEach(btn => {
            btn.addEventListener('click', () => abrirModalProducto(btn.dataset.sku));
        });
        
        document.querySelectorAll('.btn-eliminar').forEach(btn => {
            btn.addEventListener('click', () => confirmarEliminar(btn.dataset.sku));
        });
        
        mostrarMensaje('listarMensaje', '', '');
    } catch (error) {
        productosLista.innerHTML = '<p style="text-align: center; color: #666;">No se pudieron cargar los productos. Intenta buscar por atributo.</p>';
        mostrarMensaje('listarMensaje', `ℹ️ Consejo: Usa "Buscar por Atributo" para encontrar productos existentes`, 'info');
    }
}

// 3. BUSCAR POR ATRIBUTO
async function buscarPorAtributo() {
    const clave = document.getElementById('buscarClave').value.trim();
    const valor = document.getElementById('buscarValor').value.trim();
    const resultados = document.getElementById('resultadosBusqueda');

    if (!clave || !valor) {
        mostrarMensaje('buscarMensaje', '⚠️ Completa ambos campos', 'error');
        return;
    }

    resultados.innerHTML = '<p style="text-align: center; color: #666;">Buscando...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/productos/buscar/atributo?clave=${encodeURIComponent(clave)}&valor=${encodeURIComponent(valor)}`);
        
        if (!response.ok) {
            mostrarMensaje('buscarMensaje', `❌ Error en la búsqueda: ${response.status}`, 'error');
            resultados.innerHTML = '';
            return;
        }

        let productos;
        try {
            productos = await response.json();
        } catch (e) {
            mostrarMensaje('buscarMensaje', `❌ Error procesando respuesta del servidor`, 'error');
            resultados.innerHTML = '';
            return;
        }

        if (Array.isArray(productos) && productos.length > 0) {
            resultados.innerHTML = productos.map(p => crearTarjetaProducto(p)).join('');
            mostrarMensaje('buscarMensaje', `✅ Se encontraron ${productos.length} producto(s)`, 'success');
            
            // Agregar event listeners
            document.querySelectorAll('.btn-editar').forEach(btn => {
                btn.addEventListener('click', () => abrirModalProducto(btn.dataset.sku));
            });
            
            document.querySelectorAll('.btn-eliminar').forEach(btn => {
                btn.addEventListener('click', () => confirmarEliminar(btn.dataset.sku));
            });
        } else {
            resultados.innerHTML = '<p style="text-align: center; color: #999;">No se encontraron productos</p>';
            mostrarMensaje('buscarMensaje', '❌ No hay productos con esos atributos', 'error');
        }
    } catch (error) {
        resultados.innerHTML = '';
        mostrarMensaje('buscarMensaje', `❌ Error de conexión: ${error.message}`, 'error');
    }
}

// 4. ABRIR MODAL CON DETALLES
async function abrirModalProducto(sku) {
    try {
        const response = await fetch(`${API_BASE_URL}/productos/${sku}`);
        
        if (!response.ok) {
            alert(`❌ Error al cargar producto: ${response.status}`);
            return;
        }

        let producto;
        try {
            producto = await response.json();
        } catch (e) {
            alert(`❌ Error procesando respuesta del servidor`);
            return;
        }

        const modalBody = document.getElementById('modalBody');
        const modalTitulo = document.getElementById('modalTitulo');

        modalTitulo.textContent = `Producto: ${producto.nombre}`;
        
        let atributosHTML = '';
        if (producto.atributos_especificos && producto.atributos_especificos.length > 0) {
            atributosHTML = '<strong>Atributos:</strong><br>';
            producto.atributos_especificos.forEach(a => {
                atributosHTML += `<span class="atributo-badge">${a.k}: ${a.v}</span> `;
            });
        }

        modalBody.innerHTML = `
            <p><strong>SKU:</strong> ${producto.sku}</p>
            <p><strong>Nombre:</strong> ${producto.nombre}</p>
            <p><strong>Categoría:</strong> ${producto.categoria}</p>
            <p><strong>Precio:</strong> $${producto.precio_clp?.toLocaleString('es-CL') || 'N/A'}</p>
            <p><strong>Stock:</strong> ${producto.stock_actual || 'N/A'} unidades</p>
            <div>${atributosHTML}</div>
            <div class="modal-actions">
                <button class="btn-editar" onclick="abrirEditarProducto('${sku}')">✏️ Editar Stock/Precio</button>
                <button class="btn-eliminar" onclick="confirmarEliminar('${sku}')">🗑️ Eliminar</button>
            </div>
        `;

        modal.classList.add('active');
    } catch (error) {
        alert(`❌ Error de conexión: ${error.message}`);
    }
}

// 5. EDITAR PRODUCTO
function abrirEditarProducto(sku) {
    const stockNuevo = prompt('Nuevo stock:');
    if (stockNuevo !== null) {
        actualizarProducto(sku, parseInt(stockNuevo), null);
    }
}

async function actualizarProducto(sku, stock_nuevo, precio_nuevo) {
    try {
        let url = `${API_BASE_URL}/productos/${sku}?`;
        if (stock_nuevo !== null) url += `stock_nuevo=${stock_nuevo}&`;
        if (precio_nuevo !== null) url += `precio_nuevo=${precio_nuevo}`;

        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        let data;
        try {
            data = await response.json();
        } catch (e) {
            data = { mensaje: `Error del servidor: ${response.statusText}` };
        }

        if (response.ok) {
            alert(`✅ Producto actualizado exitosamente`);
            cerrarModal();
            cargarProductos();
        } else {
            alert(`❌ Error al actualizar: ${data.detail || 'Error desconocido'}`);
        }
    } catch (error) {
        alert(`❌ Error de conexión: ${error.message}`);
    }
}

// 6. ELIMINAR PRODUCTO
async function confirmarEliminar(sku) {
    if (confirm(`¿Estás seguro de que deseas eliminar el producto ${sku}?`)) {
        try {
            const response = await fetch(`${API_BASE_URL}/productos/${sku}`, {
                method: 'DELETE'
            });

            let data;
            try {
                data = await response.json();
            } catch (e) {
                data = { mensaje: `Error del servidor: ${response.statusText}` };
            }

            if (response.ok) {
                alert(`✅ Producto eliminado exitosamente`);
                cerrarModal();
                cargarProductos();
            } else {
                alert(`❌ Error al eliminar: ${data.detail || 'Error desconocido'}`);
            }
        } catch (error) {
            alert(`❌ Error de conexión: ${error.message}`);
        }
        }
    }
}

// ==================== UTILIDADES ====================

// Crear tarjeta de producto
function crearTarjetaProducto(p) {
    const atributosHTML = (p.atributos_especificos || [])
        .map(a => `<span class="atributo-badge">${a.k}: ${a.v}</span>`)
        .join('');

    return `
        <div class="producto-card">
            <div class="sku">${p.sku}</div>
            <h3>${p.nombre}</h3>
            <p><strong>Categoría:</strong> ${p.categoria}</p>
            <p class="precio">$${(p.precio_clp || 0).toLocaleString('es-CL')}</p>
            <p class="stock">📦 Stock: ${p.stock_actual || 0}</p>
            ${atributosHTML ? `<div class="atributos">${atributosHTML}</div>` : ''}
            <div class="producto-actions">
                <button class="btn-editar" data-sku="${p.sku}">📋 Ver</button>
                <button class="btn-eliminar" data-sku="${p.sku}">🗑️ Eliminar</button>
            </div>
        </div>
    `;
}

// Agregar atributo
function agregarAtributo() {
    const nuevoAtributo = document.createElement('div');
    nuevoAtributo.className = 'atributo-item';
    nuevoAtributo.innerHTML = `
        <input type="text" placeholder="Clave (ej: rareza)" class="atributo-key">
        <input type="text" placeholder="Valor (ej: Holográfico)" class="atributo-value">
        <button type="button" class="btn-eliminar-atributo">✕</button>
    `;
    atributosContainer.appendChild(nuevoAtributo);
}

// Mostrar mensaje
function mostrarMensaje(elementoId, mensaje, tipo) {
    const elemento = document.getElementById(elementoId);
    elemento.textContent = mensaje;
    elemento.className = 'mensaje';
    if (mensaje) {
        elemento.classList.add(tipo);
    }
}

// Cerrar modal
function cerrarModal() {
    modal.classList.remove('active');
}

// Cargar productos al iniciar
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ Dashboard cargado correctamente');
});
