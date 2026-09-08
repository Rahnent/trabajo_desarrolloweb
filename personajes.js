
const respuestaPersonajesAPI = {
    "status": 200,
    "message": "Personajes obtenidos correctamente",
    "data": [
        {
            "id": 1,
            "nombre": "Iron Man",
            "descripcion": "Genio, multimillonario, playboy, filántropo. Armadura de alta tecnología.",
            "afiliacion": "Avenger",
            "badgeClass": "marvel-red",
            "imagen": "img/ironman.jpg"
        },
        {
            "id": 2,
            "nombre": "Spider-Man",
            "descripcion": "Tu amigable vecino. Agilidad arácnida y sentido arácnido.",
            "afiliacion": "Vengador Reserva",
            "badgeClass": "bg-primary",
            "imagen": "img/spiderman.jpg"
        },
        {
            "id": 3,
            "nombre": "Wolverine",
            "descripcion": "Factor de curación acelerado y esqueleto de Adamantium.",
            "afiliacion": "X-Men",
            "badgeClass": "bg-warning text-dark",
            "imagen": "img/wolverine.jpg"
        },
        {
            "id": 4,
            "nombre": "Capitán América",
            "descripcion": "El primer vengador. Fuerza sobrehumana y escudo de Vibranium.",
            "afiliacion": "Avenger",
            "badgeClass": "marvel-red",
            "imagen": "img/capitan.jpg"
        }
    ]
};


function cargarPersonajes() {
    const contenedor = document.getElementById("contenedorPersonajes");
    if (!contenedor) return;

    contenedor.innerHTML = "";

    respuestaPersonajesAPI.data.forEach((heroe) => {
        const col = document.createElement("div");
        col.className = "col";

        col.innerHTML = `
            <div class="card bg-dark text-white border-secondary h-100 card-hover text-center">
                <div class="p-4">
                    <img src="${heroe.imagen}" class="card-img-top rounded-circle border border-danger border-2" alt="${heroe.nombre}" style="width: 120px; height: 120px; object-fit: cover;">
                </div>
                <div class="card-body">
                    <h5 class="card-title text-uppercase">${heroe.nombre}</h5>
                    <p class="card-text text-secondary small">${heroe.descripcion}</p>
                </div>
                <div class="card-footer border-secondary">
                    <span class="badge ${heroe.badgeClass}">${heroe.afiliacion}</span>
                </div>
            </div>
        `;

        contenedor.appendChild(col);
    });
}


document.addEventListener("DOMContentLoaded", cargarPersonajes);