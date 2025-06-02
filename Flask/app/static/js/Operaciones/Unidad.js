function buscarUnidades(page = 1) {
  const query = document.getElementById("buscador_unidad").value.toLowerCase();

  fetch(`/buscar_unidades?q=${encodeURIComponent(query)}&page=${page}`)
    .then(response => response.json())
    .then(data => {
      actualizarTablaUnidades(data.unidades);
      actualizarPaginacionUnidades(data.total_pages, data.current_page, query, data.visible_pages);
    })
    .catch(error => console.error("Error al buscar unidades:", error));
}

let unidadesActuales = [];
let ordenActual = { campo: null, asc: true };

function actualizarTablaUnidades(unidades) {
  unidadesActuales = unidades; // Guardar para ordenar
  const tbody = document.getElementById("unidadTableBody");
  tbody.innerHTML = "";

  if (!unidades.length) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center">No hay datos disponibles.</td></tr>';
    return;
  }

  unidades.forEach(ubi => {
    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${ubi.idUnidad}</td>
        <td>${ubi.nombreUnidad}</td>
        <td>${ubi.contactoUnidad}</td>
        <td>${ubi.direccionUnidad}</td>
        <td>${ubi.nombreComuna}</td>
        <td>${ubi.num_equipos}</td>
        <td>${ubi.nombreModalidad || ''}</td>
        <td>
          <div class="d-flex gap-1">
            <button class="btn btn-success btn-sm" data-bs-toggle="modal" data-bs-target="#modal-edit-unidad"
              data-id="${ubi.idUnidad}" data-codigo="${ubi.idUnidad}" data-nombre="${ubi.nombreUnidad}"
              data-contacto="${ubi.contactoUnidad}" data-direccion="${ubi.direccionUnidad}"
              data-comuna="${ubi.idComuna}" data-modalidad="${ubi.idModalidad}" title="Editar">
              <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-info btn-sm" data-bs-toggle="tooltip" title="Funcionarios"
              onclick="window.location.href='/mostrar_funcionarios_unidad/${ubi.idUnidad}'">
              <i class="bi bi-people-fill"></i>
            </button>
            <button class="btn btn-warning btn-sm" title="Ver Equipos"
              onclick="window.location.href='/mostrar_equipos_unidad/${ubi.idUnidad}'">
              <i class="bi bi-hdd-network-fill"></i>
            </button>
            <button class="btn btn-danger btn-sm" data-bs-toggle="tooltip" title="Eliminar"
              onclick="window.location.href='/delete_Unidad/${ubi.idUnidad}'">
              <i class="bi bi-trash-fill"></i>
            </button>
          </div>
        </td>
      `;
    tbody.appendChild(row);
  });
}

function ordenarUnidad(campo) {
  if (ordenActual.campo === campo) {
    ordenActual.asc = !ordenActual.asc;
  } else {
    ordenActual.campo = campo;
    ordenActual.asc = true;
  }
  unidadesActuales.sort((a, b) => {
    let valA = a[campo];
    let valB = b[campo];
    // Convertir a número si corresponde
    if (!isNaN(valA) && !isNaN(valB)) {
      valA = Number(valA);
      valB = Number(valB);
    } else {
      valA = (valA || '').toString().toLowerCase();
      valB = (valB || '').toString().toLowerCase();
    }
    if (valA < valB) return ordenActual.asc ? -1 : 1;
    if (valA > valB) return ordenActual.asc ? 1 : -1;
    return 0;
  });
  actualizarTablaUnidades(unidadesActuales);
}

function actualizarPaginacionUnidades(totalPages, currentPage, query, visiblePages) {
  const pagination = document.getElementById("unidad-pagination");
  pagination.innerHTML = "";

  visiblePages.forEach(page => {
    const li = document.createElement("li");
    if (page === "...") {
      li.className = "page-item disabled";
      li.innerHTML = `<span class="page-link">...</span>`;
    } else {
      li.className = `page-item ${page === currentPage ? "active" : ""}`;
      li.innerHTML = `<a class="page-link" href="#" onclick="buscarUnidades(${page});return false;">${page}</a>`;
    }
    pagination.appendChild(li);
  });

  // Botón "Anterior"
  if (currentPage > 1) {
    const prevLi = document.createElement("li");
    prevLi.className = "page-item";
    prevLi.innerHTML = `<a class="page-link" href="#" onclick="buscarUnidades(${currentPage - 1});return false;">Anterior</a>`;
    pagination.insertBefore(prevLi, pagination.firstChild);
  }

  // Botón "Siguiente"
  if (currentPage < totalPages) {
    const nextLi = document.createElement("li");
    nextLi.className = "page-item";
    nextLi.innerHTML = `<a class="page-link" href="#" onclick="buscarUnidades(${currentPage + 1});return false;">Siguiente</a>`;
    pagination.appendChild(nextLi);
  }
}

// Opcional: cargar todas las unidades al cargar la página
document.addEventListener("DOMContentLoaded", function () {
  buscarUnidades(1);
});
