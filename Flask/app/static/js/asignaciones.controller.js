$(document).ready(function () {
    function configModalVisualizar(title, data) {
        $("#modal-view-title").text(title); // Establecer el título del modal
        let modalContent = "";

        // Agregar los estilos directamente en el modal
        modalContent += `
            <style>
                .modal-content {
                    display: flex;
                    flex-direction: column;
                }

                .table {
                    width: 100%;
                    table-layout: fixed;
                }
            </style>
        `;

        // 1) Tabla de Funcionario
        modalContent += `
            <h5>Datos del Funcionario</h5>
            <table class="table table-bordered">
                <tr>
                    <td><strong>RUT</strong></td>
                    <td>${data.funcionario.rut}</td>
                </tr>
                <tr>
                    <td><strong>Nombre</strong></td>
                    <td>${data.funcionario.nombre}</td>
                </tr>
                <tr>
                    <td><strong>Cargo</strong></td>
                    <td>${data.funcionario.cargo}</td>
                </tr>
            </table>
        `;

        // 2) Tabla de Asignación
        modalContent += `
            <br>
            <h5>Datos de la asignación</h5>
            <table class="table table-bordered">
                <tr>
                    <td><strong>Fecha de asignación</strong></td>
                    <td>${data.asignacion.fecha_inicio}</td>
                </tr>
                <tr>
                    <td><strong>Fecha de devolución</strong></td>
                    <td>${data.asignacion.fecha_devolucion}</td>
                </tr>
                <tr>
                    <td><strong>Observaciones</strong></td>
                    <td>${data.asignacion.observacion}</td>
                </tr>
            </table>
        `;

        // 3) Tabla de Equipo
        modalContent += `
            <br>
            <h5>Datos del equipo</h5>
            <table class="table table-bordered">
                <tr>
                    <td><strong>Tipo</strong></td>
                    <td>${data.equipo.tipo_equipo}</td>
                </tr>
                <tr>
                    <td><strong>Marca</strong></td>
                    <td>${data.equipo.marca_equipo}</td>
                </tr>
                <tr>
                    <td><strong>Modelo</strong></td>
                    <td>${data.equipo.modelo_equipo}</td>
                </tr>
            </table>
        `;

        // Inyectamos todo en el modal
        $("#modal-view-message").html(modalContent);
    }

    // Manejador de clic en los enlaces "Detalles"
    $(".view-details").on("click", function () {
        const title = $(this).data("title");
        const info = $(this).attr("data-info");

        let data;
        try {
            data = JSON.parse(info);
        } catch (error) {
            console.error("Error parsing JSON data-info:", error);
            return;
        }

        configModalVisualizar(title, data);
        $("#modal-view").modal("show");
    });
});

document.addEventListener("DOMContentLoaded", () => {
    // Refresh checkbox listeners and button states
    refreshCheckboxListeners();
});

function refreshCheckboxListeners() {
    const equipoCheckboxes = document.querySelectorAll('input[name="equipoSeleccionado"]');
    const asignarBtn = document.querySelector('button[onclick="asignarSeleccionados()"]');
    const detallesBtn = document.querySelector('button[onclick="verDetalles()"]');

    function toggleButtons() {
        const seleccionados = Array.from(equipoCheckboxes).filter(checkbox => checkbox.checked).length;

        asignarBtn.disabled = seleccionados === 0;
        detallesBtn.disabled = seleccionados !== 1;
    }

    // Actualizar listeners de cambio en los checkboxes
    equipoCheckboxes.forEach(checkbox => {
        checkbox.removeEventListener('change', toggleButtons);
        checkbox.addEventListener('change', toggleButtons);
    });

    // Habilitar clic en filas
    enableRowClick();

    // Actualizar botones al cargar
    toggleButtons();
}


