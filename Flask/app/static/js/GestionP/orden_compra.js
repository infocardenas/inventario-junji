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
