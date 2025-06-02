$(document).ready(function () {
    let estadoAntesDelCambio = '';   // Guarda el estado justo antes de seleccionar una opción que requiere confirmación

    $(document).on("click", ".edit-equipo-btn", function () {
        const idEquipoInc = limpiarDato($(this).data("id"));
        const estadoInc = limpiarDato($(this).data("estado"));
        const nombreInc = limpiarDato($(this).data("nombre"));
        const fechaInc = limpiarDato($(this).data("fecha"));
        const observacionInc = limpiarDato($(this).data("observacion"));

        // Convertir la fecha al formato YYYY-MM-DD
        const fechaFormateada = new Date(fechaInc).toISOString().split("T")[0];

        // Rellenar los campos del formulario modal
        $("#edit_idEquipo").val(idEquipoInc);
        $("#form_edit_incidencia").attr("action", `/incidencia/update_incidencia/${idEquipoInc}`);
        $("#edit_estadoIncidencia").val(estadoInc);
        $("#edit_nombreIncidencia").val(nombreInc);
        $("#edit_fechaIncidencia").val(fechaFormateada);
        $("#edit_observacionIncidencia").val(observacionInc);

        // Resetear estado enabled/disabled
        $("#edit_estadoIncidencia").prop("disabled", false);
        $("#edit_nombreIncidencia").prop("disabled", false);
        $("#edit_fechaIncidencia").prop("disabled", false);
        $("#edit_observacionIncidencia").prop("disabled", false);
        $('#form_edit_incidencia button[type="submit"]').prop('disabled', false);

        // Bloquear campos si el estado inicial ya es uno de los finales
        const estadosBloqueados = ["cerrado", "equipo cambiado", "equipo reparado"];
        if (estadosBloqueados.includes(estadoInc.toLowerCase())) {
            console.log("Estado inicial es final. Deshabilitando campos.");
            $("#edit_estadoIncidencia").prop("disabled", true);
            $("#edit_nombreIncidencia").prop("disabled", true);
            $("#edit_fechaIncidencia").prop("disabled", true);
            $("#edit_observacionIncidencia").prop("disabled", true);
        }

        console.log("Editando incidencia ID:", idEquipoInc, "Estado inicial:", estadoInc);
    });

    // Variable para almacenar temporalmente el estado que necesita confirmación
    let nuevoEstadoSeleccionadoPendiente = "";

    // ✅ Listener para detectar cambios en el estado de la incidencia
    $("#edit_estadoIncidencia").on("change", function () {
        const estadoActual = $(this).val(); // El nuevo valor que el usuario seleccionó
        console.log(`Cambio detectado. Antes: "${estadoAntesDelCambio}", Ahora: "${estadoActual}"`);
        const estadosConfirmacion = ["cerrado", "equipo cambiado", "equipo reparado"];

        if (estadosConfirmacion.includes(estadoActual.toLowerCase())) {
            // El nuevo estado requiere confirmación
            nuevoEstadoSeleccionadoPendiente = estadoActual; // Guardar temporalmente

            // Actualizar el mensaje del modal de confirmación
            $("#confirmStateMessage").text(
                `¿Estás seguro de que deseas cambiar el estado a "${nuevoEstadoSeleccionadoPendiente}"? Una vez confirmado, no podrás modificar la incidencia.`
            );
            $("#confirmStateChangeModal").modal("show");

        } else {
            estadoAntesDelCambio = estadoActual;
            console.log(`Cambio sin confirmación. Nuevo 'estadoAntesDelCambio' es: "${estadoAntesDelCambio}"`);
        }
    });

    // ✅ Confirmar el cambio de estado desde el modal de confirmación
    $("#confirmStateBtn").on("click", function () {
        // El usuario ha confirmado el cambio al estado que estaba pendiente
        console.log("Confirmado cambio a:", nuevoEstadoSeleccionadoPendiente);
        estadoAntesDelCambio = nuevoEstadoSeleccionadoPendiente;
        $("#edit_estadoIncidencia").data("estado-anterior", estadoAntesDelCambio);
        $("#confirmStateChangeModal").modal("hide");

    });
    $("#confirmStateChangeModal").on("hidden.bs.modal", function (event) {
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
            console.log("Modal de confirmación cerrado después de confirmar o sin cambio pendiente.");
        }
        // Limpiar el estado pendiente por si acaso
        nuevoEstadoSeleccionadoPendiente = "";
    });

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

    let debounceTimeout;
    document.getElementById("buscador_incidencia").addEventListener("input", () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => buscarIncidencias(1), 300);
    });

    function buscarIncidencias(page = 1) {
        const query = document.getElementById("buscador_incidencia").value.toLowerCase(); // Obtener el término de búsqueda

        fetch(`/buscar_incidencias?q=${encodeURIComponent(query)}&page=${page}`) // Realizar la solicitud al backend
            .then(response => {
                if (!response.ok) {
                    throw new Error("Error al buscar incidencias");
                }
                return response.json();
            })
            .then(data => {
                actualizarTabla(data.incidencias); // Actualizar la tabla con los datos recibidos
                actualizarPaginacion(data.total_pages, data.current_page, query); // Actualizar la paginación
            })
            .catch(error => console.error("Error al buscar incidencias:", error));
    }

    function actualizarTabla(incidencias) {
        const tbody = document.getElementById("myTableBody");
        tbody.innerHTML = ""; // Limpiar la tabla

        if (incidencias.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" class="text-center">No hay datos disponibles.</td></tr>';
            return;
        }

        incidencias.forEach(inc => {
            const row = document.createElement("tr");
            row.setAttribute("data-id", inc.idIncidencia);
            row.innerHTML = `
            <td>${inc.estadoIncidencia}</td>
            <td>${inc.nombreTipo_equipo}</td>
            <td>${inc.nombreIncidencia}</td>
            <td>${inc.observacionIncidencia || '-'}</td>
            <td>${new Date(inc.fechaIncidencia).toLocaleDateString()}</td>
            <td>${inc.cod_inventarioEquipo}</td>
            <td>${inc.Num_serieEquipo}</td>
            <td>${inc.nombreModeloequipo}</td>
            <td>
                <a href="/incidencia/listar_pdf/${inc.idIncidencia}" class="btn button-info">
                    <i class="bi bi-info-circle"></i>
                </a>
                <button class="btn btn-warning edit-equipo-btn" data-bs-toggle="modal"
                    data-bs-target="#edit_incidencia" data-id="${inc.idIncidencia}"
                    data-estado="${inc.estadoIncidencia}" data-nombre="${inc.nombreIncidencia}"
                    data-fecha="${inc.fechaIncidencia}" data-observacion="${inc.observacionIncidencia}">
                    <i class="bi bi-pencil-square"></i>
                </button>
                <button class="btn btn-danger delete-button" data-bs-toggle="modal"
                    data-bs-target="#deleteModal" data-id="${inc.idIncidencia}"
                    data-url="/incidencia/delete_incidencia/${inc.idIncidencia}">
                    <i class="bi bi-trash-fill"></i>
                </button>
            </td>
        `;
            tbody.appendChild(row);
        });
    }

});