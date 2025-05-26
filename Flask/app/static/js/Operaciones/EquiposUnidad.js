let equiposActuales = [];
let ordenActualEquipo = { campo: null, asc: true };

function buscarEquiposUnidad(page = 1) {
  const query = document.getElementById("buscador_equipo").value.toLowerCase();
  // Extrae el idUnidad de la URL
  const match = window.location.pathname.match(/\/mostrar_equipos_unidad\/(\d+)/);
  const idUnidad = match ? match[1] : null;
  if (!idUnidad) return;

  fetch(`/buscar_equipos_unidad/${idUnidad}?q=${encodeURIComponent(query)}&page=${page}`)
    .then(response => response.json())
    .then(data => {
      actualizarTablaEquiposUnidad(data.equipos);
      actualizarPaginacionEquiposUnidad(data.total_pages, data.current_page, query, data.visible_pages);
    })
    .catch(error => console.error("Error al buscar equipos:", error));
}

function actualizarTablaEquiposUnidad(equipos) {
  equiposActuales = equipos;
  const tbody = document.getElementById("equiposUnidadTableBody");
  tbody.innerHTML = "";

  if (!equipos.length) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center">No hay datos disponibles.</td></tr>';
    return;
  }

  equipos.forEach(eq => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${eq.Cod_inventarioEquipo || ""}</td>
      <td>${eq.Num_serieEquipo || ""}</td>
      <td>${eq.estadoEquipo || ""}</td>
      <td>${eq.nombreFuncionario || ""}</td>
      <td>${eq.codigoproveedor_equipo || ""}</td>
      <td>${eq.nombreUnidad || ""}</td>
      <td>${eq.tipoEquipo || ""}</td>
      <td>${eq.modeloEquipo || ""}</td>
    `;
    tbody.appendChild(row);
  });
}

function actualizarPaginacionEquiposUnidad(totalPages, currentPage, query, visiblePages) {
  const pagination = document.getElementById("equipos-unidad-pagination");
  pagination.innerHTML = "";

  visiblePages.forEach(page => {
    const li = document.createElement("li");
    if (page === "...") {
      li.className = "page-item disabled";
      li.innerHTML = `<span class="page-link">...</span>`;
    } else {
      li.className = `page-item ${page === currentPage ? "active" : ""}`;
      li.innerHTML = `<a class="page-link" href="#" onclick="buscarEquiposUnidad(${page});return false;">${page}</a>`;
    }
    pagination.appendChild(li);
  });

  // Botón "Anterior"
  if (currentPage > 1) {
    const prevLi = document.createElement("li");
    prevLi.className = "page-item";
    prevLi.innerHTML = `<a class="page-link" href="#" onclick="buscarEquiposUnidad(${currentPage - 1});return false;">Anterior</a>`;
    pagination.insertBefore(prevLi, pagination.firstChild);
  }

  // Botón "Siguiente"
  if (currentPage < totalPages) {
    const nextLi = document.createElement("li");
    nextLi.className = "page-item";
    nextLi.innerHTML = `<a class="page-link" href="#" onclick="buscarEquiposUnidad(${currentPage + 1});return false;">Siguiente</a>`;
    pagination.appendChild(nextLi);
  }
}

// Opcional: cargar equipos al cargar la página
document.addEventListener("DOMContentLoaded", function () {
  buscarEquiposUnidad(1);
});