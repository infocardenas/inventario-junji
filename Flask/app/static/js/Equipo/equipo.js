document.addEventListener("DOMContentLoaded", async () => {
  try {
    await cargarMarcas(); // Llenar el selector de marcas
  } catch (error) {
    onsole.error("Error al cargar marcas:", error);
  }
});

async function cargarMarcas() {
  const response = await fetch("/get_marcas");
  const marcas = await response.json();
  const marcaSelect = document.getElementById("marcaSelect");
  marcaSelect.innerHTML = '<option value="">Seleccione una marca</option>';
  marcas.forEach((marca) => {
    const option = document.createElement("option");
    option.value = marca.idMarca_Equipo;
    option.textContent = marca.nombreMarcaEquipo;
    marcaSelect.appendChild(option);
  });
}

async function cargarTipos() {
  const marcaId = document.getElementById("marcaSelect").value;
  const tipoSelect = document.getElementById("tipoSelect");
  tipoSelect.innerHTML = '<option value="">Seleccione un tipo</option>';

  if (marcaId) {
    const response = await fetch(`/get_tipos/${marcaId}`);
    const tipos = await response.json();

    tipos.forEach((tipo) => {
      const option = document.createElement("option");
      option.value = tipo.idTipo_equipo;
      option.textContent = tipo.nombreTipo_equipo;
      tipoSelect.appendChild(option);
    });
  }

  const modeloSelect = document.getElementById("modeloSelect");
  modeloSelect.innerHTML = '<option value="">Seleccione un modelo</option>';
}

async function cargarModelos() {
  console.log("cargarModelos llamado");
  const marcaId = document.getElementById("marcaSelect").value;
  const tipoId = document.getElementById("tipoSelect").value;
  const modeloSelect = document.getElementById("modeloSelect");
  modeloSelect.innerHTML = '<option value="">Seleccione un modelo</option>';

  if (marcaId && tipoId) {
    const response = await fetch(`/get_modelos/${marcaId}/${tipoId}`);
    const modelos = await response.json();
    console.log("Modelos recibidos:", modelos);

    modelos.forEach((modelo) => {
      const option = document.createElement("option");
      option.value = modelo.idModelo_Equipo;
      option.textContent = modelo.nombreModeloequipo;
      modeloSelect.appendChild(option);
    });
  }
}



function actualizarModeloSeleccionado() {
  const modeloSelect = document.getElementById("modeloSelect");
  const modeloInput = document.getElementById("modelo_para_equipo");

  // Asegúrate de que el modelo seleccionado se copie en el input oculto
  if (modeloSelect && modeloInput) {
    modeloInput.value = modeloSelect.value;
  }
}

function manejarCamposTelefono() {
  const tipoSelect = document.getElementById("tipoSelect");
  const camposTelefono = document.getElementById("camposTelefono");

  // Mostrar u ocultar los campos si el tipo seleccionado es "Teléfono"
  if (
    tipoSelect.options[tipoSelect.selectedIndex].text.toLowerCase() ===
    "telefono"
  ) {
    camposTelefono.style.display = "block";
  } else {
    camposTelefono.style.display = "none";
  }
}

// Escucha el cambio en el selector de tipo
document
  .getElementById("tipoSelect")
  .addEventListener("change", manejarCamposTelefono);

  $(document).ready(function () {
    $("#delete-selected-button").on("click", function () {
        // Obtener los IDs de las filas seleccionadas
        const selectedRows = $(".row-checkbox:checked").closest("tr");
        if (!selectedRows.length) {
            alert("Por favor, selecciona al menos una fila para eliminar.");
            return;
        }

        const ids = selectedRows.map(function () {
            return $(this).data("id");
        }).get();

        // Confirmar eliminación
        const confirmation = confirm("¿Estás seguro de que deseas eliminar los equipos seleccionados?");
        if (!confirmation) {
            return;
        }

        // Redirigir a la URL de eliminación con los IDs seleccionados
        window.location.href = `/delete_equipo/${ids.join(",")}`;
    });
});

