let funcionariosActuales = [];

function buscarFuncionariosUnidad(page = 1) {
  const query = document.getElementById("buscador_funcionario").value.toLowerCase();
  const match = window.location.pathname.match(/\/mostrar_funcionarios_unidad\/(\d+)/);
  const idUnidad = match ? match[1] : null;
  if (!idUnidad) return;

  fetch(`/buscar_funcionarios_unidad/${idUnidad}?q=${encodeURIComponent(query)}&page=${page}`)
    .then(response => response.json())
    .then(data => {
      actualizarTablaFuncionariosUnidad(data.funcionarios);
      actualizarPaginacionFuncionariosUnidad(data.total_pages, data.current_page, query, data.visible_pages);
    })
    .catch(error => console.error("Error al buscar funcionarios:", error));
}

function actualizarTablaFuncionariosUnidad(funcionarios) {
  funcionariosActuales = funcionarios;
  const tbody = document.getElementById("funcionariosUnidadTableBody");
  tbody.innerHTML = "";

  if (!funcionarios.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="text-center">No hay datos disponibles.</td></tr>';
    return;
  }

  funcionarios.forEach(f => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${f.rutFuncionario || ""}</td>
      <td>${f.nombreFuncionario || ""}</td>
      <td>${f.cargoFuncionario || ""}</td>
      <td>${f.correoFuncionario || ""}</td>
    `;
    tbody.appendChild(row);
  });
}

function actualizarPaginacionFuncionariosUnidad(totalPages, currentPage, query, visiblePages) {
  const pagination = document.getElementById("funcionarios-unidad-pagination");
  pagination.innerHTML = "";

  visiblePages.forEach(page => {
    const li = document.createElement("li");
    if (page === "...") {
      li.className = "page-item disabled";
      li.innerHTML = `<span class="page-link">...</span>`;
    } else {
      li.className = `page-item ${page === currentPage ? "active" : ""}`;
      li.innerHTML = `<a class="page-link" href="#" onclick="buscarFuncionariosUnidad(${page});return false;">${page}</a>`;
    }
    pagination.appendChild(li);
  });

  if (currentPage > 1) {
    const prevLi = document.createElement("li");
    prevLi.className = "page-item";
    prevLi.innerHTML = `<a class="page-link" href="#" onclick="buscarFuncionariosUnidad(${currentPage - 1});return false;">Anterior</a>`;
    pagination.insertBefore(prevLi, pagination.firstChild);
  }

  if (currentPage < totalPages) {
    const nextLi = document.createElement("li");
    nextLi.className = "page-item";
    nextLi.innerHTML = `<a class="page-link" href="#" onclick="buscarFuncionariosUnidad(${currentPage + 1});return false;">Siguiente</a>`;
    pagination.appendChild(nextLi);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  buscarFuncionariosUnidad(1);
});