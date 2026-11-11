// --- LÓGICA DE NAVEGACIÓN Y SIDEBAR ---
function toggleSidebar() {
    document.getElementById('sidebarMenu').classList.toggle('open');
}

function navigate(viewName) {
    const views = document.querySelectorAll('.spa-view');
    views.forEach(view => view.classList.remove('active'));

    const activeView = document.getElementById('view-' + viewName);
    if (activeView) activeView.classList.add('active');

    document.getElementById('sidebarMenu').classList.remove('open');
    window.scrollTo(0, 0);
}

// --- LÓGICA DEL MODAL ---
function showModal(title, text, iconClass = 'fa-circle-info', iconColor = '#4a332a') {
    document.getElementById('modalTitle').innerText = title;
    document.getElementById('modalText').innerText = text;
    
    const icon = document.getElementById('modalIcon');
    icon.className = `fa-solid ${iconClass} fa-3x mb-15`;
    icon.style.color = iconColor;

    document.getElementById('appModal').classList.add('active');
}

function closeModal() {
    document.getElementById('appModal').classList.remove('active');
}

// --- ESTADO GLOBAL ---
let carrito = 0;

function actualizarBadgeCarrito() {
    document.getElementById('cart-count').innerText = carrito;
}

// --- INTERACCIÓN CON DOM Y SERVICIOS SIMULADOS ---

// Al cargar la página, intentar traer los productos
document.addEventListener("DOMContentLoaded", () => {
    cargarProductos();
});

function cargarProductos() {
    const loadingState = document.getElementById('loading-state');
    const errorState = document.getElementById('error-state');
    const catalogo = document.getElementById('catalogo-productos');

    // Estado 1: Carga
    loadingState.classList.remove('hidden');
    errorState.classList.add('hidden');
    catalogo.classList.add('hidden');
    catalogo.innerHTML = ''; // Limpiar catálogo

    // Simular un delay de red y una petición fetch
    setTimeout(() => {
        fetch('productos.json')
            .then(response => {
                if (!response.ok) throw new Error('Error al cargar datos');
                return response.json();
            })
            .then(data => {
                // Estado 2: Éxito
                loadingState.classList.add('hidden');
                renderizarCatalogo(data);
                catalogo.classList.remove('hidden');
            })
            .catch(error => {
                // Estado 3: Error
                console.error(error);
                loadingState.classList.add('hidden');
                errorState.classList.remove('hidden');
            });
    }, 1500); // 1.5 segundos de carga simulada
}

function renderizarCatalogo(productos) {
    const catalogo = document.getElementById('catalogo-productos');

    // Si el arreglo viene vacío (Estado vacío)
    if(productos.length === 0) {
        catalogo.innerHTML = `<div class="col-xs-12 text-center p-20"><p>No hay productos disponibles en este momento.</p></div>`;
        return;
    }

    // Creación dinámica de Nodos (DOM API)
    productos.forEach(producto => {
        const colDiv = document.createElement('div');
        colDiv.className = 'col-md-4 col-sm-6 col-xs-12';

        colDiv.innerHTML = `
            <div class="product-card">
                <div class="product-img-container">
                    <img src="${producto.imagen}" alt="${producto.nombre}" class="product-img">
                </div>
                <div class="product-info">
                    <h4 class="product-title">${producto.nombre}</h4>
                    <p class="product-desc">${producto.descripcion}</p>
                    <div class="product-price">$${producto.precio.toLocaleString('es-CL')}</div>
                    <button class="btn-primary-custom" onclick="agregarAlCarrito('${producto.nombre}')">
                        <i class="fa-solid fa-plus"></i> Agregar
                    </button>
                </div>
            </div>
        `;
        catalogo.appendChild(colDiv);
    });
}

function agregarAlCarrito(nombreProducto) {
    // Acción de agregar a carrito
    carrito++;
    actualizarBadgeCarrito();
    // Modal de éxito simulando que se agregó
    showModal('¡Agregado!', `Se añadió "${nombreProducto}" a tu pedido.`, 'fa-circle-check', '#5cb85c');
}

function simularCompra() {
    if(carrito === 0) {
        showModal('Carrito Vacío', 'Agrega algunos productos antes de confirmar el pedido.', 'fa-basket-shopping', '#f0ad4e');
        return;
    }
    
    // Simular un envío de orden a la API (Aquí estaba el error de CSS)
    showModal('Procesando...', 'Enviando orden a la cocina...', 'fa-spinner fa-spin', '#4a332a');
    
    setTimeout(() => {
        carrito = 0;
        actualizarBadgeCarrito();
        showModal('¡Pedido Confirmado!', 'Tu pedido ha sido recibido y está en preparación.', 'fa-circle-check', '#5cb85c');
    }, 2000);
}