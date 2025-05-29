document.addEventListener("DOMContentLoaded", function () {
    const editButtons = document.querySelectorAll(".btn-edit");
    const editForm = document.getElementById("form_editOrdenCompraModal");

    editButtons.forEach(button => {
        button.addEventListener("click", function () {
            // Obtener datos del botón
            const id = this.dataset.id;
            const nombre = this.dataset.nombre;
            const fechaCompra = this.dataset.fechaCompra;
            const fechaFin = this.dataset.fechaFin;
            const tipo = this.dataset.tipo;
            const proveedor = this.dataset.proveedor;

            // Verificar qué valores están llegando
            console.log("ID Orden:", id);
            console.log("Nombre Orden:", nombre);
            console.log("Fecha Compra:", fechaCompra);
            console.log("Fecha Fin:", fechaFin);
            console.log("Tipo de Adquisición:", tipo);
            console.log("Proveedor:", proveedor);
            // Asignar valores al formulario del modal
            document.getElementById("edit_id_ordenc").value = id;
            document.getElementById("edit_nombre_ordenc").value = nombre;
            document.getElementById("edit_fecha_compra_ordenc").value = fechaCompra;
            document.getElementById("edit_fecha_fin_ordenc").value = fechaFin;
            document.getElementById("edit_nombre_tipo_adquisicion_ordenc").value = tipo;
            document.getElementById("edit_nombre_proveedor_ordenc").value = proveedor;

            // Actualizar la acción del formulario
            editForm.action = `/update_ordenc/${id}`;
        });
    });
});

