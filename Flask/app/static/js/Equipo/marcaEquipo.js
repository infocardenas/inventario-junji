$(document).ready(function () {

    // Evento para manejar la selección de acciones
    $(".actions-select").on("change", function () {
        const action = $(this).val();
        const selectedRows = $(".row-checkbox:checked").closest("tr");

        if (!selectedRows.length) {
            alert("Por favor, selecciona una o más filas antes de realizar una acción.");
            $(this).val("");
            return;
        }

        const ids = selectedRows.map(function () {
            return $(this).data("id");
        }).get().join(',');

        if (action === "delete") {
            configureGenericModal(
                "Eliminar Marca(s)",
                `¿Estás seguro de que deseas eliminar las marcas seleccionadas?`,
                `/marca_equipo/delete_marca_equipo/${ids}`
            );
        } else if (action === "edit") {
            if (selectedRows.length > 1) {
                alert("Solo puedes editar una marca a la vez.");
                $(this).val("");
                return;
            }

            // Obtener la fila seleccionada
            const selectedRow = selectedRows.first();
            const id = selectedRow.data("id");
            const nombre = selectedRow.find("td:nth-child(2)").text().trim();

            // Rellenar el modal de edición
            $("#editMarcaModal").modal("show");
            $("#editMarcaModalLabel").text(`Editar Marca: ${nombre}`);
            $("#edit_nombreMarca").val(nombre);
            $("#editMarcaForm").attr("action", `/update_marca_equipo/${id}`);

            // Guardar temporalmente el nombre en LocalStorage para usarlo en futuras aperturas
            localStorage.setItem("ultimaMarcaGuardada", nombre);
        }
        $(this).val("");
    });

    // Evento para abrir el modal de edición desde el botón "Editar"
    $(".editMarcaBtn").on("click", function () {
        const id = $(this).data("id");
        const nombre = $(this).data("nombre");

        // Rellenar el modal con los datos correctos
        $("#editMarcaModal").modal("show");
        $("#editMarcaModalLabel").text(`Editar Marca: ${nombre}`);
        $("#edit_nombreMarca").val(nombre);
        $("#editMarcaForm").attr("action", `/update_marca_equipo/${id}`);

        // Guardar temporalmente en localStorage para persistencia en la sesión
        localStorage.setItem("ultimaMarcaGuardada", nombre);
    });

    // Función para cargar la última marca guardada en el modal de edición
    function cargarUltimaMarca() {
        const ultimaMarca = localStorage.getItem("ultimaMarcaGuardada");
        if (ultimaMarca) {
            $("#edit_nombreMarca").val(ultimaMarca);
        }
    }

    // Evento cuando el modal de edición se abre
    $("#editMarcaModal").on("shown.bs.modal", function () {
        cargarUltimaMarca();
    });

});

$(document).ready(function () {

    // Evento para abrir el modal de confirmación antes de eliminar
    $("#eliminarSeleccionados").on("click", function () {
        const selectedRows = $(".row-checkbox:checked").closest("tr");
        const mensajeError = $("#mensajeError");

        if (!selectedRows.length) {
            mensajeError.text("⚠️ Selecciona al menos una marca para eliminar.").show();
            return;
        }

        mensajeError.hide(); // Ocultar mensaje de error si ya se seleccionaron filas

        // Obtener los IDs seleccionados en formato correcto (separados por comas)
        const ids = selectedRows.map(function () {
            return $(this).data("id");
        }).get().join(',');

        // Guardar los IDs en el botón de confirmación
        $("#confirmDeleteBtn").data("ids", ids);

        // Mostrar el modal de confirmación
        $("#confirmDeleteModal").modal("show");
    });

    // Evento cuando el usuario confirma la eliminación
    $("#confirmDeleteBtn").on("click", function () {
        const ids = $(this).data("ids");

        if (!ids) {
            $("#mensajeError").text("⚠️ No se encontraron marcas para eliminar.").show();
            return;
        }

        // Mostrar mensaje de carga mientras se ejecuta la eliminación
        $("#mensajeExito").text("⏳ Eliminando marcas...").show();

        // Redirigir a la función de eliminación en Flask
        window.location.href = `/marca_equipo/delete_marca_equipo/${ids}`;
    });

});
