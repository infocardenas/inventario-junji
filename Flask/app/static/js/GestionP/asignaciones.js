let debounceTimeout;

function buscarAsignaciones(page = 1) {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
        const query = document.getElementById("buscador_asignaciones").value.toLowerCase();

        fetch(`/buscar_asignaciones?q=${encodeURIComponent(query)}&page=${page}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Error al buscar asignaciones");
                }
                return response.json();
            })
            .then(data => {
                actualizarTablaAsignaciones(data.asignaciones); // Actualizar la tabla con los datos recibidos
                actualizarPaginacion(data.total_pages, data.current_page, query); // Actualizar la paginación
            })
            .catch(error => console.error("Error al buscar asignaciones:", error));
    }, 300); // Retraso de 300ms para evitar múltiples solicitudes
}

function actualizarTablaAsignaciones(asignaciones) {
    const tbody = document.getElementById("myTableBody");
    tbody.innerHTML = ""; // Limpiar la tabla

    if (asignaciones.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">No hay datos disponibles.</td></tr>';
        return;
    }

    asignaciones.forEach(asig => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>
                <input type="checkbox" class="checkbox-table row-checkbox no-delete-value"
                  value="${asig.idEquipoAsignacion || ''}"
                  data-id-devolucion="${asig.idDevolucion || ''}"
                  data-id-asignacion="${asig.idAsignacion || ''}"
                  data-devuelto="${asig.fechaDevolucion ? 'true' : 'false'}">
            </td>
            <td class="toCheck">${asig.idAsignacion || '-'}</td>
            <td class="toCheck">${asig.nombreFuncionario || '-'}</td>
            <td class="toCheck">${asig.nombreTipo_equipo || '-'}</td>
            <td class="toCheck">${formatFecha(asig.fecha_inicioAsignacion)}</td>
            <td class="toCheck">${asig.fechaDevolucion ? formatFecha(asig.fechaDevolucion) : 'Sin devolver'}</td>
            <td class="d-flex justify-content-center gap-2">
                <div data-bs-toggle="tooltip" data-bs-title="Detalles">
                  <button class="btn button-info" data-bs-toggle="modal"
                    data-bs-target="#modal-view-${asig.idEquipoAsignacion}">
                    <i class="bi bi-info-circle"></i>
                  </button>
                </div>
                <button class="btn btn-danger delete-button" data-bs-toggle="tooltip"
                  data-url="/delete_asignacion/${asig.idAsignacion}"
                  data-title="Confirmar eliminación de asignación"
                  data-message="¿Estás seguro de que deseas eliminar esta asignación? Eliminar la asignación descartará los equipos asociados a este ID de asignación."
                  data-bs-title="Eliminar">
                  <i class="bi bi-trash-fill"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function formatFecha(fecha) {
    if (!fecha) return '-';
    try {
        return new Date(fecha).toLocaleDateString();
    } catch (error) {
        console.error("Fecha inválida:", fecha);
        return "Fecha inválida";
    }
}


function abrirModalFirmarAsignacion() {
    const modalFirmarAsignacion = new bootstrap.Modal(document.getElementById("modalFirmarAsignacion"));
    let idSeleccionado = null;

    // Capturar el ID del ítem seleccionado
    document.querySelectorAll(".row-checkbox").forEach(checkbox => {
        if (checkbox.checked) {
            idSeleccionado = checkbox.getAttribute("data-id-asignacion");
        }
    });

    if (!idSeleccionado) {
        alert("Por favor, selecciona un ítem antes de continuar.");
        return;
    }

    // Mostrar el ID en el modal
    const idSpan = document.getElementById("idAsignacionSeleccionada");
    idSpan.textContent = idSeleccionado;

    const form = document.getElementById("formSubirFirma");
    form.action = `/asignacion/adjuntar_pdf/${idSeleccionado}`;
    form.reset(); // Limpiar el formulario antes de abrir el modal
    // Abrir el modal
    modalFirmarAsignacion.show();
    // Obtener detalles y mostrarlos
    fetch(`/asignacion/detalles_json/${idSeleccionado}`)
        .then(res => res.json())
        .then(data => {
            const d = data.asignacion;

            document.getElementById("detalleID").textContent = d.idAsignacion;
            document.getElementById("rutFuncionario").textContent = d.rutFuncionario;
            document.getElementById("nombreFuncionario").textContent = d.nombreFuncionario;
            document.getElementById("cargoFuncionario").textContent = d.cargoFuncionario;

            document.getElementById("fechaAsignacion").textContent = formatFecha(d.fecha_inicioAsignacion);
            document.getElementById("fechaDevolucion").textContent = d.fechaDevolucion ? formatFecha(d.fechaDevolucion) : "Sin devolver";
            document.getElementById("observacionesAsignacion").textContent = d.ObservacionAsignacion || "-";

            document.getElementById("tipoEquipo").textContent = d.nombreTipo_equipo;
            document.getElementById("marcaEquipo").textContent = d.nombreMarcaEquipo;
            document.getElementById("modeloEquipo").textContent = d.nombreModeloequipo;
            document.getElementById("codigoInventario").textContent = d.Cod_inventarioEquipo;
            document.getElementById("numeroSerie").textContent = d.Num_serieEquipo;
            document.getElementById("codigoProveedor").textContent = d.codigoproveedor_equipo || "No informado";
            document.getElementById("observacionesEquipo").textContent = d.ObservacionEquipo || "-";
        });

    // Limpiar contenido anterior
    const tbody = document.getElementById("tablaFirmasBody");

    tbody.innerHTML = `<tr><td colspan="2" class="text-center">Buscando archivo...</td></tr>`;

    fetch(`/asignacion/firmas_json/${idSeleccionado}`)
        .then(res => res.json())
        .then(data => {
            tbody.innerHTML = ""; // Limpiar

            if (data.existe) {
                const fila = document.createElement("tr");
                fila.innerHTML = `
                <td>${data.nombre}</td>
                <td><a href="/asignacion/mostrar_pdf/${idSeleccionado}/" class="btn btn-primary info-button" target="_blank">Abrir</a></td>
            `;
                tbody.appendChild(fila);
            } else {
                const fila = document.createElement("tr");
                fila.innerHTML = `<td colspan="2" class="text-center">No existen firmas para este documento</td>`;
                tbody.appendChild(fila);
            }
        });

}

function abrirModalFirmarDevolucion() {
    const modal = new bootstrap.Modal(document.getElementById("modalFirmarDevolucion"));
    let idAsignacion = null;

    document.querySelectorAll(".row-checkbox").forEach(checkbox => {
        if (checkbox.checked) {
            idAsignacion = checkbox.getAttribute("data-id-asignacion");
        }
    });

    if (!idAsignacion) {
        alert("Por favor, selecciona un ítem antes de continuar.");
        return;
    }

    // Mostrar el ID
    document.getElementById("detalleIDDevolucion").textContent = idAsignacion;

    // Configurar formulario
    const form = document.getElementById("formSubirFirmaDevolucion");
    form.action = `/devolucion/adjuntar_pdf/${idAsignacion}`;
    form.reset();

    // Mostrar modal
    modal.show();

    // Cargar detalles
    fetch(`/asignacion/detalles_json/${idAsignacion}`)
        .then(res => res.json())
        .then(data => {
            const d = data.asignacion;

            document.getElementById("rutFuncionarioDevolucion").textContent = d.rutFuncionario;
            document.getElementById("nombreFuncionarioDevolucion").textContent = d.nombreFuncionario;
            document.getElementById("cargoFuncionarioDevolucion").textContent = d.cargoFuncionario;

            document.getElementById("fechaAsignacionDevolucion").textContent = formatFecha(d.fecha_inicioAsignacion);
            document.getElementById("fechaDevolucionDevolucion").textContent = d.fechaDevolucion ? formatFecha(d.fechaDevolucion) : "Sin devolver";
            document.getElementById("observacionesDevolucion").textContent = d.ObservacionAsignacion || "-";

            document.getElementById("tipoEquipoDevolucion").textContent = d.nombreTipo_equipo;
            document.getElementById("marcaEquipoDevolucion").textContent = d.nombreMarcaEquipo;
            document.getElementById("modeloEquipoDevolucion").textContent = d.nombreModeloequipo;
            document.getElementById("codigoInventarioDevolucion").textContent = d.Cod_inventarioEquipo;
            document.getElementById("numeroSerieDevolucion").textContent = d.Num_serieEquipo;
            document.getElementById("codigoProveedorDevolucion").textContent = d.codigoproveedor_equipo || "No informado";
            document.getElementById("observacionesEquipoDevolucion").textContent = d.ObservacionEquipo || "-";
        });

    // Cargar archivo ya subido (si existe)
    const tbody = document.getElementById("tablaFirmasBodyDevolucion");
    tbody.innerHTML = `<tr><td colspan="2" class="text-center">Buscando archivo...</td></tr>`;

    fetch(`/asignacion/firmas_devolucion_json/${idAsignacion}`)
        .then(res => res.json())
        .then(data => {
            tbody.innerHTML = "";
            if (data.existe) {
                tbody.innerHTML = `
                    <td>${data.nombre}</td>
                    <td><a href="/devolucion/mostrar_pdf/${idAsignacion}/" class="btn btn-primary info-button" target="_blank">Abrir</a></td>
                `;
            } else {
                tbody.innerHTML = `<tr><td colspan="2" class="text-center">No existen firmas para esta devolución</td></tr>`;
            }
        });
}
