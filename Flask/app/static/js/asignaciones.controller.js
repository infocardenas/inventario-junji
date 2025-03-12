document.addEventListener("DOMContentLoaded", () => {
    refreshCheckboxListeners();

    const btnDevolver = document.getElementById("devolver-button");

    if (btnDevolver) {
        btnDevolver.addEventListener("click", () => {
            let checkboxes = document.querySelectorAll(".row-checkbox:checked");
            if (checkboxes.length === 0) {
                alert("Por favor, selecciona al menos un equipo para devolver.");
                return; // Evita abrir el modal
            }

            actualizarModalDevolucion();

            // Abrir el modal de confirmación
            let modal = new bootstrap.Modal(document.getElementById("modalConfirmarDevolucion"));
            modal.show();
        });
    }

    // Vincular la función de envío al botón "Continuar" dentro del modal
    const btnContinuar = document.getElementById("btnContinuarDevolucion");
    if (btnContinuar) {
        btnContinuar.addEventListener("click", devolverSeleccionados);
    }

    // Manejar el cambio de selección de checkboxes
    document.querySelectorAll(".row-checkbox").forEach(checkbox => {
        checkbox.addEventListener("change", function () {
            let idEquipoAsignacion = this.value;
            let rowModal = document.getElementById(`modal-row-${idEquipoAsignacion}`);
            let inputHidden = document.getElementById(`modal-input-${idEquipoAsignacion}`);

            if (this.checked) {
                if (rowModal) rowModal.style.display = "";
                if (inputHidden) inputHidden.style.display = "block";
            } else {
                if (rowModal) rowModal.style.display = "none";
                if (inputHidden) inputHidden.style.display = "none";
            }
            actualizarEstadoBotonFirmar();
        });
    });

    // Permitir seleccionar la fila al hacer clic en ella (sin afectar el checkbox directamente)
    document.querySelectorAll(".selectable-row").forEach(row => {
        row.addEventListener("click", function (event) {
            if (event.target.tagName === "INPUT" && event.target.type === "checkbox") return; // 1. Evitar cambio si se hace clic sobre un checkbox directamente
            if (event.target.closest("button") || event.target.closest("i")) return; // 2. Evitar cambio si el clic vino de un botón o ícono

            let checkbox = this.querySelector(".row-checkbox");
            checkbox.checked = !checkbox.checked;
            checkbox.dispatchEvent(new Event("change"));
        });
    });

    // Habilita/deshabilita el botón de devolver
    document.querySelectorAll(".row-checkbox").forEach(checkbox => {
        let idEquipoAsignacion = checkbox.value;
        let row = document.getElementById(`row-${idEquipoAsignacion}`);

        /* Si el equipo ya fue devuelto, deshabilitar el checkbox y marcarlo como devuelto
        if (checkbox.dataset.devuelto === "true") {
            checkbox.disabled = true;
            row.classList.add("equipo-devuelto"); // Clase visual para diferenciar equipos devueltos
        }
        */
        // Agregar evento para actualizar el estado del botón cuando cambia la selección
        checkbox.addEventListener("change", actualizarEstadoBotonDevolver);
    });

    // Llamar a la función al cargar la página para deshabilitar el botón si no hay equipos seleccionables
    actualizarEstadoBotonDevolver();

    // Funciones asociadas al manejo del botón de Descargar PDF
    const btnDescargarPDF = document.getElementById("descargar-PDF-button");
    const btnAsignaciones = document.getElementById("descargar-asignacion");
    const btnDevoluciones = document.getElementById("descargar-devolucion");
    const checkboxes = document.querySelectorAll(".row-checkbox");

    function actualizarEstadoBotonDescargarPDF() {
        // Filtra los checkboxes que están seleccionados
        let seleccionados = Array.from(checkboxes).filter(cb => cb.checked);

        if (seleccionados.length === 1) {
            let checkbox = seleccionados[0];
            let idAsignacion = checkbox.dataset.idAsignacion;
            let idDevolucion = checkbox.dataset.idDevolucion;

            btnDescargarPDF.removeAttribute("disabled");
            btnAsignaciones.classList.remove("disabled");
            btnAsignaciones.href = `/asignacion/descargar_pdf_asignacion/${idAsignacion}`;

            // Para la opción de devolución, se habilita solo si existe un idDevolucion válido
            if (idDevolucion && idDevolucion.trim() !== "") {
                btnDevoluciones.classList.remove("disabled");
                btnDevoluciones.href = `/asignacion/descargar_pdf_devolucion/${idDevolucion}`;
            } else {
                btnDevoluciones.classList.add("disabled");
                btnDevoluciones.removeAttribute("href");
            }
        } else {
            // Si no hay ninguno o hay más de uno, se deshabilitan ambos botones
            btnDescargarPDF.setAttribute("disabled", "true");
            btnAsignaciones.classList.add("disabled");
            btnAsignaciones.removeAttribute("href");
            btnDevoluciones.classList.add("disabled");
            btnDevoluciones.removeAttribute("href");
        }
    }

    // Actualiza el estado cada vez que cambia la selección de algún checkbox
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", actualizarEstadoBotonDescargarPDF);
    });

    actualizarEstadoBotonDescargarPDF();
    actualizarEstadoBotonFirmar();
    // Fin de funciones asociadas al manejo del botón de Descargar PDF
});

