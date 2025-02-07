$(document).ready(function () {
    // Detectar cambios en los checkboxes para actualizar los botones
    $(document).on("change", ".row-checkbox", function () {
        actualizarBotonEditar();
    });

    function actualizarBotonEditar() {
        const seleccionados = $(".row-checkbox:checked");
        const deleteButton = $(".delete-button");
        const editButton = $(".edit-button");

        if (seleccionados.length > 0) {
            // Construir la URL para eliminar (con múltiples IDs separados por comas)
            const ids = seleccionados.map(function () {
                return $(this).closest("tr").data("id");
            }).get().join(",");

            deleteButton.data("url", `/delete_tipo_equipo/${ids}`);
            deleteButton.prop("disabled", false);
        } else {
            deleteButton.data("url", ""); // Limpiar URL cuando no hay selección
            deleteButton.prop("disabled", true);
        }

        if (seleccionados.length === 1) {
            // Obtener el ID de la única fila seleccionada para edición
            const selectedRow = seleccionados.closest("tr");
            const id = selectedRow.data("id");
            const nombre = selectedRow.data("nombre");
            const marcas = selectedRow.data("marcas");

            editButton.data("url", `/update_tipo_equipo/${id}`);
            editButton.prop("disabled", false);

            // Llenar el modal de edición
            $("#editTipoEquipoLabel").text(`Editar tipo de equipo: ${nombre}`);
            $("#edit_nombreTipo_equipo").val(nombre);

            // Desmarcar todos los checkboxes antes de marcar los seleccionados
            $("#editTipoEquipoModal input[name='marcas[]']").prop("checked", false);

            if (marcas) {
                const marcasSeleccionadas = marcas.split(",").map(marca => marca.trim());

                $("#editTipoEquipoModal input[name='marcas[]']").each(function () {
                    if (marcasSeleccionadas.includes($(this).next("label").text().trim())) {
                        $(this).prop("checked", true);
                    }
                });
            }

            // Configurar la acción del formulario con la URL correcta
            $("#editTipoEquipoForm").attr("action", `/update_tipo_equipo/${id}`);

        } else {
            editButton.data("url", "");
            editButton.prop("disabled", true);
        }
    }

    // Manejar clic en el botón "Editar" para abrir el modal
    $(".edit-button").on("click", function () {
        if ($(this).prop("disabled")) return; // Evita abrir el modal si está deshabilitado
        $("#editTipoEquipoModal").modal("show");
    });

});

// Función para cargar marcas desde el backend
function cargarMarcas() {
    $.get("/get_marcas", function (marcas) {
        let select = $("#marcaSelect, #edit_marcaSelect");
        select.empty().append('<option value="">Seleccione una marca</option>');
        $.each(marcas, function (i, marca) {
            select.append(`<option value="${marca.idMarca_Equipo}">${marca.nombreMarcaEquipo}</option>`);
        });
    });
}

// Función para cargar tipos de equipo según la marca seleccionada
function cargarTipos(marcaId, selectId, tipoSeleccionado = null) {
    if (!marcaId) {
        $(`#${selectId}`).empty().append('<option value="">Seleccione un tipo</option>');
        return;
    }

    $.get(`/get_tipos/${marcaId}`, function (tipos) {
        let select = $(`#${selectId}`);
        select.empty().append('<option value="">Seleccione un tipo</option>');
        $.each(tipos, function (i, tipo) {
            let selected = tipoSeleccionado && tipo.idTipo_equipo == tipoSeleccionado ? "selected" : "";
            select.append(`<option value="${tipo.idTipo_equipo}" ${selected}>${tipo.nombreTipo_equipo}</option>`);
        });
    });
}