$(document).ready(function () {


    $("#eliminarSeleccionados").on("click", function () {
        let seleccionados = $(".row-checkbox:checked").closest("tr").map(function () {
            return $(this).data("id");
        }).get();

        console.log("🔍 IDs seleccionados para eliminación:", seleccionados); // ✅ Depuración

        if (seleccionados.length === 0) {
            mostrarAlerta("⚠️ Debe seleccionar al menos una orden de compra para eliminar.", "warning");
            return;
        }

        $("#confirmDeleteModal").modal("show");

        $("#confirmDeleteBtn").off("click").on("click", function () {
            $("#confirmDeleteModal").modal("hide");

            $.ajax({
                url: "/delete_ordenc",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ ids: seleccionados }),
                success: function (response) {
                    console.log("✅ Respuesta del backend:", response);
                    mostrarAlerta(response.message, "success");
                    setTimeout(() => location.reload(), 1500);
                },
                error: function (xhr) {
                    let errorMsg = xhr.responseJSON?.message || "Error al eliminar las órdenes de compra.";
                    console.error("❌ Error del backend:", xhr.responseJSON);
                    mostrarAlerta(errorMsg, "danger");
                }
            });
        });
    });

    function mostrarAlerta(mensaje, tipo = "success") {
        let alertContainer = document.getElementById("alertContainer");

        // Verifica si el contenedor ya existe
        if (!alertContainer) {
            console.warn("⚠️ Contenedor de alertas no encontrado, creándolo dinámicamente...");
            document.body.insertAdjacentHTML("afterbegin", '<div id="alertContainer" class="alert-container"></div>');
            alertContainer = document.getElementById("alertContainer");
        }

        // Remueve cualquier alerta previa antes de agregar una nueva
        alertContainer.innerHTML = "";

        let alertaHTML = `
            <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
                ${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;

        alertContainer.innerHTML = alertaHTML;
        alertContainer.classList.remove("d-none");

        setTimeout(() => {
            alertContainer.classList.add("d-none");
            alertContainer.innerHTML = ""; // Limpia el contenido después de ocultarlo
        }, 5000);
    }

});



document.addEventListener("DOMContentLoaded", function () {
    let fechaCompraInput = document.getElementById("fecha_compra_ordenc");
    let fechaFinInput = document.getElementById("fecha_fin_ordenc");

    let fechaCompraEditInput = document.getElementById("edit_fecha_compra_ordenc");
    let fechaFinEditInput = document.getElementById("edit_fecha_fin_ordenc");

    // Obtener la fecha de hoy en formato YYYY-MM-DD
    let today = new Date();
    let todayStr = today.toISOString().split('T')[0];

    // **Establecer la fecha mínima en los campos de fecha**
    [fechaCompraInput, fechaFinInput, fechaCompraEditInput, fechaFinEditInput].forEach(input => {
        if (input) {
            input.setAttribute("min", todayStr);
        }
    });

    function validarFecha(input) {
        if (!input) return;
        let selectedDate = new Date(input.value);
        let dayOfWeek = selectedDate.getDay(); // 0 = Domingo, 6 = Sábado

        if (input.value < todayStr) {
            mostrarAlerta("❌ No puedes seleccionar una fecha anterior a hoy.", "warning");
            input.value = todayStr;
        } else if (dayOfWeek === 0 || dayOfWeek === 6) {
            mostrarAlerta("❌ No puedes seleccionar sábados ni domingos.", "warning");
            input.value = todayStr;
        }
    }

    // **Eventos para validar las fechas**
    [fechaCompraInput, fechaFinInput, fechaCompraEditInput, fechaFinEditInput].forEach(input => {
        if (input) {
            input.addEventListener("change", function () {
                validarFecha(input);
            });
        }
    });
    // **Validación de formularios antes de enviarlos**
    function validarFormulario(formId) {
        let form = document.getElementById(formId);
        let inputs = form.querySelectorAll("input[required], select[required]");
        let valido = true;
        let mensajeError = "";

        inputs.forEach(input => {
            if (!input.value.trim()) {
                valido = false;
                mensajeError += `⚠️ El campo "${input.previousElementSibling.textContent}" es obligatorio.<br>`;
            }
        });

        if (!valido) {
            mostrarAlerta(mensajeError, "warning");
        }

        return valido;
    }

    // **Evitar envío del formulario si hay campos vacíos**
    document.getElementById("addOrdenCompraForm").addEventListener("submit", function (e) {
        if (!validarFormulario("addOrdenCompraForm")) {
            e.preventDefault();
        }
    });

    document.getElementById("form_editOrdenCompraModal").addEventListener("submit", function (e) {
        if (!validarFormulario("form_editOrdenCompraModal")) {
            e.preventDefault();
        }
    });

});

// Funcion para ocultar o mostrar la fecha final en orden de compra
document.addEventListener("DOMContentLoaded", function () {
    // 📌 Elementos del formulario de agregar
    const selectAdquisicionAdd = document.getElementById("tipoAdquisicionSelect");
    const fechaFinContainerAdd = document.getElementById("fechaFinContainer");
    const fechaFinInputAdd = document.getElementById("fecha_fin_ordenc");

    // 📌 Elementos del formulario de edición
    const selectAdquisicionEdit = document.getElementById("edit_nombre_tipo_adquisicion_ordenc");
    const fechaFinContainerEdit = document.getElementById("editFechaFinContainer");
    const fechaFinInputEdit = document.getElementById("edit_fecha_fin_ordenc");

    // 📌 Función general para ocultar/mostrar la fecha final
    function toggleFechaFin(selectElement, fechaFinContainer, fechaFinInput) {
        const valorSeleccionado = selectElement.value;

        if (valorSeleccionado === "" || valorSeleccionado === "1") {
            // Ocultar fecha final si es Compra
            fechaFinContainer.style.display = "none";
            fechaFinInput.required = false;
            fechaFinInput.value = ""; // Limpiar su valor
        } else {
            // Mostrar fecha final si es Préstamo o Arriendo
            fechaFinContainer.style.display = "block";
            fechaFinInput.required = true;
        }
    }

    // 📌 Aplicar la función al cargar la página (para agregar)
    if (selectAdquisicionAdd) {
        toggleFechaFin(selectAdquisicionAdd, fechaFinContainerAdd, fechaFinInputAdd);
        selectAdquisicionAdd.addEventListener("change", function () {
            toggleFechaFin(selectAdquisicionAdd, fechaFinContainerAdd, fechaFinInputAdd);
        });
    }

    // 📌 Evento para abrir el modal de edición y configurar la visibilidad correcta
    document.querySelectorAll(".btn-edit").forEach(button => {
        button.addEventListener("click", function () {
            // Obtener datos del botón de edición
            const id = this.dataset.id;
            const nombre = this.dataset.nombre;
            const fechaCompra = this.dataset.fechaCompra;
            const fechaFin = this.dataset.fechaFin;
            const tipo = this.dataset.tipo; // Tipo de adquisición
            const proveedor = this.dataset.proveedor;

            // Asignar valores al formulario del modal
            document.getElementById("edit_id_ordenc").value = id;
            document.getElementById("edit_nombre_ordenc").value = nombre;
            document.getElementById("edit_fecha_compra_ordenc").value = fechaCompra;
            document.getElementById("edit_fecha_fin_ordenc").value = fechaFin;
            document.getElementById("edit_nombre_proveedor_ordenc").value = proveedor;
            document.getElementById("edit_nombre_tipo_adquisicion_ordenc").value = tipo;

            // 📌 Llamar a la función para decidir si la fecha final debe mostrarse
            toggleFechaFin(selectAdquisicionEdit, fechaFinContainerEdit, fechaFinInputEdit);
        });
    });

    // 📌 Evento para detectar cambios en el select de tipo de adquisición en edición
    if (selectAdquisicionEdit) {
        selectAdquisicionEdit.addEventListener("change", function () {
            toggleFechaFin(selectAdquisicionEdit, fechaFinContainerEdit, fechaFinInputEdit);
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const editFechaCompra = document.getElementById("edit_fecha_compra_ordenc");

    document.querySelectorAll(".btn-edit").forEach(button => {
        button.addEventListener("click", function () {
            const fechaGuardada = this.dataset.fechaCompra; // La fecha que ya tenía guardada
            const fechaHoy = new Date().toISOString().split("T")[0]; // Fecha de hoy en formato YYYY-MM-DD

            console.log("Fecha Guardada:", fechaGuardada);
            console.log("Fecha de Hoy:", fechaHoy);

            // Si la fecha guardada es anterior a hoy, se permite
            if (fechaGuardada < fechaHoy) {
                editFechaCompra.removeAttribute("min"); // Permite la fecha guardada aunque sea anterior
            } else {
                editFechaCompra.setAttribute("min", fechaHoy); // Si la fecha guardada es mayor, aplica validación normal
            }

            // Asignar la fecha guardada al campo
            editFechaCompra.value = fechaGuardada;
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("#myTableBody tr").forEach(row => {
        row.addEventListener("click", function (event) {
            // Evitar que el clic en el checkbox o botones de acción active/desactive el checkbox
            if (event.target.tagName === "INPUT" || event.target.tagName === "BUTTON" || event.target.tagName === "I") {
                return;
            }

            // Encontramos el checkbox dentro de la fila
            let checkbox = row.querySelector(".row-checkbox");

            if (checkbox) {
                // Alternar el estado del checkbox
                checkbox.checked = !checkbox.checked;
            }
        });
    });
});
