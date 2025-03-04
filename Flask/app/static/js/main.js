$(document).ready(function () {
  $('[data-bs-toggle="tooltip"]').tooltip();
});

function navigateTo(url) {
  window.location.href = url;
}

function mostrarError(inputField, mensaje) {
  const errorMessage = inputField.closest(".mb-3").find(".text-error-message");
  errorMessage.text(mensaje).show(); // Mostrar el mensaje de error

  // Verifica si el campo está dentro de un contenedor con la clase .highlight-container
  const highlightContainer = inputField.closest(".highlight-container");

  if (highlightContainer.length) {
    highlightContainer.css({ outline: "2px solid red", "outline-offset": "-2px" });
  } else {
    inputField.css({ outline: "2px solid red", "outline-offset": "-2px" });
  }
}

function limpiarError(inputField) {
  const errorMessage = inputField.closest(".mb-3").find(".text-error-message");
  errorMessage.hide(); // Ocultar el mensaje de error

  // Verifica si el campo está dentro de un contenedor con la clase .highlight-container
  const highlightContainer = inputField.closest(".highlight-container");

  if (highlightContainer.length) {
    highlightContainer.css({ outline: "none", "outline-offset": "0px" });
  } else {
    inputField.css({ outline: "none", "outline-offset": "0px" });
  }
}


// Limpia los valores de todos los inputs, selects y textareas dentro del modal
function limpiarInputsEnModal(modal) {
  if ($(modal).hasClass("no-limpiar-inputs")) {
    return;
  }
  $(modal).find("input, select, textarea").each(function () {
    const element = $(this);

    if (!element.hasClass("no-delete-value")) {
      if (element.is("input") || element.is("textarea")) {
        element.val("");
      } else if (element.is("select")) {
        element.prop("selectedIndex", 0);
      }
    }

    if (element.is("input[type='checkbox']")) {
      element.prop("checked", false);
    }
  });
}

function limpiarErroresEnModal(modal) {
  // Oculta todos los mensajes de error del modal
  $(modal).find(".text-error-message").each(function () {
    $(this).hide();
  });
  $(modal).find("input, select, textarea").css({ outline: "none", "outline-offset": "0px" });
  $(modal).find(".equipos-asignados-table").css("border", "1px solid #ddd"); // Estilo exclusivo para la tabla de asignaciones
}

$(document).ready(function () {
  $("#addAsignacionModal").on("show.bs.modal", function () {
    fechaPorDefecto(); // Establecer la fecha solo cuando el modal esté completamente cargado
  });

  // Limpiar inputs y errores al abrir cualquier modal
  $(".modal").on("show.bs.modal", function () {
    limpiarInputsEnModal(this);
    limpiarErroresEnModal(this);
  });

  // Configurar al abrir el modal de detalles
  $("#modalViewDetails").on("show.bs.modal", function () {
    // Evitar limpiar el modal principal cuando se abre el modal de detalles
    $("#addAsignacionModal").off("show.bs.modal");
  });

  // Rehabilitar la limpieza para el modal principal cuando se cierra el modal de detalles
  $("#modalViewDetails").on("hide.bs.modal", function () {
    $("#addAsignacionModal").on("show.bs.modal", function () {
      limpiarInputsEnModal(this);
      limpiarErroresEnModal(this);
    });
  });
});

function fechaPorDefecto() {
  const date = new Date();
  const year = date.getFullYear();
  let month = date.getMonth() + 1; // Los meses van de 0 a 11, sumamos 1 para obtener el mes correcto
  let day = date.getDate();

  // Asegura que el mes y el día tengan dos dígitos
  month = month < 10 ? "0" + month : month;
  day = day < 10 ? "0" + day : day;

  // Formato que requiere el input de tipo date (YYYY-MM-DD)
  const formatedDate = `${year}-${month}-${day}`;

  // Asegurar que se seleccione el input de fecha correctamente
  const fechaInput = document.querySelector(".fecha-input");

  if (fechaInput) {
    fechaInput.value = formatedDate; // Asignar la fecha actual
  }
}

