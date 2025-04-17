$(document).ready(function () {
  // ✅ Evento para editar incidencia (Abrir modal con datos correctos)
  $(".edit-equipo-btn").on("click", function () {
      const idEquipoInc = limpiarDato($(this).data("id"));
      const estadoInc = limpiarDato($(this).data("estado"));
      const nombreInc = limpiarDato($(this).data("nombre"));
      const fechaInc = limpiarDato($(this).data("fecha"));
      const observacionInc = limpiarDato($(this).data("observacion"));

      // Rellenar los campos del formulario modal
      $("#edit_idEquipo").val(idEquipoInc);
      $("#form_edit_incidencia").attr("action", `/incidencia/update_incidencia/${idEquipoInc}`);
      $("#edit_estadoIncidencia").val(estadoInc);
      $("#edit_nombreIncidencia").val(nombreInc);
      $("#edit_fechaIncidencia").val(fechaInc);
      $("#edit_observacionIncidencia").val(observacionInc);
      
      console.log("Editando incidencia ID:", idEquipoInc);
  });

    // ✅ Listener para detectar cambios en el estado de la incidencia
  $("#edit_estadoIncidencia").on("change", function () {
      const nuevoEstado = $(this).val(); // Obtener el nuevo estado seleccionado
      const idEquipo = $("#edit_idEquipo").val(); // Obtener el ID del equipo relacionado

      console.log("Nuevo estado de incidencia:", nuevoEstado);
      console.log("ID del equipo relacionado:", idEquipo);

      // Realizar una solicitud al servidor para actualizar el estado del equipo
      if (idEquipo && nuevoEstado) {
          $.ajax({
              url: `/update_estado/${idEquipo}`,
              method: "POST",
              data: { estado: nuevoEstado },
              success: function (response) {
                  console.log("Estado del equipo actualizado correctamente:", response);

              },
              error: function (error) {
                  console.error("Error al actualizar el estado del equipo:", error);

              }
          });
      }
  });

  // ✅ Evento para eliminar incidencia (elimina la incidencia correcta)
let incidenciaIdToDelete = null;
let deleteUrl = null;

  // Capturar el ID de la incidencia al abrir el modal
$(document).on("click", ".delete-button", function () {
      incidenciaIdToDelete = $(this).data("id");
      deleteUrl = $(this).data("url");
  
      console.log("Incidencia seleccionada para eliminar:", incidenciaIdToDelete);
  });
  
  // Manejar la confirmación de eliminación
  $(document).on("click", "#confirmDeleteButton", function () {
      if (deleteUrl) {
          // Crear un formulario dinámico para enviar la solicitud de eliminación
          let form = $("<form>", {
              method: "POST",
              action: deleteUrl
          }).appendTo("body");
  
          form.submit(); // Enviar el formulario
      }
  });

// ✅ Función para limpiar datos antes de usarlos
function limpiarDato(dato) {
  return dato ? dato.toString().trim() : "";
}


document.getElementById("form_add_incidencia").addEventListener("submit", function (event) {
    const selectedCheckbox = document.querySelector(".equipo-checkbox:checked");
    if (!selectedCheckbox) {
        event.preventDefault(); // Evita el envío del formulario
        alert("Por favor, selecciona un equipo.");
    } else {
        // Asigna el valor del checkbox seleccionado al campo oculto
        document.getElementById("idEquipo").value = selectedCheckbox.value;
    }
});

});