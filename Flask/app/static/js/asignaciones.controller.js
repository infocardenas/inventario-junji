document.addEventListener("DOMContentLoaded", () => {
        refreshCheckboxListeners();
});

    // Función para actualizar listeners de checkboxes
    function refreshCheckboxListeners() {
    const equipoCheckboxes = document.querySelectorAll('.equipo-checkbox');
    const selectedEquiposDiv = document.getElementById('selectedEquipos');

    equipoCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const equipoId = this.value;

            if (this.checked) {
                // Agregar input oculto con el equipo seleccionado
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'equiposAsignados[]';
                hiddenInput.value = equipoId;
                hiddenInput.id = `equipo-hidden-${equipoId}`;
                selectedEquiposDiv.appendChild(hiddenInput);
            } else {
                // Remover input oculto si se desmarca
                const hiddenInput = document.getElementById(`equipo-hidden-${equipoId}`);
                if (hiddenInput) {
                    hiddenInput.remove();
                }
            }
        });
    });

    // Permitir clic en toda la fila para seleccionar el checkbox
    enableRowClick();
}

    // Permite seleccionar checkbox haciendo clic en la fila
    function enableRowClick() {
    const rows = document.querySelectorAll('#equiposTable tr');

    rows.forEach(row => {
        row.removeEventListener('click', rowClickHandler);
    row.addEventListener('click', rowClickHandler);
    });
}

    function rowClickHandler(event) {
    // Evitar que el evento se dispare si el clic es sobre el checkbox
    if (event.target.tagName === 'INPUT' && event.target.type === 'checkbox') return;

    // Encontrar el checkbox en la fila y alternar su estado
    const checkbox = this.querySelector('.equipo-checkbox');
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
    checkbox.dispatchEvent(new Event('change')); // Disparar evento 'change' manualmente
    }
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