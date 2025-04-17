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

    // Bloquear el campo "Estado Incidencia" si el estado actual es Cerrado, Equipo cambiado o Equipo reparado
    const estadosBloqueados = ["cerrado", "equipo cambiado", "equipo reparado"];
    if (estadosBloqueados.includes(estadoInc.toLowerCase())) {
        $("#edit_estadoIncidencia").prop("disabled", true);
        $("#edit_nombreIncidencia").prop("disabled", true);
        $("#edit_fechaIncidencia").prop("disabled", true);
        $("#edit_observacionIncidencia").prop("disabled", true);
    } else {
        $("#edit_estadoIncidencia").prop("disabled", false);
        $("#edit_nombreIncidencia").prop("disabled", false);
        $("#edit_fechaIncidencia").prop("disabled", false);
        $("#edit_observacionIncidencia").prop("disabled", false);
    }
      
      console.log("Editando incidencia ID:", idEquipoInc);
  });

    // ✅ Listener para detectar cambios en el estado de la incidencia
  $("#edit_estadoIncidencia").on("change", function () {
      const nuevoEstado = $(this).val(); // Obtener el nuevo estado seleccionado
      const idEquipo = $("#edit_idEquipo").val(); // Obtener el ID del equipo relacionado
      const estadosConfirmacion = ["cerrado", "equipo cambiado", "equipo reparado"];

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

      if(estadosConfirmacion.includes(nuevoEstado.toLowerCase())) {
          if (confirm("¿Estás seguro de que deseas cambiar el estado a " + nuevoEstado + "? Luego no podrás modificarlo.")) {
              // Aquí puedes realizar la acción adicional que necesites
              console.log("Estado cambiado a:", nuevoEstado);
          } else {
              // Si el usuario cancela, revertir el cambio en el select
              $(this).val($(this).data("estado-anterior"));
          }
      }
        // Guardar el estado anterior para revertir si es necesario
      $(this).data("estado-anterior", nuevoEstado);
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

