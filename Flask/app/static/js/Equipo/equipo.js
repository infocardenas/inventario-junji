//Desde aqui comienzan las funciones para llenar los select dinamicos para marca, tipo y modelo
//Ojo las rutas backend estan en el archivo modelo_equipo.py
document.addEventListener("DOMContentLoaded", async () => {
  try {
    await cargarMarcas(); // Llenar el selector de marcas
  } catch (error) {
    console.error("Error al cargar marcas:", error);
  }
});


function buscarEquipos(page = 1) {
  const query = document.getElementById("buscador_equipo").value.toLowerCase(); // Obtener el término de búsqueda

  fetch(`/buscar_equipos?q=${encodeURIComponent(query)}&page=${page}`) // Realizar la solicitud al backend
    .then(response => {
      if (!response.ok) {
        throw new Error("Error al buscar equipos");
      }
      return response.json();
    })
    .then(data => {
      actualizarTabla(data.equipos); // Actualizar la tabla con los datos recibidos
      actualizarPaginacion(data.total_pages, data.current_page, query, data.visible_pages); // Actualizar la paginación
      guardarIdsVisibles(data.equipos); // Guardar los IDs visibles para exportar
    })
    .catch(error => console.error("Error al buscar equipos:", error));
}

function guardarIdsVisibles(equipos) {
  const visibleIds = equipos.map(equipo => equipo.idEquipo); // Extraer los IDs de los equipos visibles

  // Guardar los IDs visibles en un atributo del botón de exportar búsqueda
  const exportButton = document.getElementById("exportarBusqueda");
  if (exportButton) {
    exportButton.setAttribute("data-ids", visibleIds.join(","));
  }

  console.log("IDs visibles:", visibleIds); // Depuración
}

function exportarBusqueda() {
  const exportButton = document.getElementById("exportarBusqueda");
  const ids = exportButton.getAttribute("data-ids");

  if (!ids) {
    alert("No hay resultados para exportar.");
    return;
  }

  // Redirigir al endpoint de exportar con los IDs visibles
  window.location.href = `/crear_excel?ids=${encodeURIComponent(ids)}`;
}

function actualizarTabla(equipos) {
  const tbody = document.getElementById("myTableBody");
  tbody.innerHTML = ""; // Limpiar la tabla

  if (equipos.length === 0) {
    tbody.innerHTML = '<tr><td colspan="10" class="text-center">No hay datos disponibles.</td></tr>';
    return;
  }

  equipos.forEach(equipo => {
    const row = document.createElement("tr");
    row.setAttribute("data-id", equipo.idEquipo);
    row.innerHTML = `
      <td><input type="checkbox" class="checkbox-table row-checkbox no-delete-value"></td>
      <td>${equipo.Cod_inventarioEquipo}</td>
      <td>${equipo.Num_serieEquipo}</td>
      <td>${equipo.nombreEstado_equipo}</td>
      <td>${equipo.nombreFuncionario || '-'}</td>
      <td>${equipo.codigoproveedor_equipo || '-'}</td>
      <td>${equipo.nombreUnidad}</td>
      <td>${equipo.nombreTipo_equipo}</td>
      <td>${equipo.nombreModeloequipo}</td>
      <td>
        <a href="/equipo_detalles/${equipo.idEquipo}" class="btn button-info">
          <i class="bi bi-eye-fill"></i>
        </a>
        <button class="btn btn-warning edit-equipo-btn" data-bs-toggle="modal"
          data-bs-target="#editEquipoModal"
          data-id="${equipo.idEquipo}"
          data-codigo="${equipo.Cod_inventarioEquipo}"
          data-serie="${equipo.Num_serieEquipo}"
          data-observacion="${equipo.ObservacionEquipo || ''}"
          data-unidad="${equipo.idUnidad || ''}"
          data-orden="${equipo.idOrden_compra || ''}"
          data-marca="${equipo.idMarca_Equipo || ''}"
          data-tipo="${equipo.idTipo_equipo || ''}"
          data-modelo="${equipo.idModelo_equipo || ''}"
          data-proveedor="${equipo.codigoproveedor_equipo || ''}"
          data-mac="${equipo.macEquipo || ''}"
          data-imei="${equipo.imeiEquipo || ''}"
          data-numero="${equipo.numerotelefonicoEquipo || ''}"
          data-estado="${equipo.idEstado_equipo || ''}">
          <i class="bi bi-pencil-square"></i>
        </button>
      </td>
    `;
    tbody.appendChild(row);
  });

  // Reconfigurar eventos para los botones de edición
  configurarEventosEdicion();
}

