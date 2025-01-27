
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


