
let selectAllState = false; // Estado actual: false = deseleccionado
document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('myTableBody');

    // Verifica que exista el cuerpo de la tabla antes de continuar
    if (!tableBody) {
        console.warn('No se encontró el cuerpo de la tabla.');
        return;
    }

    // Función para alternar la selección de todas las filas
    window.toggleSelectAll = function () {
        const checkboxes = tableBody.querySelectorAll('input[type="checkbox"]'); // Checkboxes dentro del tbody
        const allChecked = Array.from(checkboxes).every((checkbox) => checkbox.checked); // Verifica si todas están seleccionadas

        // Alterna el estado de los checkboxes
        checkboxes.forEach((checkbox) => {
            checkbox.checked = !allChecked;
        });

        console.log(allChecked ? 'Deseleccionando todas las filas' : 'Seleccionando todas las filas');
    };
});


// Añadir las flechas automáticamente a los encabezados ordenables
document.addEventListener('DOMContentLoaded', () => {
    const sortableHeaders = document.querySelectorAll('.sortable-column');

    sortableHeaders.forEach(header => {
        // Agregar los íconos de ordenamiento
        header.innerHTML += `
        <i class="bi bi-caret-up"></i>
        <i class="bi bi-caret-down"></i>
        `;
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById("myTableBody");
    const paginationContainer = document.getElementById("pagination-container");
    const prevPageBtn = document.getElementById("prev-page");
    const nextPageBtn = document.getElementById("next-page");
    const pageNumbersContainer = document.getElementById("page-numbers");

    const rowsPerPage = 10; // Número de filas por página
    let currentPage = 1;
    let totalRows;
    let rows;

    function paginateTable() {
        rows = [...tableBody.querySelectorAll("tr")]; // Obtener todas las filas
        totalRows = rows.length;
        renderPage(currentPage);
        renderPagination();
    }

    function renderPage(page) {
        let startIndex = (page - 1) * rowsPerPage;
        let endIndex = startIndex + rowsPerPage;

        rows.forEach((row, index) => {
            row.style.display = (index >= startIndex && index < endIndex) ? "" : "none";
        });

        // Deshabilitar los botones de "Anterior" y "Siguiente" si es necesario
        prevPageBtn.parentElement.classList.toggle("disabled", page === 1);
        nextPageBtn.parentElement.classList.toggle("disabled", page === Math.ceil(totalRows / rowsPerPage));
    }

    function renderPagination() {
        let totalPages = Math.ceil(totalRows / rowsPerPage);
        pageNumbersContainer.innerHTML = ""; // Limpiar numeración de páginas

        if (totalPages <= 1) return; // Si solo hay una página, no mostrar paginación

        function createPageItem(page) {
            let li = document.createElement("li");
            li.classList.add("page-item");
            if (page === currentPage) li.classList.add("active");

            let a = document.createElement("a");
            a.classList.add("page-link");
            a.href = "#";
            a.textContent = page;
            a.setAttribute("data-page", page);

            li.appendChild(a);
            pageNumbersContainer.appendChild(li);
        }

        // Mostrar siempre la primera página
        createPageItem(1);

        // Agregar "..." si la diferencia entre la primera y la actual es mayor a 2
        if (currentPage > 3) {
            let dots = document.createElement("li");
            dots.classList.add("page-item", "disabled");
            dots.innerHTML = '<span class="page-link">...</span>';
            pageNumbersContainer.appendChild(dots);
        }

        // Mostrar las páginas anteriores y siguientes cuando aplicable
        if (currentPage - 1 > 1) createPageItem(currentPage - 1);
        if (currentPage !== 1 && currentPage !== totalPages) createPageItem(currentPage);
        if (currentPage + 1 < totalPages) createPageItem(currentPage + 1);

        // Agregar "..." si hay una gran distancia con la última página
        if (currentPage < totalPages - 2) {
            let dots = document.createElement("li");
            dots.classList.add("page-item", "disabled");
            dots.innerHTML = '<span class="page-link">...</span>';
            pageNumbersContainer.appendChild(dots);
        }

        // Mostrar siempre la última página
        if (totalPages > 1) createPageItem(totalPages);

        // Agregar eventos a los números de página
        pageNumbersContainer.querySelectorAll(".page-link").forEach(link => {
            link.addEventListener("click", (e) => {
                e.preventDefault();
                let newPage = parseInt(e.target.getAttribute("data-page"));
                if (!isNaN(newPage)) {
                    currentPage = newPage;
                    renderPage(currentPage);
                    renderPagination();
                }
            });
        });
    }

    // Eventos para los botones Anterior / Siguiente
    prevPageBtn.addEventListener("click", (e) => {
        e.preventDefault();
        if (currentPage > 1) {
            currentPage--;
            renderPage(currentPage);
            renderPagination();
        }
    });

    nextPageBtn.addEventListener("click", (e) => {
        e.preventDefault();
        let totalPages = Math.ceil(totalRows / rowsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            renderPage(currentPage);
            renderPagination();
        }
    });

    // **Iniciar paginación al cargar la página**
    paginateTable();

    // **Actualizar paginación cuando se realiza una búsqueda**
    document.getElementById("buscador").addEventListener("input", function () {
        let searchTerm = this.value.toLowerCase();
        let visibleRows = [];

        rows.forEach(row => {
            let text = row.innerText.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = "";
                visibleRows.push(row);
            } else {
                row.style.display = "none";
            }
        });

        // Si hay búsqueda, ocultamos la paginación
        paginationContainer.style.display = searchTerm ? "none" : "flex";
    });
});


let currentSortColumn = null; // Columna actualmente ordenada
let currentSortOrder = 'neutral'; // Estados posibles: 'neutral', 'asc', 'desc'

function sortTable(columnIndex, headerElement) {
    const tableBody = document.getElementById('myTableBody');
    const rows = Array.from(tableBody.querySelectorAll('tr'));

    // Alternar entre ascendente y descendente
    if (currentSortColumn === columnIndex) {
        currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortColumn = columnIndex;
        currentSortOrder = 'asc';
    }

    // Ordenar las filas
    rows.sort((rowA, rowB) => {
        const cellA = rowA.cells[columnIndex].innerText.trim();
        const cellB = rowB.cells[columnIndex].innerText.trim();

        const valueA = parseCellValue(cellA);
        const valueB = parseCellValue(cellB);

        if (currentSortOrder === 'asc') {
            return valueA > valueB ? 1 : valueA < valueB ? -1 : 0;
        } else if (currentSortOrder === 'desc') {
            return valueA < valueB ? 1 : valueA > valueB ? -1 : 0;
        }
    });

    // Actualizar la tabla con las filas ordenadas
    tableBody.innerHTML = '';
    rows.forEach(row => tableBody.appendChild(row));

    // Actualizar los íconos de las flechas
    updateSortIcons(headerElement);
}

function parseCellValue(cell) {
    // Detectar si es un número
    if (!isNaN(cell) && cell.trim() !== '') return parseFloat(cell);

    // Detectar si es una fecha válida
    const date = Date.parse(cell);
    if (!isNaN(date)) return new Date(date);

    // Devolver como texto en minúsculas
    return cell.toLowerCase();
}

function updateSortIcons(headerElement) {
    // Quitar clases activas y ocultar íconos de todas las columnas
    const allHeaders = document.querySelectorAll('.sortable-column');
    allHeaders.forEach(header => {
        const upIcon = header.querySelector('.bi-caret-up, .bi-caret-up-fill');
        const downIcon = header.querySelector('.bi-caret-down, .bi-caret-down-fill');
        if (upIcon) upIcon.className = 'bi bi-caret-up hidden'; // Ocultar por defecto
        if (downIcon) downIcon.className = 'bi bi-caret-down hidden'; // Ocultar por defecto
    });

    // Activar y mostrar el ícono correspondiente en la columna actual
    const upIcon = headerElement.querySelector('.bi-caret-up, .bi-caret-up-fill');
    const downIcon = headerElement.querySelector('.bi-caret-down, .bi-caret-down-fill');

    if (currentSortOrder === 'asc' && upIcon) {
        upIcon.className = 'bi bi-caret-up-fill'; // Mostrar ascendente
        downIcon.className = 'bi bi-caret-down hidden'; // Ocultar descendente
    } else if (currentSortOrder === 'desc' && downIcon) {
        downIcon.className = 'bi bi-caret-down-fill'; // Mostrar descendente
        upIcon.className = 'bi bi-caret-up hidden'; // Ocultar ascendente
    }
}


