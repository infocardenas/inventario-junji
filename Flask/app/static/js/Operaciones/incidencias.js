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
  $(".btn-danger").on("click", function () {
      let incidenciaId = $(this).data("id"); // Obtener ID correcto
      console.log("Intentando eliminar incidencia ID:", incidenciaId);

      if (confirm("¿Estás seguro de que deseas eliminar esta incidencia?")) {
          // Crear formulario dinámico para enviar solicitud de eliminación
          let form = $("<form>", {
              method: "POST",
              action: "/incidencia/delete_incidencia/" + incidenciaId
          }).appendTo("body");

          form.submit(); // Enviar el formulario
      }
  });
});

// ✅ Función para limpiar datos antes de usarlos
function limpiarDato(dato) {
  return dato ? dato.toString().trim() : "";
}

