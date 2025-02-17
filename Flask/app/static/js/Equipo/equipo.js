//Desde aqui comienzan las funciones para llenar los select dinamicos para marca, tipo y modelo
//Ojo las rutas backend estan en el archivo modelo_equipo.py
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
// Aca terminan las funciones para los select dinamicos

// Funcion para mostrar o ocultar los campos para el tipo equipo telefono
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

  //Maneja boton de eliminar
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
// Función para evitar que aparezca "None"
function limpiarDato(dato) {
  return (dato === undefined || dato === null || dato === "None") ? "" : dato;
}
// Funcion para llenar el modal de edit con los datos del equipo que se esta editando
$(document).ready(function () {
  $(".edit-equipo-btn").on("click", async function () {
    // 1. Recibir datos
    const idEquipo = limpiarDato($(this).data("id"));
    const idMarca = limpiarDato($(this).data("marca"));
    const tipoId = limpiarDato($(this).data("tipo"));
    const modeloId = limpiarDato($(this).data("modelo"));
    const codigoInventario = limpiarDato($(this).data("codigo"));
    const unidad = limpiarDato($(this).data("unidad"));
    const orden = limpiarDato($(this).data("orden"));
    const serie = limpiarDato($(this).data("serie"));
    const proveedor = limpiarDato($(this).data("proveedor"));
    const observacion = limpiarDato($(this).data("observacion"));
    const mac = limpiarDato($(this).data("mac"));
    const imei = limpiarDato($(this).data("imei"));
    const numero = limpiarDato($(this).data("numero"));
    const estado = limpiarDato($(this).data("estado"));
    // Llenar el hidden input con el estado
    $("#edit_estado_equipo").val(estado);

    // Llenar el hidden input con el id del equipo
    $("#edit_id_equipo").val(idEquipo);

    $("#editEquipoForm").attr("action", `/update_equipo/${idEquipo}`);
    // LLamar y cargar select de marca, tipo y modelo
    await cargarMarcasEdit();
    $("#edit_marcaSelect").val(idMarca);

    await cargarTiposEdit();
    $("#edit_tipoSelect").val(tipoId);
    mostrarCamposTelefonoEdit();

    await cargarModelosEdit();
    $("#edit_modeloSelect").val(modeloId);

    // 9. Rellenar otros campos
    $("#edit_codigo_inventario").val(codigoInventario);
    $("#edit_codigo_Unidad").val(unidad);
    $("#edit_orden_compra").val(orden);
    $("#edit_numero_serie").val(serie);
    $("#edit_codigoproveedor").val(proveedor);
    $("#edit_observacion_equipo").val(observacion);
    $("#edit_mac").val(mac);
    $("#edit_imei").val(imei);
    $("#edit_numero").val(numero);
  });
});


// ==================== [EDITAR] Cargar Marcas ====================
async function cargarMarcasEdit() {
  // 1. Llamar a la misma ruta donde obtienes las marcas
  const response = await fetch("/get_marcas");
  const marcas = await response.json();

  // 2. Rellenar el select de marca
  const marcaSelect = document.getElementById("edit_marcaSelect");
  marcaSelect.innerHTML = '<option value="">Seleccione una marca</option>';
  marcas.forEach((marca) => {
    const option = document.createElement("option");
    option.value = marca.idMarca_Equipo;
    option.textContent = marca.nombreMarcaEquipo;
    marcaSelect.appendChild(option);
  });
  console.log(marcas)
}

// ==================== [EDITAR] Cargar Tipos ====================
async function cargarTiposEdit() {
  const marcaId = document.getElementById("edit_marcaSelect").value;

  const tipoSelect = document.getElementById("edit_tipoSelect");
  tipoSelect.innerHTML = '<option value="">Seleccione un tipo</option>';

  if (!marcaId) {
    console.warn("No hay marca seleccionada; se detiene cargarTiposEdit()");
    return;
  }
  const urlTipos = `/get_tipos/${marcaId}`;
  const response = await fetch(urlTipos);

  if (!response.ok) {
    console.error("Error al obtener tipos. Status:", response.status);
    return;
  }
  const tipos = await response.json();

  tipos.forEach((tipo) => {
    const option = document.createElement("option");
    // Asegúrate de que las propiedades del JSON coincidan
    option.value = tipo.idTipo_equipo;
    option.textContent = tipo.nombreTipo_equipo;
    tipoSelect.appendChild(option);
  });

  // Limpia modeloSelect para forzar nueva selección
  const modeloSelect = document.getElementById("edit_modeloSelect");
  modeloSelect.innerHTML = '<option value="">Seleccione un modelo</option>';
}
async function cargarModelosEdit() {
  const marcaId = document.getElementById("edit_marcaSelect").value;
  const tipoId = document.getElementById("edit_tipoSelect").value;

  const modeloSelect = document.getElementById("edit_modeloSelect");
  modeloSelect.innerHTML = '<option value="">Seleccione un modelo</option>';
  if (!marcaId || !tipoId) {
    console.warn("Faltan marcaId o tipoId; no se buscarán modelos.");
    return;
  }
  const urlModelos = `/get_modelos/${marcaId}/${tipoId}`;
  const response = await fetch(urlModelos);

  if (!response.ok) {
    console.error("Error al obtener modelos. Status:", response.status);
    return;
  }
  const modelos = await response.json();

  modelos.forEach((modelo) => {
    const option = document.createElement("option");
    option.value = modelo.idModelo_Equipo;
    option.textContent = modelo.nombreModeloequipo;
    modeloSelect.appendChild(option);
  });
}