function configurarEventosEdicion() {
  document.querySelectorAll(".edit-equipo-btn").forEach(button => {
    button.addEventListener("click", function () {
      const id = this.getAttribute("data-id");
      const marca = this.getAttribute("data-marca");
      const tipo = this.getAttribute("data-tipo");
      const modelo = this.getAttribute("data-modelo");

      // Cargar marcas, tipos y modelos en el modal
      cargarMarcas(marca);
      cargarTipos(marca, tipo);
      cargarModelos(marca, tipo, modelo);

      // Rellenar otros campos del modal
      document.getElementById("edit_id_equipo").value = id;
      document.getElementById("edit_codigo_inventario").value = this.getAttribute("data-codigo");
      document.getElementById("edit_numero_serie").value = this.getAttribute("data-serie");
      document.getElementById("edit_observacion_equipo").value = this.getAttribute("data-observacion");
      document.getElementById("edit_codigo_Unidad").value = this.getAttribute("data-unidad");
      document.getElementById("edit_orden_compra").value = this.getAttribute("data-orden");
      document.getElementById("edit_codigoproveedor").value = this.getAttribute("data-proveedor");
      document.getElementById("edit_mac").value = this.getAttribute("data-mac");
      document.getElementById("edit_imei").value = this.getAttribute("data-imei");
      document.getElementById("edit_numero").value = this.getAttribute("data-numero");
      document.getElementById("edit_estado_equipo").value = this.getAttribute("data-estado");

      function cargarMarcas(selectedMarca) {
        fetch("/get_marcas")
          .then(response => response.json())
          .then(data => {
            const marcaSelect = document.getElementById("edit_marcaSelect");
            marcaSelect.innerHTML = '<option value="">Seleccione una marca</option>';
            data.forEach(marca => {
              const option = document.createElement("option");
              option.value = marca.idMarca_Equipo;
              option.textContent = marca.nombreMarcaEquipo;
              if (marca.idMarca_Equipo == selectedMarca) {
                option.selected = true;
              }
              marcaSelect.appendChild(option);
            });
          });
      }
      function cargarTipos(marcaId, selectedTipo) {
        fetch(`/get_tipos/${marcaId}`)
          .then(response => response.json())
          .then(data => {
            const tipoSelect = document.getElementById("edit_tipoSelect");
            tipoSelect.innerHTML = '<option value="">Seleccione un tipo</option>';
            data.forEach(tipo => {
              const option = document.createElement("option");
              option.value = tipo.idTipo_equipo;
              option.textContent = tipo.nombreTipo_equipo;
              if (tipo.idTipo_equipo == selectedTipo) {
                option.selected = true;
              }
              tipoSelect.appendChild(option);
            });
          });
      }
      function cargarModelos(marcaId, tipoId, selectedModelo) {
        fetch(`/get_modelos/${marcaId}/${tipoId}`)
          .then(response => response.json())
          .then(data => {
            const modeloSelect = document.getElementById("edit_modeloSelect");
            modeloSelect.innerHTML = '<option value="">Seleccione un modelo</option>';
            data.forEach(modelo => {
              const option = document.createElement("option");
              option.value = modelo.idModelo_equipo;
              option.textContent = modelo.nombreModeloequipo;
              if (modelo.idModelo_equipo == selectedModelo) {
                option.selected = true;
              }
              modeloSelect.appendChild(option);
            });
          });
      }
    });
  });
}

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

