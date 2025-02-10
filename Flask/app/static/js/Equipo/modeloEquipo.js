$(document).ready(function () {
    cargarMarcas();

    // Deshabilitar select de tipos hasta que se elija una marca
    $("#tipoSelect, #edit_tipoSelect").prop("disabled", true);

    // Evento para actualizar tipos de equipo al seleccionar una marca en agregar
    $("#marcaSelect").on("change", function () {
        let marcaId = $(this).val();
        if (marcaId) {
            cargarTipos(marcaId, "tipoSelect");
            $("#tipoSelect").prop("disabled", false);
        } else {
            $("#tipoSelect").empty().append('<option value="">Seleccione un tipo</option>').prop("disabled", true);
        }
    });

    // Evento para actualizar tipos de equipo al seleccionar una marca en edición
    $("#edit_marcaSelect").on("change", function () {
        let marcaId = $(this).val();
        if (marcaId) {
            cargarTipos(marcaId, "edit_tipoSelect");
            $("#edit_tipoSelect").prop("disabled", false);
        } else {
            $("#edit_tipoSelect").empty().append('<option value="">Seleccione un tipo</option>').prop("disabled", true);
        }
    });

    // Cargar datos en el modal de edición antes de abrirlo
    $(".btn-editar-modelo").on("click", function () {
        let modeloId = $(this).data("id");

        // Hacer una solicitud AJAX para obtener los detalles del modelo
        $.get(`/get_modelo/${modeloId}`, function (modelo) {
            console.log("Datos del modelo:", modelo);

            $("#edit_nombreModelo_equipo").val(modelo.nombreModeloequipo);

            // Cargar marcas y seleccionar la correcta
            $.get("/get_marcas", function (marcas) {
                let select = $("#edit_marcaSelect");
                select.empty().append('<option value="">Seleccione una marca</option>');

                $.each(marcas, function (i, marca) {
                    let selected = modelo.idMarca_Equipo == marca.idMarca_Equipo ? "selected" : "";
                    select.append(`<option value="${marca.idMarca_Equipo}" ${selected}>${marca.nombreMarcaEquipo}</option>`);
                });

                // Una vez seleccionada la marca, cargar los tipos y seleccionar el correcto
                cargarTipos(modelo.idMarca_Equipo, "edit_tipoSelect", modelo.idTipo_equipo);
                $("#edit_tipoSelect").prop("disabled", false);
            });

            // Configurar la acción del formulario
            $("#editModeloEquipoForm").attr("action", `/update_modelo_equipo/${modeloId}`);

            // Abrir el modal
            $("#editModeloEquipoModal").modal("show");
        }).fail(function () {
            alert("Error al obtener datos del modelo.");
        });
    });

    // Enviar formulario de edición
    $("#editModeloEquipoForm").on("submit", function (e) {
        e.preventDefault();
        let formData = $(this).serialize();

        $.post($(this).attr("action"), formData, function () {
            location.reload();
        }).fail(function () {
            alert("Error al actualizar el modelo de equipo.");
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

    // Función para cargar tipos de equipo según la marca seleccionada y mantener selección previa
    function cargarTipos(marcaId, selectId, tipoSeleccionado = null) {
        if (!marcaId) {
            $(`#${selectId}`).empty().append('<option value="">Seleccione un tipo</option>').prop("disabled", true);
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
});