function showDiv(id = "formulario", Esconder = []) {
  console.log("showDiv")
  console.log("Esconder")
  console.log(Esconder)
  //encontrar el div del formulario
  let div = document.getElementById(id)
  //Si esta escondido mostrarlo de lo contrario esconder
  if (div.style.display === "none") {
    div.style.display = "block";
  } else {
    div.style.display = "none"
  }
  //Esconder otras ids
  for (let i = 0; i < Esconder.length; i++) {
    id_esconder = Esconder[i]
    console.log(id_esconder)
    div = document.getElementById(id_esconder)
    div.style.display = "none";
  }
}
//Esta funcion no se usa pero es para tener multiples botones que muestran y
//esconden tablas
function showDivHideOthers(id = "formulario") {
  let divs = {
    "tabla-asignaciones": document.getElementById("tabla-asignaciones"),
    "tabla-devoluciones": document.getElementById("tabla-devoluciones"),
    "tabla-traslados": document.getElementById("tabla-traslados"),
    "tabla-incidencias": document.getElementById("tabla-incidencias")
  }
  for (const [key, value] of Object.entries(divs)) {
    if (key != id) {
      value.style.display = "none"
    } else {
      value.style.display = "block"
    }

  }
}

//esta funcion no se usa
function openWindow(url) {
  window.open(url)
}

