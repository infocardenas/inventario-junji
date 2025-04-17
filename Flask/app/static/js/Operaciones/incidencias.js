$(document).ready(function () {
    // ✅ Evento para editar incidencia (Abrir modal con datos correctos)
    $(".edit-equipo-btn").on("click", function () {
        const idEquipoInc = limpiarDato($(this).data("id"));
        const estadoInc = limpiarDato($(this).data("estado"));
        const nombreInc = limpiarDato($(this).data("nombre"));
        const fechaInc = limpiarDato($(this).data("fecha"));
        const observacionInc = limpiarDato($(this).data("observacion"));

        // Rellenar los campos del formulario modal
        $("#edit_idEquipo").val(idEquipoInc);
        $("#form_edit_incidencia").attr("action", `/incidencia/update_incidencia/${idEquipoInc}`);
        $("#edit_estadoIncidencia").val(estadoInc);
        $("#edit_nombreIncidencia").val(nombreInc);
        $("#edit_fechaIncidencia").val(fechaInc);
        $("#edit_observacionIncidencia").val(observacionInc);

        // Bloquear el campo "Estado Incidencia" si el estado actual es Cerrado, Equipo cambiado o Equipo reparado
        const estadosBloqueados = ["cerrado", "equipo cambiado", "equipo reparado"];
        if (estadosBloqueados.includes(estadoInc.toLowerCase())) {
            $("#edit_estadoIncidencia").prop("disabled", true);
            $("#edit_nombreIncidencia").prop("disabled", true);
            $("#edit_fechaIncidencia").prop("disabled", true);
            $("#edit_observacionIncidencia").prop("disabled", true);
        } else {
            $("#edit_estadoIncidencia").prop("disabled", false);
            $("#edit_nombreIncidencia").prop("disabled", false);
            $("#edit_fechaIncidencia").prop("disabled", false);
            $("#edit_observacionIncidencia").prop("disabled", false);
        }

        console.log("Editando incidencia ID:", idEquipoInc);
    });

    let nuevoEstadoSeleccionado = ""; // Variable para almacenar el estado seleccionado

    // ✅ Listener para detectar cambios en el estado de la incidencia
    $("#edit_estadoIncidencia").on("change", function () {
        nuevoEstadoSeleccionado = $(this).val(); // Obtener el nuevo estado seleccionado
        const estadosConfirmacion = ["cerrado", "equipo cambiado", "equipo reparado"];

        if (estadosConfirmacion.includes(nuevoEstadoSeleccionado.toLowerCase())) {
            // Actualizar el mensaje del modal con el estado seleccionado
            $("#confirmStateMessage").text(
                `¿Estás seguro de que deseas cambiar el estado a "${nuevoEstadoSeleccionado}"? Luego no podrás modificarlo.`
            );

            // Mostrar el modal de confirmación
            $("#confirmStateChangeModal").modal("show");
        } else {
            // Guardar el estado anterior si no requiere confirmación
            $(this).data("estado-anterior", nuevoEstadoSeleccionado);
        }
    });

    // ✅ Confirmar el cambio de estado desde el modal
    $("#confirmStateBtn").on("click", function () {
        // Guardar el estado seleccionado como el nuevo estado
        $("#edit_estadoIncidencia").data("estado-anterior", nuevoEstadoSeleccionado);

        // Cerrar el modal
        $("#confirmStateChangeModal").modal("hide");

        console.log("Estado confirmado:", nuevoEstadoSeleccionado);
    });

    // ✅ Cancelar el cambio de estado desde el modal
    $("#confirmStateChangeModal").on("hidden.bs.modal", function () {
        // Revertir el cambio si el usuario cierra el modal sin confirmar
        const estadoAnterior = $("#edit_estadoIncidencia").data("estado-anterior");
        $("#edit_estadoIncidencia").val(estadoAnterior);
    });

    // ✅ Evento para eliminar incidencia (elimina la incidencia correcta)
    let incidenciaIdToDelete = null;
    let deleteUrl = null;

    // Capturar el ID de la incidencia al abrir el modal
    $(document).on("click", ".delete-button", function () {
        incidenciaIdToDelete = $(this).data("id");
        deleteUrl = $(this).data("url");

        console.log("Incidencia seleccionada para eliminar:", incidenciaIdToDelete);
    });

    // Manejar la confirmación de eliminación
    $(document).on("click", "#confirmDeleteButton", function () {
        if (deleteUrl) {
            // Crear un formulario dinámico para enviar la solicitud de eliminación
            let form = $("<form>", {
                method: "POST",
                action: deleteUrl
            }).appendTo("body");

            form.submit(); // Enviar el formulario
        }
    });

    // ✅ Función para limpiar datos antes de usarlos
    function limpiarDato(dato) {
        return dato ? dato.toString().trim() : "";
    }


    document.getElementById("form_add_incidencia").addEventListener("submit", function (event) {
        const selectedCheckbox = document.querySelector(".equipo-checkbox:checked");
        if (!selectedCheckbox) {
            event.preventDefault(); // Evita el envío del formulario
            alert("Por favor, selecciona un equipo.");
        } else {
            // Asigna el valor del checkbox seleccionado al campo oculto
            document.getElementById("idEquipo").value = selectedCheckbox.value;
        }
    });

});