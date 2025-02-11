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
$(document).ready(function () {
  function validarSoloNumeros(inputField) {
    const regex = /^[0-9]+$/; // Solo permite números positivos
    const input = inputField.val().trim();

    if (input.length === 0) {
      limpiarError(inputField);
      return true;
    }

    if (!regex.test(input)) {
      mostrarError(inputField, "Solo se permiten números");
      return false;
    } else {
      limpiarError(inputField);
    }

    return true;
  }

  // Validar en tiempo real cuando el usuario escribe
  $(document).on("input", ".validar-numero", function () {
    validarSoloNumeros($(this));
  });

  // Validación en el envío del formulario
  $(document).on("submit", "form", function (event) {
    let esValido = true;
    const form = $(this);

    form.find(".validar-numero").each(function () {
      if (!validarSoloNumeros($(this))) {
        esValido = false;
      }
    });

    if (!esValido) {
      event.preventDefault();
    }
  });

  // Función para mostrar error correctamente
  function mostrarError(inputField, mensaje) {
    let errorMessage = inputField.siblings(".text-error-message"); // Busca el div de error en el mismo contenedor

    if (errorMessage.length === 0) {
      errorMessage = $('<div class="text-error-message text-danger"></div>'); // Si no existe, lo crea
      inputField.after(errorMessage); // Lo coloca justo debajo del input
    }

    errorMessage.text(mensaje).show(); // Muestra el mensaje de error
    inputField.addClass("border border-danger"); // Agrega borde rojo al input
  }

  // Función para limpiar el mensaje de error
  function limpiarError(inputField) {
    let errorMessage = inputField.siblings(".text-error-message"); // Busca el div de error
    errorMessage.hide(); // Oculta el mensaje
    inputField.removeClass("border border-danger"); // Elimina borde rojo del input
  }
});

$(document).ready(function () {
  function validarNumerosYLetras(inputField) {
    const regex = /^[a-zA-Z0-9]+$/; // Permite solo letras y números
    const input = inputField.val().trim();

    if (input.length === 0) {
      limpiarError(inputField);
      return true;
    }

    if (!regex.test(input)) {
      mostrarError(inputField, "Solo se permiten letras y números");
      return false;
    } else {
      limpiarError(inputField);
    }

    return true;
  }

  // Validar en tiempo real cuando el usuario escribe
  $(document).on("input", ".validar-numeros-letras", function () {
    validarNumerosYLetras($(this));
  });

  // Validación al enviar el formulario
  $(document).on("submit", "form", function (event) {
    let esValido = true;
    const form = $(this);

    form.find(".validar-numeros-letras").each(function () {
      if (!validarNumerosYLetras($(this))) {
        esValido = false;
      }
    });

    if (!esValido) {
      event.preventDefault();
    }
  });

  // Función para mostrar error correctamente
  function mostrarError(inputField, mensaje) {
    let errorMessage = inputField.siblings(".text-error-message");

    if (errorMessage.length === 0) {
      errorMessage = $('<div class="text-error-message text-danger"></div>');
      inputField.after(errorMessage);
    }

    errorMessage.text(mensaje).show();
    inputField.addClass("border border-danger");
  }

  // Función para limpiar el mensaje de error
  function limpiarError(inputField) {
    let errorMessage = inputField.siblings(".text-error-message");
    errorMessage.hide();
    inputField.removeClass("border border-danger");
  }
});
$(document).ready(function () {
  function validarMAC(inputField) {
    // Expresión regular para validar direcciones MAC con ":" o "-" como separadores
    const regex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$|^[0-9A-Fa-f]{12}$/;
    const input = inputField.val().trim();

    if (input.length === 0) {
      limpiarError(inputField);
      return true;
    }

    if (!regex.test(input)) {
      mostrarError(inputField, "Ingrese una dirección MAC válida (Ej: AA:BB:CC:DD:EE:FF)");
      return false;
    } else {
      limpiarError(inputField);
    }

    return true;
  }

  // Validar en tiempo real cuando el usuario escribe
  $(document).on("input", ".validar-mac", function () {
    validarMAC($(this));
  });

  // Validación en el envío del formulario
  $(document).on("submit", "form", function (event) {
    let esValido = true;
    const form = $(this);

    form.find(".validar-mac").each(function () {
      if (!validarMAC($(this))) {
        esValido = false;
      }
    });

    if (!esValido) {
      event.preventDefault();
    }
  });

  // Función para mostrar error correctamente
  function mostrarError(inputField, mensaje) {
    let errorMessage = inputField.siblings(".text-error-message");

    if (errorMessage.length === 0) {
      errorMessage = $('<div class="text-error-message text-danger"></div>');
      inputField.after(errorMessage);
    }

    errorMessage.text(mensaje).show();
    inputField.addClass("border border-danger");
  }

  // Función para limpiar el mensaje de error
  function limpiarError(inputField) {
    let errorMessage = inputField.siblings(".text-error-message");
    errorMessage.hide();
    inputField.removeClass("border border-danger");
  }
});

$(document).ready(function () {
  // Función para limitar caracteres en campos específicos
  function limitarCaracteres(inputField, maxLength) {
    let input = inputField.val();
    if (input.length > maxLength) {
      inputField.val(input.substring(0, maxLength)); // Corta el exceso
    }
  }

  // Aplicar el límite en los campos específicos
  $(document).on("input", "#imei", function () {
    limitarCaracteres($(this), 16);
  });

  $(document).on("input", "#mac", function () {
    limitarCaracteres($(this), 17); // MAC con separadores es de 17 caracteres máximo
  });

  $(document).on("input", "#telefono", function () {
    limitarCaracteres($(this), 15);
  });
});
