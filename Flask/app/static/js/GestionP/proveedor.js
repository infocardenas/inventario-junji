document.addEventListener("DOMContentLoaded", function () {
    const editProveedorForm = document.getElementById("editProveedorForm");
    const editIdProveedor = document.getElementById("edit_idProveedor");
    const editNombreProveedor = document.getElementById("edit_nombreProveedor");

    // Configurar el modal con datos dinámicos
    document.querySelectorAll(".edit-button").forEach(button => {
        button.addEventListener("click", function () {
            const idProveedor = this.dataset.id;
            const nombreProveedor = this.dataset.nombre;

            // Llenar el modal con los datos del proveedor
            editIdProveedor.value = idProveedor;
            editNombreProveedor.value = nombreProveedor;

            // Configurar la acción del formulario
            editProveedorForm.action = `/update_proveedor/${idProveedor}`;

            // Imprimir valores para depuración
            console.log("ID del proveedor:", idProveedor);
            console.log("Nombre del proveedor:", nombreProveedor);
            console.log("Action del formulario:", editProveedorForm.action);
        });
    });
});