// Función que actualiza el modal con las asignaciones seleccionadas
function actualizarModalDevolucion() {
    let checkboxes = document.querySelectorAll(".row-checkbox:checked");

    checkboxes.forEach(checkbox => {
        let idEquipoAsignacion = checkbox.value;
        let rowModal = document.getElementById(`modal-row-${idEquipoAsignacion}`);
        let inputHidden = document.getElementById(`modal-input-${idEquipoAsignacion}`);

        if (rowModal) rowModal.style.display = "";  // Mostrar la fila en el modal
        if (inputHidden) inputHidden.style.display = "block"; // Mostrar input hidden
    });
}

// **Función para devolver equipos seleccionados**
function devolverSeleccionados() {
    let checkboxes = document.querySelectorAll(".row-checkbox:checked");
    let idsEquipos = [];

    checkboxes.forEach(checkbox => {
        idsEquipos.push(checkbox.value);
    });

    if (idsEquipos.length === 0) {
        alert("Por favor, selecciona al menos un equipo para devolver.");
        return;
    }

    // Crear el formulario y enviarlo
    let form = document.getElementById("formDevolver");

    // Limpiar cualquier input oculto previo
    document.querySelectorAll("#formDevolver input[name='equiposSeleccionados']").forEach(input => input.remove());

    idsEquipos.forEach(id => {
        let input = document.createElement("input");
        input.type = "hidden";
        input.name = "equiposSeleccionados";
        input.value = id;
        form.appendChild(input);
    });

    form.submit();
}

function actualizarEstadoBotonDevolver() {
    const checkboxes = document.querySelectorAll(".row-checkbox:checked");
    const btnDevolver = document.getElementById("devolver-button");

    let hayDevuelto = false; // Variable para saber si hay al menos un equipo ya devuelto
    let idAsignacionBase = null;
    let mismaAsignacion = true; // Variable para saber si todas las checkbox marcadas pertenecen a la misma asignación

    checkboxes.forEach((checkbox, index) => {
        // 1. Verificar si ya fue devuelto
        if (checkbox.dataset.devuelto === "true") {
            hayDevuelto = true;
        }

        // 2. Validar si comparten el mismo idAsignacion
        if (index === 0) {
            // Guardamos el idAsignacion del primer checkbox seleccionado
            idAsignacionBase = checkbox.dataset.idAsignacion;
        } else {
            // Comparamos con el primer idAsignacion
            if (checkbox.dataset.idAsignacion !== idAsignacionBase) {
                mismaAsignacion = false;
            }
        }
    });

    // Criterios para habilitar "Devolver":
    // a) No hay equipos devueltos.
    // b) Al menos un checkbox seleccionado.
    // c) Todas las checkboxes pertenecen a la misma asignación.
    if (!hayDevuelto && checkboxes.length > 0 && mismaAsignacion) {
        btnDevolver.removeAttribute("disabled");
    } else {
        btnDevolver.setAttribute("disabled", "true");
    }
}

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
    enableRowClick();
}

// ⬇ Funciones para seleccionar fila en la tabla de agregar asignación de equipo ⬇
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
// ⬆ Fin de funciones para seleccionar fila en la tabla de agregar asignación de equipo ⬆

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

function setTooltipText(element, newText) {
    $(element).attr("data-bs-title", newText);
    let tip = bootstrap.Tooltip.getInstance(element);
    if (tip) {
        tip.dispose(); // Destruye el tooltip previo
    }
    new bootstrap.Tooltip(element); // Crea uno nuevo con el texto actualizado
}
function actualizarEstadoBotonFirmar() {
    const checkboxes = document.querySelectorAll(".row-checkbox:checked");
    const btnFirmar = document.getElementById("firmar-button");
    const btnAsignacionFirmar = document.getElementById("documento-firmado-asignacion");
    const btnDevolucionFirmar = document.getElementById("documento-firmado-devolucion");

    if (checkboxes.length === 1) {
        let checkbox = checkboxes[0];
        let idAsignacion = checkbox.dataset.idAsignacion;
        let idDevolucion = checkbox.dataset.idDevolucion;

        // Habilitar el dropdown principal
        btnFirmar.removeAttribute("disabled");

        // Habilitar el botón de asignación
        btnAsignacionFirmar.classList.remove("disabled");
        btnAsignacionFirmar.href = `/asignacion/listar_pdf/${idAsignacion}`;

        // Habilitar el botón de devolución solo si ya se devolvió el equipo
        if (idDevolucion && idDevolucion.trim() !== "") {
            btnDevolucionFirmar.classList.remove("disabled");
            btnDevolucionFirmar.href = `/asignacion/listar_pdf/${idAsignacion}/devolver`;
        } else {
            btnDevolucionFirmar.classList.add("disabled");
            btnDevolucionFirmar.removeAttribute("href");
        }
    } else {
        // Deshabilitar todo si no hay exactamente una selección
        btnFirmar.setAttribute("disabled", "true");
        btnAsignacionFirmar.classList.add("disabled");
        btnAsignacionFirmar.removeAttribute("href");
        btnDevolucionFirmar.classList.add("disabled");
        btnDevolucionFirmar.removeAttribute("href");
    }
}


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
