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

// Funciones del modal para agregar una asignación de equipo
function asignarSeleccionados() {
    // 1. Obtener todos los checkboxes marcados
    const marcados = document.querySelectorAll('input[name="equipoSeleccionado"]:checked');
    if (marcados.length === 0) {
        alert("Por favor, selecciona al menos un equipo para asignar.");
        return;
    }

    // 2. Recorrerlos y agregarlos a la lista de equipos asignados
    marcados.forEach(chk => {
        // Obtener la fila de la tabla
        const row = chk.closest('tr');

        // Extraer datos de la fila (por ejemplo, Tipo, Marca, Modelo)
        const tipo = row.children[1].innerText;
        const marca = row.children[2].innerText;
        const modelo = row.children[3].innerText;

        // Crear un <li> para mostrar el equipo
        const li = document.createElement('li');
        li.classList.add('list-group-item');
        li.textContent = `${tipo} ${marca} ${modelo}`;

        // Agregar el <li> al contenedor de equipos asignados
        document.getElementById('equiposAsignadosList').appendChild(li);

        // Opcional: podrías ocultar o eliminar la fila del equipo ya asignado
        row.remove();
    });
}

function verDetalles() {
    // 1. Verifica cuántos checkboxes están seleccionados
    const marcados = document.querySelectorAll('input[name="equipoSeleccionado"]:checked');
    if (marcados.length !== 1) {
        alert("Por favor, selecciona un solo equipo para ver detalles.");
        return;
    }

    // 2. Obtener la información de la fila
    const row = marcados[0].closest('tr');
    const tipo = row.children[1].innerText;
    const marca = row.children[2].innerText;
    const modelo = row.children[3].innerText;

    // 3. Muestra esos detalles en un nuevo modal o un alert, según prefieras
    alert(`Detalles del equipo:\nTipo: ${tipo}\nMarca: ${marca}\nModelo: ${modelo}`);
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