function handleActionChange(selectElement) {
    const selectedValue = selectElement.value; // Valor de la opción seleccionada
    const selectedRows = Array.from(document.querySelectorAll('.row-checkbox:checked')); // Checkboxes seleccionados

    if (selectedRows.length === 0) {
        MensajeGenericoModal("Sin selección", "Por favor, selecciona al menos una fila para realizar esta acción.");
        selectElement.value = ""; // Restablecer el select
        return;
    }

    // Obtener los IDs de las filas seleccionadas
    const selectedIds = selectedRows.map(checkbox => {
        const row = checkbox.closest('tr'); // Encuentra la fila padre
        return row.dataset.id; // Devuelve el ID de la fila
    });

    if (selectedValue === "edit") {
        if (selectedIds.length > 1) {
            MensajeGenericoModal(
                "Edición no permitida",
                "Solo puedes editar una fila a la vez. Selecciona una sola fila."
            );
        } else {
            const id = selectedIds[0];
            window.location.href = `/marca_equipo/edit_marca_equipo/${id}`; // Redirigir a la edición
        }
    } else if (selectedValue === "delete") {
        // Obtener los nombres de las marcas seleccionadas
        const selectedNames = selectedRows.map(checkbox => {
            const row = checkbox.closest('tr'); // Encuentra la fila padre
            return row.querySelector('td:nth-child(2)').innerText.trim(); // Obtiene el texto de la segunda celda
        });

        // Configurar el modal para confirmación de eliminación
        configureGenericModal(
            "Eliminar Marca",
            `¿Estás seguro de que deseas eliminar la/s marca/s: ${selectedNames.join(", ")}?`,
            `/marca_equipo/delete_marca_equipo/${selectedIds.join(",")}` // Ruta con los IDs seleccionados
        );

    }


    // Restablecer el select a su estado inicial
    selectElement.value = "";
}
