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

        if (confirm("¿Seguro que deseas eliminar los modelos seleccionados?")) {
            $.ajax({
                url: "/delete_modelos",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ ids: seleccionados }),
                success: function () {
                    location.reload();
                },
                error: function () {
                    alert("Error al eliminar modelos.");
                }
            });
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