function asignarSeleccionados() {
    const marcados = document.querySelectorAll('input[name="equipoSeleccionado"]:checked');
    if (marcados.length === 0) {
        alert("Por favor, selecciona al menos un equipo para asignar.");
        return;
    }

    marcados.forEach(chk => {
        const row = chk.closest('tr');
        const tipo = row.children[1].innerText;
        const marca = row.children[2].innerText;
        const modelo = row.children[3].innerText;

        // Obtener los atributos `data-*` para restaurar después
        const codigoInventario = row.dataset.codigoInventario || "N/A";
        const numeroSerie = row.dataset.numeroSerie || "N/A";
        const codigoProveedor = row.dataset.codigoProveedor || "N/A";
        const unidad = row.dataset.unidad || "N/A";

        // Crear un <li> para los equipos asignados
        const li = document.createElement('li');
        li.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');
        li.innerHTML = `
            <span>${tipo} ${marca} ${modelo}</span>
            <button type="button" class="btn btn-danger btn-sm" 
                onclick="quitarEquipo(this, '${chk.value}', '${tipo}', '${marca}', '${modelo}', '${codigoInventario}', '${numeroSerie}', '${codigoProveedor}', '${unidad}')">
                <i class="bi bi-trash-fill"></i>
            </button>
            <input type="hidden" class="no-delete-value" name="equiposAsignados[]" value="${chk.value}">
        `;

        document.getElementById('equiposAsignadosList').appendChild(li);
        row.remove(); // Remover fila de la tabla
    });

    refreshCheckboxListeners(); // Actualizar listeners después de modificar la tabla
}



function quitarEquipo(button, idEquipo, tipo, marca, modelo, codigoInventario, numeroSerie, codigoProveedor, unidad) {
    const li = button.closest('li');
    li.remove();

    const equiposTable = document.getElementById('equiposTable');
    const newRow = document.createElement('tr');

    // Rellenar los datos de la fila incluyendo los atributos `data-*`
    newRow.setAttribute('data-codigo-inventario', codigoInventario || "N/A");
    newRow.setAttribute('data-numero-serie', numeroSerie || "N/A");
    newRow.setAttribute('data-codigo-proveedor', codigoProveedor || "N/A");
    newRow.setAttribute('data-unidad', unidad || "N/A");

    newRow.innerHTML = `
        <td><input class="no-delete-value" type="checkbox" name="equipoSeleccionado" value="${idEquipo}"></td>
        <td>${tipo}</td>
        <td>${marca}</td>
        <td>${modelo}</td>
    `;

    equiposTable.appendChild(newRow);

    refreshCheckboxListeners(); // Asegúrate de actualizar los listeners
}


function verDetalles() {
    const marcados = document.querySelectorAll('input[name="equipoSeleccionado"]:checked');
    
    // Validar que solo un equipo esté seleccionado
    if (marcados.length !== 1) {
        alert("Por favor, selecciona un único equipo para ver detalles.");
        return;
    }

    // Obtener la fila del equipo seleccionado
    const row = marcados[0].closest('tr');
    const tipo = row.children[1].innerText;
    const marca = row.children[2].innerText;
    const modelo = row.children[3].innerText;

    // Rellenar los datos en el modal
    document.getElementById('detalleTipo').textContent = tipo;
    document.getElementById('detalleMarca').textContent = marca;
    document.getElementById('detalleModelo').textContent = modelo;
    document.getElementById('detalleCodigoInventario').textContent = row.dataset.codigoInventario || "N/A";
    document.getElementById('detalleNumeroSerie').textContent = row.dataset.numeroSerie || "N/A";
    document.getElementById('detalleCodigoProveedor').textContent = row.dataset.codigoProveedor || "N/A";
    document.getElementById('detalleUnidad').textContent = row.dataset.unidad || "N/A";
}

// Búsqueda dinámica
document.getElementById('searchEquipo').addEventListener('input', function () {
    const filter = this.value.toLowerCase();
    const rows = document.querySelectorAll('#equiposTable tr');

    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
    });
});

function enableRowClick() {
    const rows = document.querySelectorAll('#equiposTable tr');

    // Remover listeners existentes para evitar duplicados
    rows.forEach(row => {
        row.removeEventListener('click', rowClickHandler);
        row.addEventListener('click', rowClickHandler);
    });
}

function rowClickHandler(event) {
    // Evitar que el evento se dispare si el clic es sobre el checkbox
    if (event.target.tagName === 'INPUT' && event.target.type === 'checkbox') return;

    // Encontrar el checkbox en la fila y alternar su estado
    const checkbox = this.querySelector('input[type="checkbox"]');
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
        checkbox.dispatchEvent(new Event('change')); // Disparar evento 'change' manualmente
    }
}
