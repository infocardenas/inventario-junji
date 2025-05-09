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