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
  $(document).on("click", ".delete-button", function () {
    // Obtener el ID y la URL del botón
    const incidenciaId = $(this).data("id");
    const url = $(this).data("url");

    console.log("Intentando eliminar incidencia ID:", incidenciaId);

    // Confirmar la eliminación (opcional, puedes eliminar esta parte si no quieres confirmación)
    const confirmMessage = $(this).data("message") || "¿Estás seguro de que deseas eliminar esta incidencia?";
    if (!confirm(confirmMessage)) {
        return; // Si el usuario cancela, no hacer nada
    }

    // Crear un formulario dinámico para enviar la solicitud de eliminación
    let form = $("<form>", {
        method: "POST",
        action: url
    }).appendTo("body");

    form.submit(); // Enviar el formulario
});

// ✅ Función para limpiar datos antes de usarlos
function limpiarDato(dato) {
  return dato ? dato.toString().trim() : "";
}