function actualizarPaginacion(totalPages, currentPage, query, visiblePages) {
  const paginationContainer = document.querySelector(".pagination-container ul");
  paginationContainer.innerHTML = ""; // Limpiar la paginación

  visiblePages.forEach(page => {
    const li = document.createElement("li");
    if (page === "...") {
      li.className = "page-item disabled";
      li.innerHTML = `<span class="page-link">...</span>`;
    } else {
      li.className = `page-item ${page === currentPage ? "active" : ""}`;
      li.innerHTML = `
        <a class="page-link" href="#" onclick="buscarEquipos(${page})">${page}</a>
      `;
    }
    paginationContainer.appendChild(li);
  });

  // Botón "Anterior"
  if (currentPage > 1) {
    const prevLi = document.createElement("li");
    prevLi.className = "page-item";
    prevLi.innerHTML = `
      <a class="page-link" href="#" onclick="buscarEquipos(${currentPage - 1})">Anterior</a>
    `;
    paginationContainer.insertBefore(prevLi, paginationContainer.firstChild);
  }

  // Botón "Siguiente"
  if (currentPage < totalPages) {
    const nextLi = document.createElement("li");
    nextLi.className = "page-item";
    nextLi.innerHTML = `
      <a class="page-link" href="#" onclick="buscarEquipos(${currentPage + 1})">Siguiente</a>
    `;
    paginationContainer.appendChild(nextLi);
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

document.addEventListener("DOMContentLoaded", function () {
  var tipoSelect = document.getElementById("tipoSelect");
  if (tipoSelect) {
      tipoSelect.addEventListener("change", manejarCamposTelefono);
  } else {
      console.warn("El elemento #tipoSelect no se encontró en el DOM.");
  }
});


  //Maneja boton de eliminar equipo
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

        // Configurar y mostrar el modal de confirmación
        configureGenericModal(
            "Confirmar Eliminación",
            "¿Estás seguro de que deseas eliminar los equipos seleccionados?",
            `/delete_equipo/${ids.join(",")}`
        );
    });
});

// Manejar boton de eliminar incidencia
$(document).ready(function () {
  $("#delete-incidencia-button").on("click", function () {
      // Obtener el ID de la incidencia (ya que es un único elemento)
      const id = $(this).data("id");
      if (!id) {
          alert("No se encontró la incidencia.");
          return;
      }

      // Configurar y mostrar el modal de confirmación con la URL de eliminación
      configureGenericModal(
          "Confirmar Eliminación",
          "¿Estás seguro de que deseas eliminar esta incidencia?",
          `/incidencia/delete_incidencia/${id}`
      );
  });
});




