$(document).ready(function () {
    $(".actions-select").on("change", function () {
        const action = $(this).val();
        const selectedRows = $(".row-checkbox:checked").closest("tr"); 

        console.log("Acción seleccionada:", action); // Verificar acción seleccionada
        console.log("Filas seleccionadas:", selectedRows.length); // Verificar si hay filas seleccionadas

        if (!selectedRows.length) {
            alert("Por favor, selecciona una o más filas antes de realizar una acción.");
            $(this).val(""); 
            return;
        }

        const ids = selectedRows.map(function () {
            return $(this).data("id");
        }).get();

        console.log("IDs capturados:", ids); // Verificar los IDs capturados

        if (action === "delete") {
            configureGenericModal(
                "Eliminar Tipo(s) de Equipo",
                `¿Estás seguro de que deseas eliminar los tipos seleccionados? Esto afectará las relaciones asociadas.`,
                `/tipo_equipo/delete_tipo_equipo/${ids.join(',')}`
            );
        } else if (action === "edit") {
            if (selectedRows.length > 1) {
                alert("Solo puedes editar un tipo de equipo a la vez.");
                $(this).val("");
                return;
            }

            const selectedRow = selectedRows.first();
            const id = selectedRow.data("id");
            const nombre = selectedRow.data("nombre");
            const marcas = selectedRow.data("marcas");

            console.log("Editando ID:", id); // Verificar ID al editar
            console.log("Nombre capturado:", nombre);
            console.log("Marcas capturadas:", marcas);

            $("#editTipoModal").modal("show");
            $("#editTipoModalLabel").text(`Editar Tipo: ${nombre}`);
            $("#edit_nombreTipo").val(nombre);
            $("#editTipoForm").attr("action", `/update_tipo_equipo/${id}`);
        }

        $(this).val("");
    });
});
