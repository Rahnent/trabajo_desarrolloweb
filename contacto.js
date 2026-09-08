
const heroesAPI = {
    "status": 200,
    "message": "Héroes obtenidos correctamente",
    "data": [
        { "id": "ironman", "nombre": "Iron Man (Tony Stark)" },
        { "id": "spiderman", "nombre": "Spider-Man (Peter Parker)" },
        { "id": "capitan", "nombre": "Capitán América (Steve Rogers)" },
        { "id": "wolverine", "nombre": "Wolverine (Logan)" },
        { "id": "shield", "nombre": "Comando Central S.H.I.E.L.D." }
    ]
};


function cargarHeroesSelect() {
    const cmb = document.getElementById("cmbHeroe");
    if (!cmb) return;

    heroesAPI.data.forEach((heroe) => {
        const opt = document.createElement("option");
        opt.setAttribute("value", heroe.id);
        opt.innerText = heroe.nombre;
        cmb.appendChild(opt);
    });
}


document.addEventListener("DOMContentLoaded", cargarHeroesSelect);