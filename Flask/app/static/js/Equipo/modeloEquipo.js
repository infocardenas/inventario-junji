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

    // **Validación y Envío del Formulario de Agregar Modelo**
    $("#addModeloForm").on("submit", function (e) {
        e.preventDefault();
        let nombreModelo = $("#nombre_modelo_equipo").val().trim().toLowerCase();
        let tipoEquipo = $("#tipoSelect").val();  // Obtener el valor del select
        let marcaEquipo = $("#marcaSelect").val(); // Obtener la marca seleccionada

        if (!nombreModelo) {
            mostrarMensaje("El nombre del modelo no puede estar vacío.", "warning");
            return;
        }
        if (!marcaEquipo) {
            mostrarMensaje("Debe seleccionar una marca antes de guardar.", "warning");
            return;
        }
    
        if (!tipoEquipo) {
            mostrarMensaje("Debe seleccionar un tipo de equipo antes de guardar.", "warning");
            return;
        }

        // **Verificar si el modelo ya existe en la tabla**
        let modeloDuplicado = false;
        $("#myTableBody tr").each(function () {
            let nombreExistente = $(this).find("td:nth-child(2)").text().trim().toLowerCase();
            if (nombreExistente === nombreModelo) {
                modeloDuplicado = true;
                return false; // Detener el bucle si se encuentra un duplicado
            }
        });

        if (modeloDuplicado) {
            mostrarMensaje("Este modelo ya existe en la lista. Por favor, elija otro nombre.", "warning");
            return;
        }

        // **Enviar formulario con AJAX**
        $.post("/add_modelo_equipo", $("#addModeloForm").serialize(), function (response) {
            mostrarMensaje(response.message, response.tipo_alerta);
            if (response.status === "success") {
                setTimeout(() => location.reload(), 1500);
            }
        }).fail(function (xhr) {
            let errorMsg = xhr.responseJSON?.message || "Error al agregar el modelo.";
            let tipoAlerta = xhr.responseJSON?.tipo_alerta || "danger";
            mostrarMensaje(errorMsg, tipoAlerta);
        });
    });

    // **Editar Modelo**
    $(".btn-editar-modelo").on("click", function () {
        let modeloId = $(this).data("id");

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

                cargarTipos(modelo.idMarca_Equipo, "edit_tipoSelect", modelo.idTipo_equipo);
                $("#edit_tipoSelect").prop("disabled", false);
            });

            $("#editModeloEquipoForm").attr("action", `/update_modelo_equipo/${modeloId}`);

            $("#editModeloEquipoModal").modal("show");
        }).fail(function () {
            mostrarMensaje("Error al obtener datos del modelo.", "danger");
        });
    });

        $("#eliminarSeleccionados").on("click", function () {
            let seleccionados = $(".row-checkbox:checked").closest("tr").map(function () {
                return $(this).data("id");
            }).get();
    
            if (seleccionados.length === 0) {
                mostrarMensaje("Debe seleccionar al menos un modelo para eliminar.", "warning");
                return;
            }
    
            $("#confirmDeleteModal").modal("show");
    
            $("#confirmDeleteBtn").off("click").on("click", function () {
                $("#confirmDeleteModal").modal("hide");
    
                $.ajax({
                    url: "/delete_modelo_equipo",
                    type: "POST",
                    contentType: "application/json",
                    data: JSON.stringify({ ids: seleccionados }),
                    success: function (response) {
                        mostrarMensaje(response.message, response.tipo_alerta);
                        setTimeout(() => location.reload(), 2000);
                    },
                    error: function (xhr) {
                        let errorMsg = xhr.responseJSON?.message || "Error al eliminar los modelos.";
                        let tipoAlerta = xhr.responseJSON?.tipo_alerta || "danger";
                        mostrarMensaje(errorMsg, tipoAlerta);
                    }
                });
            });
        });
    });

    
// **Función para Mostrar Mensajes en la UI**
function mostrarMensaje(mensaje, tipo) {
    let alertContainer = $("#alertContainer");

    if (alertContainer.length === 0) {
        console.warn("El contenedor #alertContainer no se encontró. Creándolo...");
        $("body").prepend('<div id="alertContainer" class="alert d-none" role="alert"></div>');
        alertContainer = $("#alertContainer");
    }

    alertContainer.removeClass("d-none alert-success alert-warning alert-danger")
        .addClass(`alert alert-${tipo}`)
        .html(`<i class="bi bi-info-circle"></i> ${mensaje}`)
        .fadeIn();

    setTimeout(() => {
        alertContainer.fadeOut("slow", function () {
            $(this).addClass("d-none");
        });
    }, 4000);
}



// **Función para Cargar Marcas desde el Backend**
function cargarMarcas() {
    $.get("/get_marcas", function (marcas) {
        let select = $("#marcaSelect, #edit_marcaSelect");
        select.empty().append('<option value="">Seleccione una marca</option>');
        $.each(marcas, function (i, marca) {
            select.append(`<option value="${marca.idMarca_Equipo}">${marca.nombreMarcaEquipo}</option>`);
        });
    }).fail(function () {
        mostrarMensaje("Error al cargar marcas.", "danger");
    });
}

// **Función para Cargar Tipos de Equipo Según la Marca Seleccionada**
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
    }).fail(function () {
        mostrarMensaje("Error al cargar tipos de equipo.", "danger");
    });
}