$(document).ready(function () {
  // Función para actualizar el estado de los botones
  function updateButtonStates() {
      // Obtener las filas seleccionadas
      const selectedRows = $(".row-checkbox:checked").closest("tr");

      // Si no hay filas seleccionadas, deshabilitar ambos botones
      if (!selectedRows.length) {
          $("#assign-button").prop("disabled", true);
          $("#return-button").prop("disabled", true);
          return;
      }

      // Obtener los estados de los equipos seleccionados
      const estados = selectedRows.map(function () {
          return $(this).find("td:nth-child(4)").text().trim(); // Cambiar índice según la columna de estado
      }).get();

      // Habilitar o deshabilitar botones según los estados
      const allSinAsignar = estados.every((estado) => estado === "SIN ASIGNAR");
      const allEnUso = estados.every((estado) => estado === "EN USO");

      $("#assign-button").prop("disabled", !allSinAsignar); // Habilitar solo si todos son "SIN ASIGNAR"
      $("#return-button").prop("disabled", !allEnUso);     // Habilitar solo si todos son "EN USO"
  }

  // Actualizar botones al cambiar checkboxes
  $(".row-checkbox").on("change", updateButtonStates);

  // Acción del botón Asignar
  $("#assign-button").on("click", function () {
      const selectedRow = $(".row-checkbox:checked").closest("tr").first();
      const id = selectedRow.data("id");
      window.location.href = `/add_asignacion/${id}`;
  });

  // Acción del botón Devolver
  $("#return-button").on("click", function () {
      const selectedRow = $(".row-checkbox:checked").closest("tr").first();
      const id = selectedRow.data("id");
      window.location.href = `/asignacion/devolver_uno/${id}`;
  });

  // Deshabilitar botones al cargar la página
  updateButtonStates();
});

document.addEventListener("DOMContentLoaded", function () {
    const editButtons = document.querySelectorAll(".edit-equipo-btn");

    editButtons.forEach(button => {
        button.addEventListener("click", function () {
            // Precargar datos en los inputs
            document.getElementById("edit_codigo_inventario").value = this.getAttribute("data-codigo");
            document.getElementById("edit_numero_serie").value = this.getAttribute("data-serie");
            document.getElementById("edit_codigo_Unidad").value = this.getAttribute("data-unidad");
            document.getElementById("edit_observacion_equipo").value = this.getAttribute("data-observacion");

            // Seleccionar Marca, Tipo y Modelo
            document.getElementById("edit_marcaSelect").value = this.getAttribute("data-marca");
            document.getElementById("edit_tipoSelect").value = this.getAttribute("data-tipo");
            document.getElementById("edit_modeloSelect").value = this.getAttribute("data-modelo");

            // Mostrar datos de teléfono si es un teléfono
            let tipoEquipo = this.getAttribute("data-tipo").toLowerCase();
            if (tipoEquipo.includes("teléfono") || tipoEquipo.includes("telefono")) {
                document.getElementById("edit_mac").value = this.getAttribute("data-mac");
                document.getElementById("edit_imei").value = this.getAttribute("data-imei");
                document.getElementById("edit_numero").value = this.getAttribute("data-numero");
                document.getElementById("camposTelefonoEdit").style.display = "block";
            } else {
                document.getElementById("camposTelefonoEdit").style.display = "none";
            }
        });
    });
});

// Cargar tipos al cambiar la marca
function cargarTiposEdit() {
    let marcaId = document.getElementById("edit_marcaSelect").value;
    // Aquí deberías llenar el select con los tipos según la marca seleccionada
}

// Cargar modelos al cambiar el tipo
function cargarModelosEdit() {
    let tipoId = document.getElementById("edit_tipoSelect").value;
    // Aquí deberías llenar el select con los modelos según el tipo seleccionado
}


