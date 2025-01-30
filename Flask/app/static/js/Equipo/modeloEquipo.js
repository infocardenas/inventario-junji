// Cargar marcas al abrir el modal
document.addEventListener("DOMContentLoaded", function () {
    cargarMarcas(); // Llama a la función que carga las marcas
});

// Función para cargar las marcas
async function cargarMarcas() {
    const response = await fetch("/get_marcas");
    const marcas = await response.json();
    const marcaSelect = document.getElementById("marcaSelect");

    marcaSelect.innerHTML = `<option value="">Seleccione una marca</option>`;
    marcas.forEach(marca => {
        const option = document.createElement("option");
        option.value = marca.idMarca_Equipo;
        option.textContent = marca.nombreMarcaEquipo;
        marcaSelect.appendChild(option);
    });

    limpiarSelect("tipoSelect", "Seleccione un tipo");
}

// Función para cargar los tipos basados en la marca seleccionada
async function cargarTipos() {
    const marcaId = document.getElementById("marcaSelect").value;
    const tipoSelect = document.getElementById("tipoSelect");

    if (!marcaId) {
        limpiarSelect("tipoSelect", "Seleccione un tipo");
        tipoSelect.disabled = true;
        return;
    }

    const response = await fetch(`/get_tipos/${marcaId}`);
    const tipos = await response.json();

    tipoSelect.innerHTML = `<option value="">Seleccione un tipo</option>`;
    tipos.forEach(tipo => {
        const option = document.createElement("option");
        option.value = tipo.idTipo_equipo;
        option.textContent = tipo.nombreTipo_equipo;
        tipoSelect.appendChild(option);
    });
}


// Función para limpiar un select
function limpiarSelect(id, placeholder) {
    const select = document.getElementById(id);
    select.innerHTML = `<option value="">${placeholder}</option>`;
}

$(document).ready(function () {
    // Si hay un mensaje de confirmación en `flash`, activamos el modal
    const confirmUrl = $(".flash-message[data-confirm]").data("confirm");
    if (confirmUrl) {
      configureGenericModal(
        "Eliminar Modelo de Equipo",
        "No se puede eliminar el modelo porque hay equipos asociados. ¿Deseas eliminar todas las relaciones y continuar?",
        confirmUrl
      );
    }
  });
  
