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
  const queryInput = document.getElementById("buscador_equipo");
  // Si el input no existe en la página actual, no hacer nada (protección)
  if (!queryInput) return;
  const query = queryInput.value.toLowerCase();

  fetch(`/buscar_equipos?q=${encodeURIComponent(query)}&page=${page}`)
    .then(response => {
      if (!response.ok) {
        throw new Error("Error al buscar equipos");
      }
      return response.json();
    })
    .then(data => {
      actualizarTabla(data.equipos);
      actualizarPaginacion(data.total_pages, data.current_page, query, data.visible_pages);
      guardarIdsVisibles(data.equipos);

      // Reconfigurar TODOS los event listeners de la tabla después de actualizarla
      configurarTodosLosEventListenersDeTabla();
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
  if (!tbody) return; // Protección si la tabla no existe
  tbody.innerHTML = "";

  if (equipos.length === 0) {
    tbody.innerHTML = '<tr><td colspan="10" class="text-center">No hay datos disponibles.</td></tr>';
    return;
  }

  equipos.forEach(equipo => {
    const row = document.createElement("tr");
    row.setAttribute("data-id", equipo.idEquipo);
    // El innerHTML de la fila es el mismo que tenías
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

// En equipo.js - función global para el modal de AGREGAR
async function cargarModelos() {
  console.log("cargarModelos llamado");
  const marcaId = document.getElementById("marcaSelect").value;
  const tipoId = document.getElementById("tipoSelect").value;
  const modeloSelect = document.getElementById("modeloSelect");
  modeloSelect.innerHTML = '<option value="">Seleccione un modelo</option>';

  if (marcaId && tipoId) {
    const response = await fetch(`/get_modelos/${marcaId}/${tipoId}`);
    const modelos = await response.json();
    console.log("Modelos recibidos para AGREGAR:", modelos);

    modelos.forEach((modelo) => {
      const option = document.createElement("option");
      option.value = modelo.idModelo_Equipo; // CORRECTO (debe ser 'E' mayúscula)
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


document.getElementById("edit_tipoSelect").addEventListener("change", function () {
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
document.addEventListener("DOMContentLoaded", function () {
  // Selecciona todas las filas del cuerpo de la tabla
  const rows = document.querySelectorAll("#myTableBody tr");

  rows.forEach(row => {
    row.addEventListener("click", function (e) {
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

// --- Funciones para cargar selects en el MODAL DE EDICIÓN ---
function _cargarMarcasModalEdit(selectedMarca) {
  const marcaSelect = document.getElementById("edit_marcaSelect");
  if (!marcaSelect) return;

  fetch("/get_marcas")
    .then(response => response.json())
    .then(data => {
      marcaSelect.innerHTML = '<option value="">Seleccione una marca</option>';
      data.forEach(marca => {
        const option = document.createElement("option");
        option.value = marca.idMarca_Equipo;
        option.textContent = marca.nombreMarcaEquipo;
        if (String(marca.idMarca_Equipo) === String(selectedMarca)) { // Comparación más robusta
          option.selected = true;
        }
        marcaSelect.appendChild(option);
      });
      // Si hay una marca preseleccionada, cargar sus tipos
      if (selectedMarca) {
        // Obtener el tipo original que estaba guardado en el botón y pasarlo
        const tipoOriginal = marcaSelect.closest('.modal-body').querySelector('#edit_tipoSelect').dataset.tipoOriginal;
        _cargarTiposModalEdit(selectedMarca, tipoOriginal);
      } else { // Si no hay marca seleccionada, limpiar tipos y modelos
        _cargarTiposModalEdit(null, null);
      }
    });
}

function _cargarTiposModalEdit(marcaId, selectedTipo) {
  const tipoSelect = document.getElementById("edit_tipoSelect");
  const modeloSelect = document.getElementById("edit_modeloSelect");
  if (!tipoSelect || !modeloSelect) return;

  tipoSelect.innerHTML = '<option value="">Seleccione un tipo</option>'; // Limpiar tipos
  modeloSelect.innerHTML = '<option value="">Seleccione un modelo</option>'; // Limpiar modelos

  if (!marcaId) { // Si no hay marca, deshabilitar y salir
    tipoSelect.disabled = true;
    modeloSelect.disabled = true;
    mostrarCamposTelefonoEdit(); // Actualizar visibilidad campos de teléfono
    return;
  }
  tipoSelect.disabled = false;

  fetch(`/get_tipos/${marcaId}`)
    .then(response => response.json())
    .then(data => {
      data.forEach(tipo => {
        const option = document.createElement("option");
        option.value = tipo.idTipo_equipo;
        option.textContent = tipo.nombreTipo_equipo;
        if (String(tipo.idTipo_equipo) === String(selectedTipo)) {
          option.selected = true;
        }
        tipoSelect.appendChild(option);
      });
      // Si hay un tipo preseleccionado, cargar sus modelos
      if (selectedTipo) {
        const modeloOriginal = modeloSelect.dataset.modeloOriginal;
        _cargarModelosModalEdit(marcaId, selectedTipo, modeloOriginal);
      } else {
        modeloSelect.disabled = true;
      }
      mostrarCamposTelefonoEdit(); // Actualizar visibilidad campos de teléfono
    });
}

// En equipo.js - dentro de la estructura propuesta en mi respuesta anterior
function _cargarModelosModalEdit(marcaId, tipoId, selectedModelo) {
  const modeloSelect = document.getElementById("edit_modeloSelect");
  if (!modeloSelect) return;

  modeloSelect.innerHTML = '<option value="">Seleccione un modelo</option>';

  if (!marcaId || !tipoId) {
    modeloSelect.disabled = true;
    return;
  }
  modeloSelect.disabled = false;

  fetch(`/get_modelos/${marcaId}/${tipoId}`)
    .then(response => response.json())
    .then(data => {
      data.forEach(modelo => {
        const option = document.createElement("option");
        option.value = modelo.idModelo_Equipo; // CORRECCIÓN AQUÍ (debe ser 'E' mayúscula)
        option.textContent = modelo.nombreModeloequipo;
        if (String(modelo.idModelo_Equipo) === String(selectedModelo)) { // Comparar con 'E' mayúscula
          option.selected = true;
        }
        modeloSelect.appendChild(option);
      });
    });
}

function configurarEventosEdicion() {
  document.querySelectorAll("#myTableBody .edit-equipo-btn").forEach(button => {
    // Simple check to avoid double listeners if this function is ever called without table refresh
    if (button.dataset.listenerAttached === 'true') return;

    button.addEventListener("click", function () {
      const id = this.getAttribute("data-id");
      const marca = limpiarDato(this.getAttribute("data-marca")); // Ensure empty fields are filled with empty strings
      const tipo = limpiarDato(this.getAttribute("data-tipo"));
      const modelo = limpiarDato(this.getAttribute("data-modelo"));

      // Guardar los IDs originales para la carga en cascada de selects
      const tipoSelect = document.getElementById("edit_tipoSelect");
      if (tipoSelect) tipoSelect.dataset.tipoOriginal = tipo;
      const modeloSelect = document.getElementById("edit_modeloSelect");
      if (modeloSelect) modeloSelect.dataset.modeloOriginal = modelo;

      // Iniciar carga en cascada de selects para el modal de EDICIÓN
      _cargarMarcasModalEdit(marca);
      // Las funciones _cargarTiposModalEdit y _cargarModelosModalEdit se llamarán en cascada desde _cargarMarcasModalEdit

      // Rellenar otros campos del modal
      document.getElementById("edit_id_equipo").value = id;
      document.getElementById("edit_codigo_inventario").value = limpiarDato(this.getAttribute("data-codigo"));
      document.getElementById("edit_numero_serie").value = limpiarDato(this.getAttribute("data-serie"));
      document.getElementById("edit_observacion_equipo").value = limpiarDato(this.getAttribute("data-observacion"));
      document.getElementById("edit_codigo_Unidad").value = limpiarDato(this.getAttribute("data-unidad"));
      document.getElementById("edit_orden_compra").value = limpiarDato(this.getAttribute("data-orden"));
      document.getElementById("edit_codigoproveedor").value = limpiarDato(this.getAttribute("data-proveedor"));
      document.getElementById("edit_mac").value = limpiarDato(this.getAttribute("data-mac"));
      document.getElementById("edit_imei").value = limpiarDato(this.getAttribute("data-imei"));
      document.getElementById("edit_numero").value = limpiarDato(this.getAttribute("data-numero"));
      document.getElementById("edit_estado_equipo").value = limpiarDato(this.getAttribute("data-estado"));

      // Actualizar el action del formulario de edición
      const editForm = document.getElementById("editEquipoForm");
      if (editForm) {
        editForm.action = `/update_equipo/${id}`;
      }
    });
    button.dataset.listenerAttached = 'true';
  });
}

function limpiarDato(dato) {
  return (dato === undefined || dato === null || dato === "None") ? "" : dato;
}

function configurarEventosCheckbox() {
  const checkboxes = document.querySelectorAll("#myTableBody .row-checkbox");
  checkboxes.forEach(function (checkbox) {
    if (checkbox.dataset.listenerAttached === 'true') return;
    checkbox.addEventListener("change", actualizarEstadoBotonesGlobales);
    checkbox.dataset.listenerAttached = 'true';
  });
}

function configurarClickEnFila() {
  const rows = document.querySelectorAll("#myTableBody tr");
  rows.forEach(row => {
    if (row.dataset.listenerAttached === 'true') return;
    row.addEventListener("click", function (e) {
      const tag = e.target.tagName.toLowerCase();
      // No activar si se hizo clic directamente en un input, botón, o enlace dentro de la fila
      if (tag === "input" || tag === "a" || tag === "button" || e.target.closest('button') || e.target.closest('a')) {
        return;
      }
      const checkbox = row.querySelector("input.row-checkbox");
      if (checkbox) {
        checkbox.checked = !checkbox.checked;
        checkbox.dispatchEvent(new Event('change')); // Para que se actualicen los botones globales
      }
    });
    row.dataset.listenerAttached = 'true';
  });
}

function actualizarEstadoBotonesGlobales() {
  var selectedCheckboxes = document.querySelectorAll("#myTableBody .row-checkbox:checked");
  var seleccionados = selectedCheckboxes.length;
  const incidenciaButton = document.getElementById("incidencia-button");
  const deleteButton = document.getElementById("delete-selected-button");

  if (incidenciaButton) {
    incidenciaButton.disabled = (seleccionados !== 1);
  }
  if (deleteButton) {
    deleteButton.disabled = (seleccionados === 0);
  }
}

// Función unificada para configurar todos los listeners de la tabla
function configurarTodosLosEventListenersDeTabla() {
  configurarEventosEdicion();
  configurarEventosCheckbox();
  configurarClickEnFila();
  actualizarEstadoBotonesGlobales(); // Llamar para establecer el estado inicial de los botones
}


// --- Event Listeners Globales (se configuran una vez) ---
document.addEventListener('DOMContentLoaded', async () => {
  // Carga inicial de marcas para el modal de AGREGAR
  try {
    // La función global cargarMarcas() es para el modal de agregar y ya está definida.
    // Se llama con onchange desde el HTML o cuando se abre el modal.
    // Aquí podemos llamar a cargarMarcas() para poblar el select la primera vez.
    if (document.getElementById("marcaSelect")) { // Solo si existe el select del modal de agregar
      await cargarMarcas();
    }
  } catch (error) {
    console.error("Error al cargar marcas iniciales para el modal de agregar:", error);
  }

  // Listener para el buscador
  const buscadorEquipo = document.getElementById('buscador_equipo');
  if (buscadorEquipo) {
    buscadorEquipo.addEventListener('input', () => buscarEquipos(1));
  }

  // Listener para exportar búsqueda
  const exportarBusquedaBtn = document.getElementById('exportarBusqueda');
  if (exportarBusquedaBtn) {
    exportarBusquedaBtn.addEventListener('click', exportarBusqueda); // exportarBusqueda ya está definida
  }

  // Listener para el botón de asignar global (Toolbar)
  const assignButton = document.getElementById("assign-button");
  if (assignButton) {
    assignButton.addEventListener("click", function () {
      window.location.href = "/asignacion";
    });
  }

  // Listener para el botón de incidencia global (Toolbar)
  const incidenciaButtonGlobal = document.getElementById("incidencia-button");
  if (incidenciaButtonGlobal) {
    incidenciaButtonGlobal.addEventListener("click", setIdEquipoInModal); // setIdEquipoInModal ya está definida
  }

  // Listener para el botón de eliminar seleccionados global (Toolbar)
  // (Reemplaza el $(document).ready para este botón)
  const deleteSelectedButton = document.getElementById("delete-selected-button");
  if (deleteSelectedButton) {
    deleteSelectedButton.addEventListener("click", function () {
      const selectedRowsCheckboxes = document.querySelectorAll("#myTableBody .row-checkbox:checked");
      if (!selectedRowsCheckboxes.length) {
        alert("Por favor, selecciona al menos una fila para eliminar.");
        return;
      }
      const ids = Array.from(selectedRowsCheckboxes).map(function (checkbox) {
        return checkbox.closest("tr").getAttribute("data-id");
      });

      // Usar configureGenericModal si está disponible (de main.js)
      if (typeof configureGenericModal === "function") {
        configureGenericModal(
          "Confirmar Eliminación",
          "¿Estás seguro de que deseas eliminar los equipos seleccionados?",
          `/delete_equipo/${ids.join(",")}` // Flask necesita poder manejar esta ruta con múltiples IDs
        );
      } else { // Fallback por si main.js o la función no carga
        if (confirm("¿Estás seguro de que deseas eliminar los equipos seleccionados?")) {
          window.location.href = `/delete_equipo/${ids.join(",")}`;
        }
      }
    });
  }

  // Listener para el checkbox "Todo" en el encabezado de la tabla
  const thTodo = document.querySelector("#tablaEquipo > thead > tr > th.checkbox-column");
  if (thTodo) {
    thTodo.addEventListener('click', function (e) {
      // Evitar que el click en el th active el sortTable si está en el mismo th
      if (e.target.tagName.toLowerCase() === 'i') return;

      const checkboxesEnPagina = document.querySelectorAll("#myTableBody .row-checkbox");
      // Determinar si todos están ya marcados para invertir la selección
      let todosMarcadosEnPagina = checkboxesEnPagina.length > 0; // Asumir que sí si hay checkboxes
      checkboxesEnPagina.forEach(cb => { if (!cb.checked) todosMarcadosEnPagina = false; });

      checkboxesEnPagina.forEach(cb => {
        cb.checked = !todosMarcadosEnPagina;
        cb.dispatchEvent(new Event('change')); // Disparar evento change
      });
    });
  }

  // Configurar listeners de la tabla para la carga inicial de la página
  // (si la tabla se llena con Jinja2 al principio)
  configurarTodosLosEventListenersDeTabla();

  // Selects dependientes en el modal de EDICIÓN
  const editMarcaSelect = document.getElementById('edit_marcaSelect');
  if (editMarcaSelect) {
    editMarcaSelect.addEventListener('change', function () {
      // Al cambiar la marca, se limpian y recargan los tipos. El modelo se limpiará/recargará desde cargarTipos.
      _cargarTiposModalEdit(this.value, null);
    });
  }

  const editTipoSelect = document.getElementById('edit_tipoSelect');
  if (editTipoSelect) {
    editTipoSelect.addEventListener('change', function () {
      const marcaId = document.getElementById('edit_marcaSelect').value;
      // Al cambiar el tipo, se limpian y recargan los modelos.
      _cargarModelosModalEdit(marcaId, this.value, null);
      mostrarCamposTelefonoEdit(); // Para el modal de edición, actualizar campos de teléfono
    });
  }

  // Selects dependientes en el modal de AGREGAR (ya definidos con onchange en HTML, pero podrías moverlos aquí)
  // Ejemplo:
  // const addMarcaSelect = document.getElementById('marcaSelect');
  // if (addMarcaSelect) {
  //     addMarcaSelect.addEventListener('change', cargarTipos); // cargarTipos es tu función global
  // }
  // const addTipoSelect = document.getElementById('tipoSelect');
  // if (addTipoSelect) {
  //     addTipoSelect.addEventListener('change', cargarModelos); // cargarModelos es tu función global
  //     addTipoSelect.addEventListener('change', manejarCamposTelefono); // manejarCamposTelefono es tu función global
  // }
  // const addModeloSelect = document.getElementById('modeloSelect');
  // if (addModeloSelect) {
  //     addModeloSelect.addEventListener('change', actualizarModeloSeleccionado); // actualizarModeloSeleccionado es tu función global
  // }
});
