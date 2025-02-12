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

            // Limpiar error si hay al menos 1 equipo seleccionado
            const equiposSeleccionados = document.querySelectorAll('input[name="equiposAsignados[]"]').length;
            if (equiposSeleccionados > 0) {
                limpiarError($("#equiposContainer"));
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

$(document).ready(function () {
    // Validación cuando se intente enviar el formulario
    $(document).on("submit", "#form-asignacion-modal", function (e) {
        // Cantidad de equipos que se han agregado dinámicamente

        const equiposSeleccionados = document.querySelectorAll('input[name="equiposAsignados[]"]').length;

        if (equiposSeleccionados === 0) {
            e.preventDefault();
            // Apuntamos al contenedor #equiposContainer
            mostrarError($("#equiposContainer"), "Debes asignar al menos un equipo");
        } else {
            limpiarError($("#equiposContainer"));
        }
    });

    $("#addAsignacionModal").on("hidden.bs.modal", function () {
        limpiarError($("#equiposContainer"));

        // Desmarcar todos los checkboxes
        $(".equipo-checkbox").prop("checked", false);

        // Eliminar los inputs ocultos que se agregaron para equipos seleccionados
        $("#selectedEquipos").empty();
    });
});

$(document).ready(function () {
    let listaFuncionarios = JSON.parse($("#listaFuncionarios").attr("data-funcionarios"));

    // Referencias a elementos
    let label = $("#label-funcionario");
    let contenedorNombre = $("#contenedorNombre");
    let contenedorRut = $("#contenedorRut");
    let nombreInput = $("#nombre_funcionario");
    let rutInput = $("#rut_funcionario");
    let sugerenciasDiv = $("#sugerencias_funcionarios");
    let toggleBtn = $("#toggleFuncionario");

    // 1. Alternar entre Nombre y RUT
    toggleBtn.on("click", function () {
        if (contenedorNombre.is(":visible")) {
            contenedorNombre.hide();
            sugerenciasDiv.hide(); // Cerrar autocompletado si estaba abierto
            contenedorRut.show();
            rutInput.focus();
            limpiarError(rutInput);
            setTooltipText(this, "Buscar por nombre");
            label.html('RUT del funcionario<span style="color: red; margin-left: 5px">*</span>');
        } else {
            contenedorRut.hide();
            contenedorNombre.show();
            nombreInput.focus();
            limpiarError(nombreInput);
            setTooltipText(this, "Buscar por RUT");
            label.html('Nombre del funcionario<span style="color: red; margin-left: 5px">*</span>');
        }
    });

    function setTooltipText(element, newText) {
        $(element).attr("data-bs-title", newText);
        // Re-inicializar
        let tip = bootstrap.Tooltip.getInstance(element);
        if (tip) {
            tip.dispose(); // Destruye el tooltip previo
        }
        new bootstrap.Tooltip(element); // Crea uno nuevo con el texto actualizado
    }

    // 2. Autocompletado en el input de nombre
    nombreInput.on("input", function () {
        let input = $(this).val().trim().toLowerCase();

        if (input.length === 0) {
            sugerenciasDiv.hide();
            return;
        }

        // Filtrar funcionarios
        let coincidencias = listaFuncionarios.filter(f => f.nombre.toLowerCase().includes(input));

        if (coincidencias.length > 0) {
            let listaHTML = coincidencias.map(funcionario =>
                `<button type="button" class="list-group-item list-group-item-action sugerencia-item"
                         data-nombre="${funcionario.nombre}" data-rut="${funcionario.rut}">
                    ${funcionario.nombre}
                </button>`
            ).join("");

            sugerenciasDiv.html(listaHTML).show();
        } else {
            sugerenciasDiv.html("<p class='list-group-item text-danger'>No encontrado</p>").show();
        }
    });

    // 3. Seleccionar un funcionario desde las sugerencias
    $(document).on("click", ".sugerencia-item", function () {
        let nombre = $(this).data("nombre");
        let rutCompleto = $(this).data("rut");
        let [rutSinDV, dv] = rutCompleto.split("-");

        $("#nombre_funcionario").val(nombre);

        // Llenar el input de RUT sin guion ni DV
        $("#rut_funcionario").val(rutSinDV);

        // Llenar el campo DV
        $("#rut_verificador").val(dv);

        // Si usas el hidden "rut_completo"
        $("#rut_completo").val(rutCompleto);

        $("#sugerencias_funcionarios").hide();
        limpiarError($("#nombre_funcionario"));
    });

    // 4. Ocultar sugerencias si se hace clic fuera
    $(document).click(function (event) {
        if (!$(event.target).closest("#nombre_funcionario, #sugerencias_funcionarios").length) {
            sugerenciasDiv.hide();
        }
    });

    // 5. Validación antes de enviar el formulario
    $(document).on("submit", "#form-asignacion-modal", function (event) {
        let esValido = true;

        // Si el contenedor de Nombre está visible, validamos el nombre
        if (contenedorNombre.is(":visible")) {
            let nombreIngresado = nombreInput.val().trim().toLowerCase();
            let nombreValido = listaFuncionarios.some(f => f.nombre.toLowerCase() === nombreIngresado);

            if (!nombreValido) {
                mostrarError(nombreInput, "No se ha encontrado el funcionario");
                esValido = false;
            } else {
                limpiarError(nombreInput);
            }
        }

        if (!esValido) {
            event.preventDefault();
        }
    });
});
