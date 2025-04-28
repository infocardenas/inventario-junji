$(document).ready(function () {
    // Variables para gestionar el estado del select de incidencia durante la edición
    let originalEstadoIncidencia = ''; // Guarda el estado cuando el modal se abre por primera vez
    let estadoAntesDelCambio = '';   // Guarda el estado justo antes de seleccionar una opción que requiere confirmación

    // ✅ Evento para editar incidencia (Abrir modal con datos correctos)
    $(".edit-equipo-btn").on("click", function () {
        const idEquipoInc = limpiarDato($(this).data("id"));
        const estadoInc = limpiarDato($(this).data("estado"));
        const nombreInc = limpiarDato($(this).data("nombre"));
        const fechaInc = limpiarDato($(this).data("fecha"));
        const observacionInc = limpiarDato($(this).data("observacion"));

        // Guardar el estado inicial en las variables cuando el modal se abre
        originalEstadoIncidencia = estadoInc;
        estadoAntesDelCambio = estadoInc; // Inicializar con el estado original

        // Rellenar los campos del formulario modal
        $("#edit_idEquipo").val(idEquipoInc);
        $("#form_edit_incidencia").attr("action", `/incidencia/update_incidencia/${idEquipoInc}`);
        $("#edit_estadoIncidencia").val(estadoInc);
        // Guardar estado inicial también en data-attribute por si se usa en otro lado
        $("#edit_estadoIncidencia").data("estado-anterior", estadoInc);
        $("#edit_nombreIncidencia").val(nombreInc);
        $("#edit_fechaIncidencia").val(fechaInc);
        $("#edit_observacionIncidencia").val(observacionInc);

        // --- Importante: Resetear estado enabled/disabled ---
        // Asegurarse de que los campos estén habilitados por defecto al abrir
        $("#edit_estadoIncidencia").prop("disabled", false);
        $("#edit_nombreIncidencia").prop("disabled", false);
        $("#edit_fechaIncidencia").prop("disabled", false);
        $("#edit_observacionIncidencia").prop("disabled", false);
        // Habilitar también el botón de guardar por si se deshabilitó antes
        $('#form_edit_incidencia button[type="submit"]').prop('disabled', false);


        // Bloquear campos si el estado INICIAL ya es uno de los finales
        const estadosBloqueados = ["cerrado", "equipo cambiado", "equipo reparado"];
        if (estadosBloqueados.includes(estadoInc.toLowerCase())) {
            console.log("Estado inicial es final. Deshabilitando campos.");
            $("#edit_estadoIncidencia").prop("disabled", true);
            $("#edit_nombreIncidencia").prop("disabled", true);
            $("#edit_fechaIncidencia").prop("disabled", true);
            $("#edit_observacionIncidencia").prop("disabled", true);
        }

        console.log("Editando incidencia ID:", idEquipoInc, "Estado inicial:", estadoInc);
        // Asegúrate de que el modal de edición se muestre (si no se hace automáticamente)
        // $('#edit_incidencia').modal('show'); // Descomentar si es necesario
    });

    // Variable para almacenar temporalmente el estado que necesita confirmación
    let nuevoEstadoSeleccionadoPendiente = "";

    // ✅ Listener para detectar cambios en el estado de la incidencia
    $("#edit_estadoIncidencia").on("change", function () {
        const estadoActual = $(this).val(); // El nuevo valor que el usuario seleccionó

        // 'estadoAntesDelCambio' todavía tiene el valor ANTES de que este evento 'change' ocurriera

        console.log(`Cambio detectado. Antes: "${estadoAntesDelCambio}", Ahora: "${estadoActual}"`);

        const estadosConfirmacion = ["cerrado", "equipo cambiado", "equipo reparado"];

        if (estadosConfirmacion.includes(estadoActual.toLowerCase())) {
            // El nuevo estado requiere confirmación
            nuevoEstadoSeleccionadoPendiente = estadoActual; // Guardar temporalmente

            // Actualizar el mensaje del modal de confirmación
            $("#confirmStateMessage").text(
                `¿Estás seguro de que deseas cambiar el estado a "${nuevoEstadoSeleccionadoPendiente}"? Una vez confirmado, no podrás modificar la incidencia.`
            );

            // Mostrar el modal de confirmación
            // IMPORTANTE: No actualizamos 'estadoAntesDelCambio' todavía.
            $("#confirmStateChangeModal").modal("show");

        } else {
            // El cambio no necesita confirmación, así que lo aceptamos directamente.
            // Actualizamos 'estadoAntesDelCambio' para que refleje este nuevo estado aceptado.
            estadoAntesDelCambio = estadoActual;
            // Opcional: actualizar data-attribute si se usa en otro lado
            // $(this).data("estado-anterior", estadoActual);
            console.log(`Cambio sin confirmación. Nuevo 'estadoAntesDelCambio' es: "${estadoAntesDelCambio}"`);
        }
    });

    // ✅ Confirmar el cambio de estado desde el modal de confirmación
    $("#confirmStateBtn").on("click", function () {
        // El usuario ha confirmado el cambio al estado que estaba pendiente
        console.log("Confirmado cambio a:", nuevoEstadoSeleccionadoPendiente);

        // Actualizar 'estadoAntesDelCambio' para que refleje el estado recién confirmado.
        // Ahora este es el estado estable actual.
        estadoAntesDelCambio = nuevoEstadoSeleccionadoPendiente;
        // Opcional: actualizar data-attribute
        $("#edit_estadoIncidencia").data("estado-anterior", estadoAntesDelCambio);


        // Cerrar el modal de confirmación
        $("#confirmStateChangeModal").modal("hide");

        // Deshabilitar los campos AHORA que el estado final está confirmado
        const estadosBloqueados = ["cerrado", "equipo cambiado", "equipo reparado"];
        if (estadosBloqueados.includes(estadoAntesDelCambio.toLowerCase())) { // Usar estadoAntesDelCambio que ya tiene el valor confirmado
             console.log("Campos deshabilitados tras confirmar estado final.");
            $("#edit_estadoIncidencia").prop("disabled", true);
            $("#edit_nombreIncidencia").prop("disabled", true);
            $("#edit_fechaIncidencia").prop("disabled", true);
            $("#edit_observacionIncidencia").prop("disabled", true);
        }

        // No necesitamos cambiar el valor del select aquí, porque el usuario ya lo cambió
        // y la acción de confirmar simplemente acepta ese cambio.
    });

    // ✅ Gestionar cancelación/cierre del modal de confirmación (cuando se OCULTA)
    $("#confirmStateChangeModal").on("hidden.bs.modal", function (event) {
        // Este evento se dispara SIEMPRE que el modal se oculta (Confirmar, Cancelar, 'X', ESC, click fuera)

        // Comprobamos si el valor actual del select es DIFERENTE al último estado estable ('estadoAntesDelCambio')
        // Si son diferentes, significa que el usuario seleccionó una opción que requería confirmación,
        // pero CERRÓ el modal SIN hacer clic en "Confirmar".
        if ($("#edit_estadoIncidencia").val() !== estadoAntesDelCambio) {
            console.log(`Modal de confirmación cerrado sin confirmar explícitamente. Revertir a: "${estadoAntesDelCambio}"`);

            // Revertir el valor del select al estado que tenía ANTES de seleccionar la opción problemática.
            $("#edit_estadoIncidencia").val(estadoAntesDelCambio);

            // Asegurarse de que los campos y el botón Guardar estén habilitados si revertimos desde un estado final potencial
            const estadosBloqueados = ["cerrado", "equipo cambiado", "equipo reparado"];
             if (!estadosBloqueados.includes(estadoAntesDelCambio.toLowerCase())) {
                  $("#edit_estadoIncidencia").prop("disabled", false);
                  $("#edit_nombreIncidencia").prop("disabled", false);
                  $("#edit_fechaIncidencia").prop("disabled", false);
                  $("#edit_observacionIncidencia").prop("disabled", false);
                  $('#form_edit_incidencia button[type="submit"]').prop('disabled', false);
                  console.log("Campos y botón Guardar re-habilitados al cancelar cambio a estado final.");
             }

        } else {
             // Si son iguales, significa que el modal se cerró DESPUÉS de hacer clic en "Confirmar"
             // (porque el botón "Confirmar" ya actualizó 'estadoAntesDelCambio') o que no hubo cambio pendiente.
             console.log("Modal de confirmación cerrado después de confirmar o sin cambio pendiente.");
             // No necesitamos hacer nada aquí.
        }
        // Limpiar el estado pendiente por si acaso
        nuevoEstadoSeleccionadoPendiente = "";
    });


    // --- Resto de tu código ---

    // ✅ Evento para eliminar incidencia (parece correcto)
    let incidenciaIdToDelete = null;
    let deleteUrl = null;
    $(document).on("click", ".delete-button", function () {
        incidenciaIdToDelete = $(this).data("id");
        deleteUrl = $(this).data("url");
        console.log("Incidencia seleccionada para eliminar:", incidenciaIdToDelete);
    });
    $(document).on("click", "#confirmDeleteButton", function () {
        if (deleteUrl) {
            let form = $("<form>", { method: "POST", action: deleteUrl }).appendTo("body");
            form.submit();
        }
    });

    // ✅ Función para limpiar datos (parece correcta)
    function limpiarDato(dato) {
        return dato ? dato.toString().trim() : "";
    }

// ✅ Evento para abrir el modal de añadir incidencia
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

// Búsqueda dinámica
document.getElementById('searchEquipo').addEventListener('input', function () {
    const filter = this.value.toLowerCase();
    const rows = document.querySelectorAll('#equiposTable tr');

    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
    });
});

});