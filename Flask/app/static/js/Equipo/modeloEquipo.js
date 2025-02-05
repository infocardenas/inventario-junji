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
    $(".actions-select").on("change", function () {
        const action = $(this).val(); // Acción seleccionada
        const selectedRows = $(".row-checkbox:checked").closest("tr"); // Filas seleccionadas

        if (!selectedRows.length) {
            alert("Por favor, selecciona una fila antes de realizar una acción.");
            $(this).val(""); // Resetear el select
            return;
        }

        // Obtener los IDs de los modelos seleccionados
        const ids = selectedRows.map(function () {
            return $(this).data("id");
        }).get();

        if (action === "delete") {
            // Mostrar modal de confirmación
            configureGenericModal(
                "Eliminar Modelo(s) de Equipo",
                "¿Estás seguro de que deseas eliminar los modelos seleccionados?",
                `/delete_modelo_equipo/${ids.join(",")}` // URL de eliminación
            );
        } else if (action === "edit") {
            if (selectedRows.length > 1) {
                alert("Solo puedes editar un modelo a la vez.");
                $(this).val("");
                return;
            }

            // Capturar los datos de la fila seleccionada
            const selectedRow = selectedRows.first();
            const id = selectedRow.data("id");
            const nombreModelo = selectedRow.find("td:nth-child(2)").text();
            const tipoEquipo = selectedRow.find("td:nth-child(3)").text();
            const marcaEquipo = selectedRow.find("td:nth-child(4)").text();

            // Llenar el formulario dentro del modal
            $("#editModeloEquipoLabel").text(`Editar Modelo de Equipo: ${nombreModelo}`);
            $("#edit_nombreModelo_equipo").val(nombreModelo);
            $("#edit_tipoEquipo").val(tipoEquipo);
            $("#edit_marcaEquipo").val(marcaEquipo);

            // Configurar la acción del formulario
            $("#editModeloEquipoForm").attr("action", `/edit_modelo_equipo/${id}`);

            // Mostrar el modal
            $("#editModeloEquipoModal").modal("show");
        }

        $(this).val(""); // Resetear el select después de usarlo
    });
});
