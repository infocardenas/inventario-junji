

$(document).ready(function () {
    $(".edit-equipo-btn").on("click", async function () {
      // 1. Recibir datos
      const idEquipoInc = limpiarDato($(this).data("id"));
      const nombreInc = limpiarDato($(this).data("nombre"));
      const fechaInc = limpiarDato($(this).data("fecha"));
      const observacionInc = limpiarDato($(this).data("observacion"));
      

      $("#edit_idEquipo").val(idEquipoInc);
      console.log(idEquipoInc);
      $("#form_edit_incidencia").attr("action", `/incidencia/update_incidencia/${idEquipoInc}`);

      console.log(nombreInc);
      console.log(fechaInc);
      console.log(observacionInc);
      // 9. Rellenar otros campos
      $("#edit_nombreIncidencia").val(nombreInc);
      $("#edit_fechaIncidencia").val(fechaInc);
      $("#edit_observacionIncidencia").val(observacionInc);
    });
  });
