$(document).ready(function () {
    $(".actions-select").on("change", function () {
        const action = $(this).val();
        const selectedRows = $(".row-checkbox:checked").closest("tr");

        if (!selectedRows.length) {
            alert("Por favor, selecciona una fila antes de realizar una acción.");
            $(this).val("");
            return;
        }

        const ids = selectedRows.map(function () {
            return $(this).data("id");
        }).get();

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

            // Capturar los datos de la fila seleccionada
            const selectedRow = selectedRows.first();
            const id = selectedRow.data("id");
            const nombre = selectedRow.data("nombre");
            const marcas = selectedRow.data("marcas");
            const observacion = selectedRow.data("observacion");


            console.log("Editando ID:", id);
            console.log("Nombre:", nombre);
            console.log("Marcas:", marcas);
            console.log("Observación:", observacion);

            // Rellenar el formulario dentro del modal
            $("#editTipoEquipoLabel").text(`Editar Tipo de Equipo: ${nombre}`);
            $("#edit_nombreTipo_equipo").val(nombre);
            $("#edit_observacion").val(observacion || "");  // Evita valores `null`

            // Desmarcar todos los checkboxes antes de marcar los seleccionados
            $("#editTipoEquipoModal input[name='marcas[]']").prop("checked", false);

            if (marcas) {
                const marcasSeleccionadas = marcas.split(",").map(marca => marca.trim());

                $("#editTipoEquipoModal input[name='marcas[]']").each(function () {
                    if (marcasSeleccionadas.includes($(this).next("label").text().trim())) {
                        $(this).prop("checked", true);
                    }
                });
            }

            // Configurar la acción del formulario
            $("#editTipoEquipoForm").attr("action", `/update_tipo_equipo/${id}`);

            // Abrir el modal
            $("#editTipoEquipoModal").modal("show");
        }

        $(this).val("");
    });
});
