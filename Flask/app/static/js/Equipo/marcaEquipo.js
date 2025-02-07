$(document).ready(function () {
    // Detectar cambios en los checkboxes para actualizar los botones
    $(document).on("change", ".row-checkbox, #selectAll", function () {
        actualizarBotonesAcciones();
    });

    function actualizarBotonesAcciones() {
        const seleccionados = $(".row-checkbox:checked");
        const deleteButton = $(".delete-button");
        const editButton = $(".edit-button");

        if (seleccionados.length > 0) {
            // Construir la URL para eliminar (con múltiples IDs separados por comas)
            const ids = seleccionados.map(function () {
                return $(this).closest("tr").data("id");
            }).get().join(",");

            deleteButton.data("url", `/delete_marca_equipo/${ids}`);
            deleteButton.prop("disabled", false);
        } else {
            deleteButton.data("url", ""); // Limpiar URL cuando no hay selección
            deleteButton.prop("disabled", true);
        }

        if (seleccionados.length === 1) {
            // Obtener el ID de la única fila seleccionada para edición
            const selectedRow = seleccionados.closest("tr");
            const id = selectedRow.data("id");
            const nombre = selectedRow.find("td:nth-child(2)").text().trim();

            editButton.data("url", `/update_marca_equipo/${id}`);
            editButton.prop("disabled", false);

            // Guardamos el valor original en un atributo `data-original`
            $("#modal-edit-marca-input")
                .val(nombre)
                .attr("data-original", nombre);
            $("#modal-edit-marca-title").text(`Editar marca: ${nombre}`);
            $("#form-edit-marca-equipo").attr("action", `/update_marca_equipo/${id}`);

        } else {
            editButton.data("url", "");
            editButton.prop("disabled", true);
        }
    }

    // Manejar selección/deselección de todos los checkboxes
    $(document).on("change", "#selectAll", function () {
        $(".row-checkbox").prop("checked", this.checked);
        actualizarBotonesAcciones();
    });

    // Manejar clic en el botón "Editar" para abrir el modal
    $(".edit-button").on("click", function () {
        if ($(this).prop("disabled")) return; // Evita abrir el modal si está deshabilitado

        // Restablecer el valor original antes de abrir el modal
        const inputMarca = $("#modal-edit-marca-input");
        inputMarca.val(inputMarca.attr("data-original"));

        $("#modal-edit-marca").modal("show");
    });

    // Manejar clic en el botón "Eliminar" para abrir el modal de confirmación
    $(".delete-button").on("click", function () {
        if ($(this).prop("disabled")) return; // Evita la acción si está deshabilitado

        const deleteUrl = $(this).data("url");

        if (!deleteUrl.includes("/delete_marca_equipo/")) {
            return;
        }

        // Configurar el modal con la URL correcta
        $("#confirm-delete-button").attr("href", deleteUrl);
        $("#modal-delete-marca").modal("show");
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