//Redireccion al modulo de asignacion desde equipos
$(document).ready(function () {
  $("#assign-button").on("click", function () {
      window.location.href = "/asignacion"; // Cambia "/asignacion" por la URL correcta
  });
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
    // Expresión regular para direcciones MAC válidas
    const regex = /^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$|^[0-9A-Fa-f]{12}$/;
    const input = inputField.val().trim();

    if (input.length === 0) {
      limpiarError(inputField);
      return true; // Permite el campo vacío
    }

    if (!regex.test(input)) {
      mostrarError(inputField, "⚠️ Ingrese una dirección MAC válida (Ej: AA:BB:CC:DD:EE:FF o AABBCCDDEEFF)");
      return false;
    }

    limpiarError(inputField);
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
      event.preventDefault(); // Evita el envío si hay errores
    }
  });

  // Función para mostrar error correctamente
  function mostrarError(inputField, mensaje) {
    let errorMessage = inputField.siblings(".text-error-message");

    if (errorMessage.length === 0) {
      errorMessage = $('<div class="text-error-message text-danger small mt-1"></div>');
      inputField.after(errorMessage);
    }

    errorMessage.text(mensaje).fadeIn();
    inputField.addClass("is-invalid");
  }

  // Función para limpiar el mensaje de error
  function limpiarError(inputField) {
    let errorMessage = inputField.siblings(".text-error-message");
    errorMessage.fadeOut();
    inputField.removeClass("is-invalid");
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
    $("#edit_estado_equipo").val(estado);
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



function setIdEquipoInModal() {
  // Obtener todos los checkboxes seleccionados
  var selectedCheckboxes = document.querySelectorAll('.row-checkbox:checked');
  console.log("Cantidad de checkboxes seleccionados:", selectedCheckboxes.length);
  
  // Si no hay exactamente uno seleccionado, alerta y sale
  if (selectedCheckboxes.length !== 1) {
      alert("Por favor, seleccione un equipo.");
      return;
  }
  
  // Obtener la fila y extraer el id del equipo
  var row = selectedCheckboxes[0].closest('tr');
  console.log("Fila seleccionada:", row);
  var idEquipo = row.getAttribute('data-id');
  console.log("Valor obtenido del data-id:", idEquipo);
  
  // Asignar el id al input oculto dentro del modal
  var inputEquipo = document.querySelector('#add_incidencia #idEquipo');
  if (inputEquipo) {
      inputEquipo.value = idEquipo;
      console.log("idEquipo asignado en el input:", inputEquipo.value);
  } else {
      console.log("No se encontró el input #idEquipo dentro del modal.");
  }
  
  // Abrir el modal manualmente usando la API de Bootstrap
  var modalElement = document.getElementById('add_incidencia');
  var modal = bootstrap.Modal.getOrCreateInstance(modalElement);
  modal.show();
}


document.addEventListener("DOMContentLoaded", function () {
  var checkboxes = document.querySelectorAll(".row-checkbox");
  var incidenciaButton = document.getElementById("incidencia-button");
  var deleteButton = document.getElementById("delete-selected-button");

  function actualizarEstadoBotones() {
      var selectedCheckboxes = document.querySelectorAll(".row-checkbox:checked");
      var seleccionados = selectedCheckboxes.length;

      // Habilita el botón de incidencia solo si hay exactamente 1 checkbox seleccionado
      if (seleccionados === 1) {
          incidenciaButton.removeAttribute("disabled");
      } else {
          incidenciaButton.setAttribute("disabled", "true");
      }

      // Habilita el botón de eliminar si hay al menos 1 checkbox seleccionado
      if (seleccionados > 0) {
          deleteButton.removeAttribute("disabled");
      } else {
          deleteButton.setAttribute("disabled", "true");
      }
  }

  // Agregar eventos a cada checkbox para actualizar el estado de los botones
  checkboxes.forEach(function (checkbox) {
      checkbox.addEventListener("change", actualizarEstadoBotones);
  });

  // Ejecutar al cargar la página por si hay valores previos
  actualizarEstadoBotones();
});


  // Espera a que el DOM esté completamente cargado
  document.addEventListener("DOMContentLoaded", function() {
    // Selecciona todas las filas del cuerpo de la tabla
    const rows = document.querySelectorAll("#myTableBody tr");
    
    rows.forEach(row => {
      row.addEventListener("click", function(e) {
        // Evita que se active el toggle si se hace clic en elementos interactivos
        const tag = e.target.tagName.toLowerCase();
        if (tag === "input" || tag === "a" || tag === "button") {
          return;
        }
        // Busca el checkbox dentro de la fila y alterna su estado
        const checkbox = row.querySelector("input.row-checkbox");
        if (checkbox) {
          checkbox.checked = !checkbox.checked;
          // Dispara el evento 'change' para que se ejecuten otros manejadores
          checkbox.dispatchEvent(new Event('change'));
        }
      });
    });
  });


  function exportarBusqueda() {
    let button = document.getElementById("exportarBusqueda");
    let ids = button.getAttribute("data-ids");
    
    if (ids) {
      window.location.href = `/crear_excel?ids=${ids}`;
    } else {
      alert("No hay datos visibles para exportar.");
    }
  }
  