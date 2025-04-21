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

// ✅ Evento para abrir el modal de añadir incidencia
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

// Búsqueda dinámica
document.getElementById('searchEquipo').addEventListener('input', function () {
    const filter = this.value.toLowerCase();
    const rows = document.querySelectorAll('#equiposTable tr');

    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
    });
});

});