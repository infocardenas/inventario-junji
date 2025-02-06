$(document).ready(function () {
    cargarMarcas();

    // Evento para actualizar tipos de equipo al seleccionar una marca
    $("#marcaSelect").on("change", function () {
        let marcaId = $(this).val();
        if (marcaId) {
            cargarTipos(marcaId, "tipoSelect");
        } else {
            $("#tipoSelect").html('<option value="">Seleccione un tipo</option>');
        }
    });

    $("#edit_marcaSelect").on("change", function () {
        let marcaId = $(this).val();
        if (marcaId) {
            cargarTipos(marcaId, "edit_tipoSelect");
        } else {
            $("#edit_tipoSelect").html('<option value="">Seleccione un tipo</option>');
        }
    });

    // Abrir modal de edición con datos cargados
    $(".btn-editar-modelo").on("click", function () {
        let id = $(this).data("id");
        let nombre = $(this).data("nombre");
        let marcaId = $(this).data("marca-id");
        let tipoId = $(this).data("tipo-id");

        console.log("Editando ID:", id);
        console.log("Nombre:", nombre);
        console.log("Marca ID:", marcaId);
        console.log("Tipo ID:", tipoId);

        // Llenar los campos
        $("#edit_nombreModelo_equipo").val(nombre);
        $("#edit_marcaSelect").val(marcaId);

        // Cargar tipos correspondientes a la marca
        cargarTipos(marcaId, "edit_tipoSelect", tipoId);

        // Configurar la acción del formulario
        $("#editModeloEquipoForm").attr("action", `/update_modelo_equipo/${id}`);

        // Abrir el modal
        $("#editModeloEquipoModal").modal("show");
    });

    // Enviar formulario de agregar modelo
    $("#addModeloForm").on("submit", function (e) {
        e.preventDefault();
        let formData = $(this).serialize();

        $.post("/add_modelo_equipo", formData, function (response) {
            location.reload();
        }).fail(function () {
            alert("Error al agregar el modelo de equipo.");
        });
    });

    // Enviar formulario de edición
    $("#editModeloEquipoForm").on("submit", function (e) {
        e.preventDefault();
        let formData = $(this).serialize();

        $.post($(this).attr("action"), formData, function (response) {
            location.reload();
        }).fail(function () {
            alert("Error al actualizar el modelo de equipo.");
        });
    });

    // Seleccionar/Deseleccionar todos los checkboxes
    $("#toggleSelectAll").on("click", function () {
        let checkboxes = $(".row-checkbox");
        let allChecked = checkboxes.length === checkboxes.filter(":checked").length;
        checkboxes.prop("checked", !allChecked);
    });

    // Eliminar modelos seleccionados
    $("#eliminarSeleccionados").on("click", function () {
        let seleccionados = [];
        $(".row-checkbox:checked").each(function () {
            seleccionados.push($(this).closest("tr").data("id"));
        });

        if (seleccionados.length === 0) {
            alert("No hay modelos seleccionados.");
            return;
        }

        const ids = selectedRows.map(function () {
            return $(this).data("id");
        }).get();

        if (action === "delete") {
            configureGenericModal(
                "Eliminar Tipo(s) de Equipo",
                `¿Estás seguro de que deseas eliminar los tipos seleccionados? Esto afectará las relaciones asociadas.`,
                `/tipo_equipo/delete_tipo_equipo/${ids.join(',')}`
            );
        } else if (action === "edit") {
            if (selectedRows.length > 1) {
                alert("Solo puedes editar un tipo de equipo a la vez.");
                $(this).val("");
                return;
            }

            // Capturar los datos de la fila seleccionada
            const selectedRow = selectedRows.first();
            const id = selectedRow.data("id");
            const nombre = selectedRow.data("nombre");
            const marcas = selectedRow.data("marcas");

            // Rellenar el formulario dentro del modal
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

            // Configurar la acción del formulario
            $("#editTipoEquipoForm").attr("action", `/update_tipo_equipo/${id}`);

            // Abrir el modal
            $("#editTipoEquipoModal").modal("show");
        }
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
