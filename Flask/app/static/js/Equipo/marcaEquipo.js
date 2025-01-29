$(document).ready(function () {
    $(".actions-select").on("change", function () {
        const action = $(this).val(); // Obtener la acción seleccionada
        const selectedRows = $(".row-checkbox:checked").closest("tr"); // Filas seleccionadas

        if (!selectedRows.length) {
            alert("Por favor, selecciona una o más filas antes de realizar una acción."); // Validación básica
            $(this).val(""); // Resetear el select
            return;
        }

        // Obtener los IDs de las marcas seleccionadas
        const ids = selectedRows.map(function () {
            return $(this).data("id");
        }).get().join(',');

        if (action === "delete") {
            // Mostrar el modal de confirmación
            configureGenericModal(
                "Eliminar Marca(s)",
                `¿Estás seguro de que deseas eliminar las marcas seleccionadas? Esto eliminará también las relaciones asociadas.`,
                `/marca_equipo/delete_marca_equipo/${ids}` // URL de eliminación
            );
        } else if (action === "edit") {
            if (selectedRows.length > 1) {
                alert("Solo puedes editar una marca a la vez.");
                $(this).val("");
                return;
            }

            // Configurar el modal de edición para una sola fila
            const selectedRow = selectedRows.first();
            const id = selectedRow.data("id");
            const nombre = selectedRow.find("td:nth-child(2)").text();

            $("#editMarcaModal").modal("show");
            $("#editMarcaModalLabel").text(`Editar Marca: ${nombre}`);
            $("#edit_nombreMarca").val(nombre);
            $("#editMarcaForm").attr("action", `/update_marca_equipo/${id}`);
        }

        $(this).val(""); // Resetear el select después de usarlo
    });
});
