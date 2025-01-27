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