// // Funcion para manejar el boton actualizar 
// document.addEventListener("DOMContentLoaded", function () {
//   document.getElementById("editEquipoForm").addEventListener("submit", async function (event) {
//       event.preventDefault(); // Evita el envío automático del formulario

//       // Cerrar el modal inmediatamente
//       let modal = bootstrap.Modal.getInstance(document.getElementById("editEquipoModal"));
//       modal.hide();

//       setTimeout(() => {
//           document.querySelectorAll(".modal-backdrop").forEach(el => el.remove());
//           document.body.classList.remove("modal-open"); // Evita que el body quede bloqueado
//       }, 100);

//       // Obtener el ID del equipo
//       const idEquipo = document.getElementById("edit_id_equipo").value;

//       // Capturar los datos del formulario
//       const datos = {
//           codigo_inventario: document.getElementById("edit_codigo_inventario").value.trim(),
//           numero_serie: document.getElementById("edit_numero_serie").value.trim(),
//           observacion_equipo: document.getElementById("edit_observacion_equipo").value.trim(),
//           codigoproveedor: document.getElementById("edit_codigoproveedor").value.trim(),
//           mac: document.getElementById("edit_mac").value.trim(),
//           imei: document.getElementById("edit_imei").value.trim(),
//           numero: document.getElementById("edit_numero").value.trim(),
//           codigo_Unidad: document.getElementById("edit_codigo_Unidad").value,
//           nombre_orden_compra: document.getElementById("edit_orden_compra").value,
//           nombre_modelo_equipo: document.getElementById("edit_modeloSelect").selectedOptions[0].textContent,
//           nombreTipo_equipo: document.getElementById("edit_tipoSelect").selectedOptions[0].textContent,
//           nombre_estado_equipo: document.getElementById("edit_estado_equipo").value
//       };

//       try {
//           // Enviar los datos al backend en segundo plano
//           const response = await fetch(`/update_equipo/${idEquipo}`, {
//               method: "POST",
//               headers: { "Content-Type": "application/json" },
//               body: JSON.stringify(datos),
//           });

//           if (!response.ok) {
//               console.error("Error al actualizar el equipo.");
//               return;
//           }

//           // Retrasar la recarga para darle tiempo a que se muestre la alerta flash
//           setTimeout(() => {
//             window.location.reload();
//           }, 2000); // 2000 milisegundos = 2 segundos
//       } catch (error) {
//           console.error("Error al actualizar el equipo:", error);
//       }
//   });
// });

function mostrarCamposTelefonoEdit() {
  const tipoSelect = document.getElementById("edit_tipoSelect");
  const camposTelefono = document.getElementById("edit_camposTelefono");

  if (!tipoSelect) return; // Evita errores si no existe el select
  if (tipoSelect.selectedIndex < 0) return; // No hay opción seleccionada

  // Lee el texto de la opción seleccionada
  const tipoTexto = tipoSelect.options[tipoSelect.selectedIndex].text.toLowerCase();

  // Verifica si es "teléfono" (con o sin tilde)
  if (tipoTexto === "teléfono" || tipoTexto === "telefono") {
    camposTelefono.style.display = "block";
  } else {
    camposTelefono.style.display = "none";
  }
}


document.getElementById("edit_tipoSelect").addEventListener("change", function() {
  mostrarCamposTelefonoEdit();
});



// funcion para manejar la incidencia 
document.addEventListener("DOMContentLoaded", function () {
  var incidenciaModal = document.getElementById('incidenciaModal');
  incidenciaModal.addEventListener('show.bs.modal', function (event) {
      var button = event.relatedTarget;
      var idEquipo = button.getAttribute('data-id');
      var inputEquipo = incidenciaModal.querySelector('#idEquipo');
      inputEquipo.value = idEquipo;
      console.log(idEquipo);
  });
});