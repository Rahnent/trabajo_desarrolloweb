// Lógica para el Menú Lateral
function toggleSidebar() {
    var sidebar = document.getElementById('sidebarMenu');
    sidebar.classList.toggle('open');
}

// Lógica de Navegación SPA
function navigate(viewName) {
    // Ocultar todas las vistas
    var views = document.querySelectorAll('.spa-view');
    views.forEach(function(view) {
        view.classList.remove('active');
    });

    // Mostrar la vista elegida
    var activeView = document.getElementById('view-' + viewName);
    if (activeView) {
        activeView.classList.add('active');
    }

    // Cerrar sidebar si está abierto y hacer scroll arriba
    document.getElementById('sidebarMenu').classList.remove('open');
    window.scrollTo(0, 0);
}

// Lógica del Modal (Reemplazo de alert)
function showModal(title, text) {
    document.getElementById('modalTitle').innerText = title;
    document.getElementById('modalText').innerText = text;
    document.getElementById('appModal').classList.add('active');
}

function closeModal() {
    document.getElementById('appModal').classList.remove('active');
}