function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("myTableBody");
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 0; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (dir == "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}

function busqueda(tableBodyId = "myTBody") {
  var input, filter, tbody, tr, visibleIds = [];
  input = document.getElementById("buscador");
  filter = input.value.toLowerCase();
  tbody = document.getElementById(tableBodyId);
  tr = tbody.getElementsByTagName("tr");

  for (let i = 0; i < tr.length; i++) {
    let td = tr[i].querySelectorAll(".toCheck");
    let found = false;
    for (let j = 0; j < td.length; j++) {
      let texto = td[j].textContent.toLowerCase();
      if (texto.indexOf(filter) > -1) {
        tr[i].style.display = "";
        found = true;
      } 
    }
    if (!found) {
      tr[i].style.display = "none";
    } else {
      // Obtener el ID del equipo (asumiendo que está en un atributo data-id)
      let equipoId = tr[i].getAttribute("data-id");
      if (equipoId) visibleIds.push(equipoId);
    }
  }

  // Guardar los IDs en un atributo del botón de exportar búsqueda
  document.getElementById("exportarBusqueda").setAttribute("data-ids", visibleIds.join(","));
}

//al tocar el boton radio todo se destickea todo lo demas
function todoCheck() {
  checkboxContainer = document.getElementById("checkbox_container")
  checkboxes = checkboxContainer.getElementsByTagName("input")
  for (let i = 0; i < checkboxes.length; i++) {
    checkboxes[i].checked = false
  }
}
//al tickear una opcion automaticamente el boton radio se 
//destickea
function sheetCheck() {
  todo_check = document.getElementById("todo_check")
  todo_check.checked = false
}
//al tickear tickear todo se tickean todas las opciones inferiores
function check_all() {
  sheetCheck()
  console.log("checkall")
  checkboxContainer = document.getElementById("checkbox_container")
  checkboxes = checkboxContainer.getElementsByTagName("input")
  checkall_element = document.getElementById("checkall")
  for (let i = 0; i < checkboxes.length; i++) {
    checkboxes[i].checked = checkall.checked
  }
}
//Para filtrar los modelos de equipo en base a los tipos de equipo seria nesesario
//tener los grupos ya filtrados. y guardados de alguna manera.
//podria tenerlos separados en selects invisibles.
//por cada tipo un select

//tipos para mostrar Mac
tipos_mac = {
  "Telefono": true
}
tipos_imei = {
  "Tablet": true,
  "Celular": true
}
tipos_num_telefono = {
  "Celular": true,
  "Telefono": true
}
function mostrarSelectModelo(id_select_tipo_equipo) {
  console.log("select_tipo")
  select_tipo = document.getElementById(id_select_tipo_equipo)
  console.log(select_tipo)
  //get all divs with class select_tipo_modelo_rel_marca
  divs_select_de_tipo = document.querySelectorAll('.select_modelo_rel_tipo')
  console.log('divs_select_de_tipo')
  console.log(divs_select_de_tipo)
  //no puede ser un for in porque divs_select_de_tipo es un diccionario y 
  //devolveria las llaves no los valores
  for (let i = 0; i < divs_select_de_tipo.length; i++) {
    div = divs_select_de_tipo[i]
    console.log(div.id)
    console.log(select_tipo.value)
    if (div.id === "div_modelo_" + select_tipo.value) {
      div.style.display = "block"
    } else {
      div.style.display = "none"
    }
  }
}

function mostrarSelectsEspeciales(id_marca) {
  tipo = document.getElementById('select_tipo_marca:' + id_marca)
  valor_tipo_equipo = tipo.value
  console.log('valor_tipo_equipo')
  console.log(valor_tipo_equipo)
  //esconder mac
  console.log("mostrarSelectsEspeciales")
  mac_div = document.getElementById("Mac")
  if (tipos_mac[valor_tipo_equipo]) {
    mac_div.style.display = "block"
  } else {
    mac_div.style.display = "none"
  }

  //esconder imei
  imei_div = document.getElementById("Imei")
  if (tipos_imei[valor_tipo_equipo]) {
    imei_div.style.display = "block"
  } else {
    imei_div.style.display = "none"
  }
  //esconder numero de telefono
  num_telefono_div = document.getElementById("Telefono")
  if (tipos_num_telefono[valor_tipo_equipo]) {
    console.log("test")
    console.log(num_telefono_div)
    num_telefono_div.style.display = "block"
  } else {
    num_telefono_div.style.display = "none"
  }
}

function mostrarTipo_equipo() {
  //console.log("select_marca")
  select_marca = document.getElementById('marca')
  console.log(select_marca.value)
  //get all divs with class select_tipo_modelo_rel_marca
  divs_select_de_marca = document.querySelectorAll('.select_tipo_modelo_rel_marca')
  //console.log('divs_select_de_marca')
  //console.log(divs_select_de_marca)
  for (let i = 0; i < divs_select_de_marca.length; i++) {
    div = divs_select_de_marca[i]
    //console.log(div)
    if (div.id === select_marca.value) {
      div.style.display = "block"
    } else {
      div.style.display = "none"
    }
  }

}
//Envia el tipo a 
function enviarTipo(valor) {
  console.log("test")
  console.log(valor)
  select = document.getElementById(valor)
  tipo_equipo_value = select.value
  console.log("select")
  console.log(select)
  console.log(select.value)
  output_tipo_equipo = document.getElementById('nombre_tipo_equipo')
  output_tipo_equipo.value = select.value
  console.log("tipo_equipo")
  console.log(output_tipo_equipo)

}
function abrir_cerrar_ojo(id_ojo, repetir) {
  ojo_contrasenna = document.getElementById(id_ojo)
  src = ojo_contrasenna.src
  img_name = src.split("/")
  console.log("img_name")
  console.log(img_name)
  if (img_name[5] == "eye.png") {
    console.log("if")
    ojo_contrasenna.src = "../static/img/hidden.png"
    if (repetir) {
      input = document.getElementById('contrasenna_repetir').type = 'password'
    } else {
      input = document.getElementById('contrasenna').type = 'password'
    }
  } else {
    console.log("else")
    ojo_contrasenna.src = "../static/img/eye.png"
    if (repetir) {
      input = document.getElementById('contrasenna_repetir').type = 'text'
    } else {
      input = document.getElementById('contrasenna').type = 'text'
    }
  }



}

function enviarModelo(valor) {
  console.log("test")
  console.log(valor)
  select = document.getElementById(valor)
  console.log("select")
  console.log(select)
  tipo_equipo_value = select.value
  console.log("select value")
  console.log(select.value)
  options = select.options
  a = options[select.selectedIndex].value
  console.log(a)
  output_modelo_equipo = document.getElementById('modelo_para_equipo')
  output_modelo_equipo.value = select.value
  console.log("modelo_equipo")
  console.log(output_modelo_equipo)
}



function mostrarTipo_para_agregar_modelo() {
  select_marca = document.getElementById('marca')
  console.log(select_marca.value)
  //get all divs with class select_tipo_modelo_rel_marca
  divs_select_de_marca = document.querySelectorAll('.select_modelo')
  //console.log('divs_select_de_marca')
  //console.log(divs_select_de_marca)
  for (let i = 0; i < divs_select_de_marca.length; i++) {
    div = divs_select_de_marca[i]
    //console.log(div)
    if (div.id === select_marca.value) {
      div.style.display = "block"
    } else {
      div.style.display = "none"
    }
  }
}
function mostrarBotonAgregarAlUsarSelect() {
  boton = document.getElementById("enviar")
  boton.style.display = "block"
  console.log(boton)

}
function mostrar_agregar(id_select) {
  //mostrar el boton de agregar
  select = document.getElementById(id_select)
  boton = document.getElementById('enviar')
  boton.style.display = "block"
  //enviar tipo de equipo
  input_tipo_equipo = document.getElementById('nombre_tipo_equipo')
  input_tipo_equipo.value = select.value
  console.log(input_tipo_equipo)
}

//para editar modelo. Mueve el valor del input al selector de tipo_equipo que se muestra
function seleccionarTipoEquipoEditarModelo(id_select) {
  console.log("seleccionarTipoEquipoEditarModelo")
  input = document.getElementById("nombre_tipo_equipo")
  console.log("input")
  console.log(input)
  select = document.getElementById("s_" + id_select)
  console.log("select")
  console.log(select)
  Options = select.options
  console.log("options")
  console.log(Options)
  console.log("")
  for (let i = 0; i < Options.length; i++) {
    option = Options[i]
    console.log(option)
    if (option.value === input.value) {
      console.log("selected")
      option.selected = true
    } else {
      console.log("not selected")
      option.selected = false
    }
  }

}

$(document).ready(function () {
  // Función para validar caracteres permitidos en el correo
  function validateEmailInput() {
    var input = $(this).val();
    var regex = /^[a-zA-Z0-9.@]*$/; // Solo permite letras, números, puntos y @
    var errorMessage = $("#error-message");

    // Verificar si hay caracteres no permitidos
    if (!regex.test(input)) {
      errorMessage.text("Caracteres no permitidos. Solo se permiten letras, números, puntos y @.").show();
    } else {
      errorMessage.hide();
    }
  }

  // Asignar la función de validación a todos los inputs con la clase 'validate-email'
  $(".validar-correo").on("input", validateEmailInput);
});

$(document).ready(function () {
  // Función de validación
  function validateInput() {
    var input = $(this).val();
    var regex = /^[a-zA-Z0-9,.-/  ]*$/; // Permitir letras, @, puntos, números y espacios
    var errorMessage = $("#error-message");

    // Verificar si el input actual es válido
    if (!regex.test(input)) {
      errorMessage.text("Caracteres no permitidos. Solo se permiten letras, números y espacios.").show();
    } else {
      // Verificar si hay algún input con error
      if ($(".validatable-input").filter(function () { return !regex.test($(this).val()); }).length > 0) {
        errorMessage.text("Caracteres no permitidos. Solo se permiten letras, números y espacios.").show();
      } else {
        errorMessage.hide();
      }
    }
  }

  // Asignar la función de validación a todos los inputs con la clase 'validatable-input'
  $(".validatable-input").on("input", validateInput);
});

$(document).ready(function () {
  function validarContraseña() {
    const password = $(this).val();

    const upperCasePattern = /[A-Z]/;
    const lowerCasePattern = /[a-z]/;
    const numberPattern = /[0-9]/;
    const specialCharPattern = /[!@#$%^&*(),.?":{}|<>-]/;
    const minLength = 8;

    updateValidation("upperCase", upperCasePattern.test(password));
    updateValidation("lowerCase", lowerCasePattern.test(password));
    updateValidation("number", numberPattern.test(password));
    updateValidation("specialChar", specialCharPattern.test(password));
    updateValidation("minLength", password.length >= minLength);
  }

  function updateValidation(elementId, isValid) {
    const element = $("#" + elementId);
    const icon = element.find("i");

    if (isValid) {
      element.removeClass("invalid").addClass("valid");
      icon.removeClass("bi-shield-x").addClass("bi-shield-check");
    } else {
      element.removeClass("valid").addClass("invalid");
      icon.removeClass("bi-shield-check").addClass("bi-shield-x");
    }
  }

  $(".validar-contraseña").on("input", validarContraseña);
});

$(document).ready(function () {
  function validarSoloLetras(inputField) {
    const regex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
    const input = inputField.val().trim();

    if (input.length === 0) {
      limpiarError(inputField);
      return true;
    }

    if (!regex.test(input)) {
      mostrarError(inputField, "Solo se permiten letras y espacios");
      return false;
    } else {
      limpiarError(inputField);
    }

    return true;
  }

  // Validar en tiempo real cuando el usuario escribe
  $(document).on("input", ".validar-letras", function () {
    validarSoloLetras($(this));
  });

  // Validación en el envío del formulario
  $(document).on("submit", "form", function (event) {
    let esValido = true;
    const form = $(this);

    form.find(".validar-letras").each(function () {
      if (!validarSoloLetras($(this))) {
        esValido = false;
      }
    });

    if (!esValido) {
      event.preventDefault();
    }
  });
});


  $(document).ready(function () {
    function validarInputCorreo(inputField) {
      const regex = /^[a-zA-Z0-9._-]+$/; // Solo caracteres válidos antes del @
      const input = inputField.val().trim();

      if (input.length === 0) {
        limpiarError(inputField);
        return true;
      }

      if (!regex.test(input)) {
        mostrarError(inputField, "Solo se permiten letras, números y los caracteres: . _ -");
        return false;
      } else {
        limpiarError(inputField);
      }

      return true;
    }

  // Validar en tiempo real cuando el usuario escribe
  $(document).on("input", ".validar-input-correo", function () {
    validarInputCorreo($(this)); // Pasar correctamente $(this) a la función
  });

  // Validación en el envío del formulario
  $(document).on("submit", "form", function (event) {
    let esValido = true;
  const form = $(this);

  form.find(".validar-input-correo").each(function () {
      if (!validarInputCorreo($(this))) {
    esValido = false;
      }
    });

  if (!esValido) {
    event.preventDefault();
    }
  });
});



$(document).ready(function () {
  // Función de validación
  function validateNumbersInput() {
    const inputField = $(this);
    const inputValue = inputField.val();
    const regex = /^[0-9]*$/; // Permitir números

    if (!regex.test(inputValue)) {
      mostrarError(inputField, "Sólo se permiten números");
    } else {
      limpiarError(inputField);
    }
  }
  $(".solo-numeros").on("input", validateNumbersInput);
});

$(document).ready(function () {
  function validarCampoObligatorio(inputField) {
    const input = inputField.val().trim();

    if (input === "") {
      mostrarError(inputField, "Este campo es obligatorio");
      return false;
    } else {
      limpiarError(inputField);
      return true;
    }

  }

  $(document).on("change", "select.campo-obligatorio", function () {
    validarCampoObligatorio($(this));
  });

  // Validación en el envío del formulario
  $(document).on("submit", "form", function (event) {
    let esFormularioValido = true;
    const form = $(this);

    // Solo mostrar mensaje de error al enviar el formulario
    form.find(".campo-obligatorio").each(function () {
      if (!validarCampoObligatorio($(this))) {
        esFormularioValido = false;
      }
    });

    if (!esFormularioValido) {
      event.preventDefault();
    }
  });
});

// Valida las fechas, sólo es necesario ocupar la clase ".validar-fecha-X-Y", tal que:
// => X representa los días anteriores a la fecha actual
// => Y representa los días siguientes a la fecha actual
$(document).ready(function () {
  function configurarRangoFecha(inputField) {
    const classList = inputField.attr("class").split(" ");
    let diasAtras = 0;
    let diasAdelante = 0;

    // Buscar la clase que siga el formato "validar-fecha-X-Y"
    classList.forEach(className => {
      const match = className.match(/^validar-fecha-(\d+)-(\d+)$/);
      if (match) {
        diasAtras = parseInt(match[1]);
        diasAdelante = parseInt(match[2]);
      }
    });

    // Obtener fechas mínima y máxima permitidas
    const hoy = new Date();
    const fechaMin = new Date();
    fechaMin.setDate(hoy.getDate() - diasAtras);

    const fechaMax = new Date();
    fechaMax.setDate(hoy.getDate() + diasAdelante);

    // Formatear fechas en formato YYYY-MM-DD
    const fechaMinFormato = fechaMin.toISOString().split("T")[0];
    const fechaMaxFormato = fechaMax.toISOString().split("T")[0];

    // Aplicar restricciones en el input de fecha
    inputField.attr("min", fechaMinFormato);
    inputField.attr("max", fechaMaxFormato);
  }

  function validarRangoFecha(inputField) {
    const fechaSeleccionada = new Date(inputField.val());
    const fechaMin = new Date(inputField.attr("min"));
    const fechaMax = new Date(inputField.attr("max"));

    if (fechaSeleccionada < fechaMin || fechaSeleccionada > fechaMax) {
      mostrarError(inputField, `La fecha debe estar entre ${fechaMin.toLocaleDateString()} y ${fechaMax.toLocaleDateString()}.`);
      return false;
    } else {
      limpiarError(inputField);
      return true;
    }
  }

  // Configurar automáticamente los inputs con clase "validar-fecha-X-Y"
  $("input[type='date']").each(function () {
    if ($(this).attr("class").match(/validar-fecha-\d+-\d+/)) {
      configurarRangoFecha($(this));
    }
  });

  // Validar en tiempo real cuando el usuario cambie la fecha
  $(document).on("change", "input[type='date']", function () {
    if ($(this).attr("class").match(/validar-fecha-\d+-\d+/)) {
      validarRangoFecha($(this));
    }
  });

  // Validación en el envío del formulario
  $(document).on("submit", "form", function (event) {
    let esValido = true;
    const form = $(this);

    form.find("input[type='date']").each(function () {
      if ($(this).attr("class").match(/validar-fecha-\d+-\d+/)) {
        if (!validarRangoFecha($(this))) {
          esValido = false;
        }
      }
    });

    if (!esValido) {
      event.preventDefault();
    }
  });
});

// Funcion para darle un tiempo de espera y luego desaparer la alerta
$(document).ready(function () {
  setTimeout(function () {
    $('.alert').each(function () {
      $(this).addClass('hidden');
      setTimeout(() => {
        $(this).remove();
      }, 2000);
    });
  }, 5000);
});

$(document).ready(function () {
  // Función para mostrar un modal genérico con solo un botón de cerrar
  window.MensajeGenericoModal = function (title, message) {
    // Configurar el título y el mensaje
    $("#genericModalLabel").text(title);
    $("#genericModalMessage").text(message);
    

    // Quitar cualquier evento existente en el botón de confirmación y ocultarlo
    $("#genericModalConfirmButton").hide();

    // Mostrar el modal
    $("#genericModal").modal("show");
  };
});

$(document).ready(function () {
  // Definir y exponer configureGenericModal globalmente
  window.configureGenericModal = function (title, message, confirmUrl) {
    // Configurar el título y mensaje del modal
    $("#genericModalLabel").text(title);
    $("#genericModalMessage").text(message);

    // Asignar la acción de redirección al botón de confirmación
    $("#genericModalConfirmButton").off("click").on("click", function () {
      if (confirmUrl) {
        window.location.href = confirmUrl; // Redirigir a la URL
      }
      $("#genericModal").modal("hide");
    });

    $("#genericModal").modal("show");
  };

  // Asignar eventos a los botones de eliminar
  $(".delete-button").on("click", function () {
    const title = $(this).data("title") || "Confirmar Acción";
    const message = $(this).data("message") || "¿Estás seguro de realizar esta acción?";
    const confirmUrl = $(this).data("url");

    configureGenericModal(title, message, confirmUrl);
  });
});


$(document).ready(function () {
  function calcularDigitoVerificador(rutSinFormato) {
    let rut = rutSinFormato.replace(/\D/g, "");
    let suma = 0;
    let multiplicador = 2;

    for (let i = rut.length - 1; i >= 0; i--) {
      suma += parseInt(rut[i]) * multiplicador;
      multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
    }

    const resto = suma % 11;
    const digitoVerificador = 11 - resto;

    if (digitoVerificador === 11) return "0";
    if (digitoVerificador === 10) return "K";
    return digitoVerificador.toString();
  }

  function actualizarRutVerificador(rutInput) {
    const inputRut = $(rutInput);
    const inputVerificador = inputRut.siblings(".rut-verificador");

    const rutSinFormato = inputRut.val().replace(/[^0-9]/g, "");
    inputRut.val(rutSinFormato);

    if (!rutSinFormato) {
      inputVerificador.val(""); // Limpia el dígito verificador
      limpiarError(inputRut); // Limpia cualquier error
      return;
    }

    if (!/^\d{7,8}$/.test(rutSinFormato)) {
      inputVerificador.val(""); // Limpia el dígito verificador
      mostrarError(inputRut, "El RUT debe contener 7 u 8 números");
      return;
    }

    const digitoVerificador = calcularDigitoVerificador(rutSinFormato);
    inputVerificador.val(digitoVerificador);
    limpiarError(inputRut); // Limpia cualquier error si el RUT es válido
  }

  function prepararRutCompleto(form) {
    const inputRut = $(form).find(".rut-input");
    const inputVerificador = $(form).find(".rut-verificador");
    const hiddenInput = $(form).find(".rut_completo");
    const rutSinFormato = inputRut.val();
    const digitoVerificador = inputVerificador.val();

    if (!rutSinFormato) {
      hiddenInput.val("");
      mostrarError(inputRut, "Este campo es obligatorio");
      return;
    }

    if (/^\d{7,8}$/.test(rutSinFormato) && /^[0-9Kk]$/.test(digitoVerificador)) {
      hiddenInput.val(`${rutSinFormato}-${digitoVerificador}`);
    } else {
      hiddenInput.val("");
      mostrarError(inputRut, "El RUT debe contener 7 u 8 números");
    }
  }

  $("form.funcionarios, form.asignaciones").on("submit", function (event) {
    prepararRutCompleto(this);

    const rutCompleto = $(this).find(".rut_completo").val();

    if (!rutCompleto) {
      event.preventDefault(); // Detener el envío del formulario si el RUT no es válido
    }
  });

  $(".rut-input").on("input", function () {
    actualizarRutVerificador(this);
  });

  // Limpiar mensajes de error en tiempo real
  $(".rut-input").on("input change", function () {
    limpiarError($(this));
  });
});



$(document).ready(function () {
  $(".edit-button").on("click", function () {
    // Obtiene valores del botón
    const rutCompleto = $(this).data("rut");
    const nombre = $(this).data("nombre");
    const correo = $(this).data("correo");
    const cargo = $(this).data("cargo");
    const unidad = $(this).data("unidad");

    // Separa el RUT en cuerpo y dígito verificador
    const [rutSinFormato, digitoVerificador] = rutCompleto.split("-");

    // Divide el correo en parte local y dominio
    const [parteLocalCorreo, dominioCorreo] = correo.split("@");

    // Asigna valores a los campos del formulario en el modal
    $("#edit_rut_funcionario").val(rutSinFormato); // Rut sin el dígito verificador
    $("#edit_rut_verificador").val(digitoVerificador); // Dígito verificador
    $("#edit_rut_actual").val(rutCompleto); // Rut completo en el campo oculto
    $("#edit_nombre_funcionario").val(nombre);
    $("#edit_correo_funcionario").val(parteLocalCorreo); // Solo la parte local del correo
    $("#edit_correo_dominio").val(`@${dominioCorreo}`); // Asigna el dominio al selector
    $("#edit_cargo_funcionario").val(cargo);
    $("#edit_codigo_Unidad").val(unidad);
  });
});

$(document).ready(function () {
  function combinarCorreoCompleto(modal) {
    // Selecciona los elementos específicos dentro del modal
    const inputCorreo = $(modal).find(".correo-input-funcionario");
    const dominioSeleccionado = $(modal).find(".correo-dominio-funcionario").val();
    const correoCompleto = inputCorreo.val().trim() + dominioSeleccionado;

    // Actualiza el campo oculto con el correo completo
    $(modal).find(".correo-oculto").val(correoCompleto);
  }

  // Actualiza el correo completo en tiempo real para el modal actual (agregar o editar)
  $(".correo-input-funcionario, .correo-dominio-funcionario").on("input change", function () {
    const modal = $(this).closest(".modal"); // Identifica el modal actual (agregar o editar)
    combinarCorreoCompleto(modal);
  });

  // Filtra el evento submit solo para los formularios relacionados
  $("form.funcionarios").on("submit", function () {
    const modal = $(this).closest(".modal"); // Identifica el modal actual (agregar o editar)
    combinarCorreoCompleto(modal);
  });
});





