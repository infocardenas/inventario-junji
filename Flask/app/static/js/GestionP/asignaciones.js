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
                // actualizarPaginacion(data.total_pages, data.current_page, query); // Actualizar la paginación (comentado porque no está definida)
            })
            .catch(error => console.error("Error al buscar asignaciones:", error));
    }, 300); // Retraso de 300ms para evitar múltiples solicitudes
}

function actualizarTablaAsignaciones(asignaciones) {
    const tbody = document.getElementById("myTableBody");
    tbody.innerHTML = ""; // Limpiar la tabla

    if (asignaciones.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">No hay datos disponibles.</td></tr>';
        actualizarBotonesBarraSuperior();
        return;
    }

    asignaciones.forEach(asig => {
        const row = document.createElement("tr");
        row.setAttribute('data-marca-equipo', asig.nombreMarcaEquipo || '');
        row.setAttribute('data-modelo-equipo', asig.nombreModeloequipo || '');
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
                  <button class="btn button-info"
                    data-id-asignacion="${asig.idAsignacion}">
                    <i class="bi bi-info-circle"></i>
                  </button>
                </div>
                <button class="btn btn-danger delete-button" data-bs-toggle="tooltip"
                  data-url="/delete_asignacion/${asig.idAsignacion}"
                  data-title="Confirmar eliminación de asignación"
                  data-message="¿Estás seguro de que deseas eliminar esta asignación? Eliminar la asignación descartará los equipos asociados a este ID de asignación."
                  data-bs-title="Eliminar" data-id-asignacion="${asig.idAsignacion}">
                  <i class="bi bi-trash-fill"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });

    // Vuelve a enlazar los eventos para los checkboxes
    rebindCheckboxEvents();

    // Llama a la función para actualizar el estado de los botones después de actualizar la tabla
    actualizarBotonesBarraSuperior();
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

// Evento para abrir el modal de devolución y poblarlo con los equipos seleccionados
document.addEventListener('DOMContentLoaded', function () {
    const devolverButton = document.getElementById('devolver-button');
    const modalEl = document.getElementById('modalConfirmarDevolucion');
    const tbody = document.getElementById('tbodyDevolucionSeleccionados');
    const form = document.getElementById('formDevolver');

    if (devolverButton && modalEl && tbody && form) {
        devolverButton.addEventListener('click', function () {
            // Obtener todos los checkboxes seleccionados
            const seleccionados = Array.from(document.querySelectorAll('.row-checkbox:checked'));

            // Limpiar el tbody y los inputs ocultos previos
            tbody.innerHTML = '';
            Array.from(form.querySelectorAll('input[name="equiposSeleccionados"]')).forEach(input => input.remove());

            if (seleccionados.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">No hay equipos seleccionados.</td></tr>';
            } else {
                seleccionados.forEach(checkbox => {
                    const row = checkbox.closest('tr');
                    if (!row) return;
                    const cells = row.querySelectorAll('td');
                    // Extraer datos del tr (marca/modelo) y celdas
                    const marcaEquipo = row.getAttribute('data-marca-equipo') || '';
                    const modeloEquipo = row.getAttribute('data-modelo-equipo') || '';
                    const idAsignacion = cells[1]?.textContent || '';
                    const funcionario = cells[2]?.textContent || '';
                    const tipoEquipo = cells[3]?.textContent || '';
                    // Puedes ajustar el índice de celdas si tu tabla cambia
                    const codInventario = cells[5]?.textContent || '';

                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${idAsignacion}</td>
                        <td>${funcionario}</td>
                        <td>${tipoEquipo}</td>
                        <td>${marcaEquipo}</td>
                        <td>${modeloEquipo}</td>
                        <td>${codInventario}</td>
                    `;
                    tbody.appendChild(tr);

                    // Crea el input oculto para enviar el idEquipoAsignacion
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'equiposSeleccionados';
                    input.value = checkbox.value;
                    form.appendChild(input);
                });
            }

            // Mostrar el modal correctamente (sin bloquear)
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            modal.show();
        });

        // Limpiar el modal al cerrarse y eliminar backdrop si queda
        modalEl.addEventListener('hidden.bs.modal', function () {
            tbody.innerHTML = '';
            Array.from(form.querySelectorAll('input[name="equiposSeleccionados"]')).forEach(input => input.remove());
            // Limpieza manual del backdrop si quedara alguno
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
        });
    }
});

function actualizarBotonesBarraSuperior() {
    // Actualizar enlaces de descarga PDF según el seleccionado
    const descargarAsignacion = document.getElementById("descargar-asignacion");
    const descargarDevolucion = document.getElementById("descargar-devolucion");
    const firmarButton = document.getElementById("firmar-button");
    const devolverButton = document.getElementById("devolver-button");
    const descargarPDFButton = document.getElementById("descargar-PDF-button");
    // Siempre obtener los botones de firma del dropdown
    const btnFirmarAsignacion = document.getElementById("documento-firmado-asignacion");
    const btnFirmarDevolucion = document.getElementById("documento-firmado-devolucion");

    // Siempre dejar los botones de firma activos (no bloqueados)
    if (btnFirmarAsignacion) {
        btnFirmarAsignacion.disabled = false;
        btnFirmarAsignacion.classList.remove('disabled');
        btnFirmarAsignacion.tabIndex = 0;
        btnFirmarAsignacion.style.pointerEvents = 'auto';
    }
    if (btnFirmarDevolucion) {
        btnFirmarDevolucion.disabled = false;
        btnFirmarDevolucion.classList.remove('disabled');
        btnFirmarDevolucion.tabIndex = 0;
        btnFirmarDevolucion.style.pointerEvents = 'auto';
    }

    // Buscar el primer checkbox seleccionado
    const checked = document.querySelector('.row-checkbox:checked');
    const haySeleccion = !!checked;

    if (firmarButton) firmarButton.disabled = !haySeleccion;
    if (devolverButton) devolverButton.disabled = !haySeleccion;
    if (descargarPDFButton) descargarPDFButton.disabled = !haySeleccion;

    // Habilitar los botones del dropdown de firma SOLO si hay selección
    if (btnFirmarAsignacion) btnFirmarAsignacion.disabled = !haySeleccion;
    if (btnFirmarDevolucion) btnFirmarDevolucion.disabled = !haySeleccion;

    if (haySeleccion) {
        const idAsignacion = checked.getAttribute('data-id-asignacion');
        const idDevolucion = checked.getAttribute('data-id-devolucion');
        if (descargarAsignacion) {
            descargarAsignacion.href = `/asignacion/descargar_pdf_asignacion/${idAsignacion}`;
            descargarAsignacion.classList.remove('disabled');
            descargarAsignacion.removeAttribute('aria-disabled');
        }
        if (descargarDevolucion) {
            if (idDevolucion) {
                descargarDevolucion.href = `/asignacion/descargar_pdf_devolucion/${idDevolucion}`;
                descargarDevolucion.classList.remove('disabled');
                descargarDevolucion.removeAttribute('aria-disabled');
            } else {
                descargarDevolucion.href = "#";
                descargarDevolucion.classList.add('disabled');
                descargarDevolucion.setAttribute('aria-disabled', 'true');
            }
        }
    } else {
        if (descargarAsignacion) {
            descargarAsignacion.href = "#";
            descargarAsignacion.classList.add('disabled');
            descargarAsignacion.setAttribute('aria-disabled', 'true');
        }
        if (descargarDevolucion) {
            descargarDevolucion.href = "#";
            descargarDevolucion.classList.add('disabled');
            descargarDevolucion.setAttribute('aria-disabled', 'true');
        }
    }
}

// Actualizar los enlaces de descarga y botones cada vez que se selecciona un checkbox
document.addEventListener('change', function (e) {
    if (e.target.classList.contains('row-checkbox')) {
        actualizarBotonesBarraSuperior();
    }
});

// También actualizar al cargar la tabla por primera vez
document.addEventListener('DOMContentLoaded', function () {
    actualizarBotonesBarraSuperior();
    rebindCheckboxEvents();
    // Descargar PDF dinámicamente según selección
    const descargarAsignacion = document.getElementById("descargar-asignacion");
    const descargarDevolucion = document.getElementById("descargar-devolucion");

    if (descargarAsignacion) {
        descargarAsignacion.addEventListener('click', function (e) {
            if (descargarAsignacion.classList.contains('disabled')) {
                e.preventDefault();
                return;
            }
            const checked = document.querySelector('.row-checkbox:checked');
            if (!checked) {
                e.preventDefault();
                alert("Selecciona una asignación para descargar el PDF.");
                return;
            }
            const idAsignacion = checked.getAttribute('data-id-asignacion');
            if (idAsignacion) {
                descargarAsignacion.href = `/asignacion/descargar_pdf_asignacion/${idAsignacion}`;
            } else {
                e.preventDefault();
                alert("No se encontró el ID de asignación.");
            }
        });
    }

    if (descargarDevolucion) {
        descargarDevolucion.addEventListener('click', function (e) {
            if (descargarDevolucion.classList.contains('disabled')) {
                e.preventDefault();
                return;
            }
            const checked = document.querySelector('.row-checkbox:checked');
            if (!checked) {
                e.preventDefault();
                alert("Selecciona una asignación para descargar el PDF de devolución.");
                return;
            }
            const idDevolucion = checked.getAttribute('data-id-devolucion');
            if (idDevolucion) {
                descargarDevolucion.href = `/asignacion/descargar_pdf_devolucion/${idDevolucion}`;
            } else {
                e.preventDefault();
                alert("No se encontró el ID de devolución para esta asignación.");
            }
        });
    }
});

// Asegura que los eventos de los checkboxes funcionen después de buscar
function rebindCheckboxEvents() {
    document.querySelectorAll('.row-checkbox').forEach(cb => {
        cb.onchange = actualizarBotonesBarraSuperior;
    });

    // Botón de información: abrir modal genérico y cargar datos dinámicamente
    document.querySelectorAll('.button-info').forEach(btn => {
        btn.onclick = function (e) {
            e.preventDefault();
            e.stopPropagation();
            const idAsignacion = btn.getAttribute('data-id-asignacion');
            if (!idAsignacion) return;
            abrirModalDetalleAsignacion(idAsignacion);
        };
    });

    document.querySelectorAll('.delete-button').forEach(btn => {
        btn.onclick = function (e) {
            e.preventDefault();
            e.stopPropagation();
            const url = btn.getAttribute('data-url');
            const title = btn.getAttribute('data-title') || 'Confirmar eliminación';
            const message = btn.getAttribute('data-message') || '¿Estás seguro de que deseas eliminar este elemento?';

            if (confirm(`${title}\n\n${message}`)) {
                fetch(url, { method: 'POST' })
                    .then(res => {
                        if (res.ok) {
                            location.reload();
                        } else {
                            alert('Error al eliminar la asignación.');
                        }
                    })
                    .catch(() => alert('Error al eliminar la asignación.'));
            }
        };
    });
}

// Modal genérico para detalles de asignación
function abrirModalDetalleAsignacion(idAsignacion) {
    // Mostrar el número de asignación en el título
    document.getElementById('modalDetalleAsignacionId').textContent = `#${idAsignacion}`;
    // Limpia el contenido anterior
    document.getElementById('modalDetalleAsignacionBody').innerHTML = '<div class="text-center">Cargando...</div>';
    const modal = new bootstrap.Modal(document.getElementById('modalDetalleAsignacion'));
    modal.show();

    fetch(`/asignacion/detalles_json/${idAsignacion}`)
        .then(res => res.json())
        .then(data => {
            if (!data.asignacion) {
                document.getElementById('modalDetalleAsignacionBody').innerHTML = '<div class="text-danger">No se encontraron datos.</div>';
                return;
            }
            const d = data.asignacion;
            document.getElementById('modalDetalleAsignacionBody').innerHTML = `
                <h5>Datos del Funcionario</h5>
                <table class="table table-bordered" style="table-layout: fixed">
                    <tr><td><strong>RUT</strong></td><td>${d.rutFuncionario || 'Sin información'}</td></tr>
                    <tr><td><strong>Nombre</strong></td><td>${d.nombreFuncionario || 'Sin información'}</td></tr>
                    <tr><td><strong>Cargo</strong></td><td>${d.cargoFuncionario || 'Sin información'}</td></tr>
                </table>
                <br>
                <h5>Datos de la Asignación</h5>
                <table class="table table-bordered" style="table-layout: fixed">
                    <tr><td><strong>Fecha de asignación</strong></td><td>${d.fecha_inicioAsignacion ? new Date(d.fecha_inicioAsignacion).toLocaleDateString() : 'Sin información'}</td></tr>
                    <tr><td><strong>Fecha de devolución</strong></td><td>${d.fechaDevolucion ? new Date(d.fechaDevolucion).toLocaleDateString() : 'Sin devolver'}</td></tr>
                    <tr><td><strong>Observaciones</strong></td><td>${d.ObservacionAsignacion || 'Sin información'}</td></tr>
                </table>
                <br>
                <h5>Datos del Equipo</h5>
                <table class="table table-bordered" style="table-layout: fixed">
                    <tr><td><strong>Tipo</strong></td><td>${d.nombreTipo_equipo || 'Sin información'}</td></tr>
                    <tr><td><strong>Marca</strong></td><td>${d.nombreMarcaEquipo || 'Sin información'}</td></tr>
                    <tr><td><strong>Modelo</strong></td><td>${d.nombreModeloequipo || 'Sin información'}</td></tr>
                    <tr><td><strong>Cód. inventario</strong></td><td>${d.Cod_inventarioEquipo || 'Sin información'}</td></tr>
                    <tr><td><strong>N° serie</strong></td><td>${d.Num_serieEquipo || 'Sin información'}</td></tr>
                    <tr><td><strong>Cód. proveedor</strong></td><td>${d.codigoproveedor_equipo || 'Sin información'}</td></tr>
                    <tr><td><strong>Observaciones</strong></td><td>${d.ObservacionEquipo || 'Sin información'}</td></tr>
                </table>
            `;
        })
        .catch(() => {
            document.getElementById('modalDetalleAsignacionBody').innerHTML = '<div class="text-danger">Error al cargar los datos.</div>';
        });
}
