/*const btnDelete= document.querySelectorAll('.btn-delete');
if(btnDelete) {
  const btnArray = Array.from(btnDelete);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if(!confirm('Are you sure you want to delete it?')){
        e.preventDefault();
      }
    });
  })
}
//Código para Datables
$(document).ready(function() { 
  $('#table').DataTable(); //Para inicializar datatables de la manera más simple
});
*/
function fechaPorDefecto() {
  //Crea un objeto date para obtener la fecha actual
  date = new Date();
  year = date.getFullYear();
  month = date.getMonth() + 1;
  day = date.getDate();
  //El formato tiene que ser con dos digitos con un 0 a la izquierda
  //de ser nesesario
  if (month < 10) {
    month = "0" + month
  }
  if (day < 10) {
    day = "0" + day
  }
  //Se crea una string con la fecha en el formato que nesesita html
  formatedDate = year + "-" + month + "-" + day
  document.getElementById("inputFecha")
    .setAttribute("value", formatedDate);

}
console.log("jsLink")

function showDiv(id = "formulario", Esconder = []) {
  console.log("showDiv")
  console.log("Esconder")
  console.log(Esconder)
  //encontrar el div del formulario
  let div = document.getElementById(id)
  //Si esta escondido mostrarlo de lo contrario esconder
  if (div.style.display === "none") {
    div.style.display = "block";
  }else {
    div.style.display = "none"
  }
  //Esconder otras ids
  for(let i = 0; i < Esconder.length; i++) {
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
  console.log("busqueda")
  var input, a, filter, tbody;
  //busca el bloque de texto
  input = document.getElementById("buscador")
  //el texto del bloque es nuestro filtro
  filter = input.value.toLowerCase();
  //obtenemos el cuerpo de la tabla
  tbody = document.getElementById(tableBodyId)
  //tr es una lista de todos las filas
  tr = tbody.getElementsByTagName("tr")
  for (let i = 0; i < tr.length; i++) {
    //obtiene todas las columnas de la fila actual
    //console.log("row")
    td = tr[i].querySelectorAll(".toCheck")
    //console.log("td " + td.length)
    //console.log(td)
    for (let j = 0; j < td.length; j++) {
      console.log("col")
      texto = td[j].textContent.toLowerCase()
      //console.log(texto)
      if (texto.indexOf(filter) > -1) {
        tr[i].style.display = ""
        break;
      } else {
        tr[i].style.display = "none"
      }
    }
  }
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
  /*
  console.log("mostrar")
  //obtener la id del tipo
  tipo = document.getElementById("nombre_tipo_equipo").value
  
  console.log("tipo")
  console.log(tipo)
  //get all divs with class x give class x to relevant divs
  div = document.getElementById("select_div")   
  selects = div.querySelectorAll(".select_modelo")
  //esconder todos los divs menos los relevantes
  for(let i = 0; i < selects.length; i++) {
    if(selects[i].id == tipo) {
      selects[i].style.display = ""
      console.log(selects[i])
    }else {
      selects[i].style.display = "none"

    }
  }
  */
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


  /*
  select = document.getElementById("marca_equipo")
  idMarca = select.value;
  console.log("mostarTipo_equipo" + idMarca)

  //Obten todos los divs de la clase select_modelo
  divs_select_para_marca = document.querySelectorAll('.select_modelo')
  //parece que el objeto retornado es un dicionario por lo que un 
  //for in no funciona pero las claves son numeros naturales + 0
  //console.log(divs_select_para_marca)
  //console.log(divs_select_para_marca[0])
  
  for(let i = 0; i < divs_select_para_marca.length; i++) {
    div = divs_select_para_marca[i]
    div.style.display = "none"
  }
  objective_div = document.getElementById(idMarca)
  objective_div.style.display = "block"

  boton = document.getElementById("enviar")
  boton.style.display = "block"
  */
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
  //console.log("src")
  //console.log(src)
  //relative_tmp = location.href.split("/")
  //relative_path = relative_tmp[0] + "//" + relative_tmp[2]
  //console.log("absURL")
  //console.log(relative_path)
  //console.log(document.URL)
  //console.log(location.href)
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
//Envia el tipo a 
//Hay una forma mas facil pero ya lo hice asi








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
function mostrar_agregar(id_select)  {
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
  for(let i = 0; i < Options.length; i++) {
    option = Options[i]
    console.log(option)
    if(option.value === input.value) {
      console.log("selected")
      option.selected = true
    }else {
      console.log("not selected")
      option.selected = false
    }
  }

}

function validarInputs() {
  // Define los caracteres no permitidos
  const caracteresNoPermitidos = /[!"#$%&/()]/;
  const inputs = document.querySelectorAll('input'); // Selecciona todos los inputs del formulario

  for (let input of inputs) {
      if (input.value.trim() !== "" && caracteresNoPermitidos.test(input.value)) {
          alert(`El campo "${input.name}" contiene caracteres no permitidos.`);
          input.focus(); // Enfoca el input problemático
          return false; // Evita que el formulario se envíe
      }
  }
  return true; // Si todos los inputs son válidos, permite el envío del formulario
}


$(document).ready(function() {
  // Función de validación
  function validateInput() {
      var input = $(this).val();
      var regex = /^[a-zA-Z0-9 ]*$/; // Permitir letras, números y espacios
      var errorMessage = $("#error-message");

      // Verificar si el input actual es válido
      if (!regex.test(input)) {
          errorMessage.text("Caracteres no permitidos. Solo se permiten letras, números y espacios.").show();
      } else {
          // Verificar si hay algún input con error
          if ($(".validatable-input").filter(function() { return !regex.test($(this).val()); }).length > 0) {
              errorMessage.text("Caracteres no permitidos. Solo se permiten letras, números y espacios.").show();
          } else {
              errorMessage.hide();
          }
      }
  }

  // Asignar la función de validación a todos los inputs con la clase 'validatable-input'
  $(".validatable-input").on("input", validateInput);
});


$(document).ready(function() {
  function validateLettersInput() {
      const input = $(this).val();
      const regex = /^[a-zA-Z\s]*$/; 
      const errorMessage = $("#error-message"); 

      if (!regex.test(input)) {
          errorMessage.text("Solo se permiten letras y espacios.").show();
      } else {
          errorMessage.hide();
      }
  }

  $(".solo-letras").on("input", validateLettersInput);
});


$(document).ready(function() {
  function validateNumbersInput() {
      const input = $(this).val();
      const regex = /^[0-9]*$/;
      const errorMessage = $("#error-message"); 

      if (!regex.test(input)) {
          errorMessage.text("Solo se permiten números.").show()
      } else {
          errorMessage.hide();
      }
  }
  $(".solo-numeros").on("input", validateNumbersInput);
});

$(document).ready(function () {
  function validarRut() {
      const inputField = $(this);
      let rawInput = inputField.val(); // Captura el valor ingresado
      const errorMessage = $("#error-message");

      // Ocultar el mensaje si el campo está vacío
      if (rawInput.trim() === "") {
          errorMessage.hide();
          return;
      }

      // Validar caracteres no permitidos
      if (/[^0-9\-kK]/.test(rawInput)) {
          errorMessage.text("Solo se permiten números, un guion y la letra K (después del guion).").show();
          rawInput = rawInput.replace(/[^0-9\-kK]/g, ""); // Elimina caracteres no válidos
          return;
      }

      // Dividir el input en partes (antes y después del guion)
      const parts = rawInput.split("-");
      const rut = parts[0]; // Parte numérica antes del guion
      const dv = parts[1] || ""; // Parte después del guion, si existe
      const hasGuion = rawInput.includes("-");

      // Validar longitud antes del guion
      if (rut.length > 8) {
          errorMessage.text("El RUT no puede tener más de 8 dígitos antes del guion.").show();
          rawInput = rut.slice(0, 8) + (hasGuion ? "-" + dv : ""); // Cortar al límite
          inputField.val(rawInput);
          return;
      }

      // Prevenir ingresar guion si hay menos de 7 dígitos
      if (hasGuion && (rut.length < 7 || rut.length > 8)) {
          errorMessage.text("El RUT debe tener entre 7 y 8 dígitos antes del guion.").show();
          rawInput = rut; // Elimina el guion si es inválido
          inputField.val(rawInput);
          return;
      }

      // Validar que el dígito verificador tenga solo un carácter
      if (dv && dv.length > 1) {
          errorMessage.text("El dígito verificador solo puede tener un carácter.").show();
          rawInput = rut + "-" + dv.slice(0, 1); // Limitar el dígito verificador
          inputField.val(rawInput);
          return;
      }

      // Validar que la `k` solo aparezca después del guion
      if (dv && !/^[0-9kK]$/.test(dv)) {
          errorMessage.text("El dígito verificador debe ser un número o la letra K.").show();
          rawInput = `${rut}-`; // Borra el DV inválido
          inputField.val(rawInput);
          return;
      }

      // Calcular el dígito verificador automáticamente solo si el guion es válido
      if (hasGuion && dv === "" && rut.length >= 7 && rut.length <= 8) {
          const calculatedDV = calcularDigitoVerificador(rut); // Calcular DV
          rawInput = `${rut}-${calculatedDV}`; // Formatear el RUT completo
          inputField.val(rawInput);

          // Mover el cursor antes del dígito verificador
          const cursorPos = rawInput.length - calculatedDV.length; // Posición justo antes del DV
          inputField[0].setSelectionRange(cursorPos, cursorPos);

          errorMessage.hide();
          return;
      }

      // Bloquear entrada si el RUT está completo
      if (rut.length >= 7 && rut.length <= 8 && hasGuion && /^[0-9kK]$/.test(dv)) {
          // Limitar el valor del input solo al RUT completo
          rawInput = `${rut}-${dv}`;
          inputField.val(rawInput);

          // Eliminar cualquier carácter adicional
          if (rawInput.length > rut.length + dv.length + 1) {
              inputField.val(`${rut}-${dv}`); // Asegurarse de que no se agreguen caracteres adicionales
          }

          errorMessage.hide();
          return;
      }

      // Si no hay errores, ocultar el mensaje
      errorMessage.hide();
  }

  function calcularDigitoVerificador(rut) {
      let suma = 0;
      let multiplicador = 2;

      // Iterar sobre el RUT de derecha a izquierda
      for (let i = rut.length - 1; i >= 0; i--) {
          suma += parseInt(rut[i]) * multiplicador;
          multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
      }

      const resto = suma % 11;
      const calculado = 11 - resto;

      // Convertir el resultado al formato de DV esperado
      return calculado === 10 ? "k" : calculado === 11 ? "0" : calculado.toString();
  }

  $(".rut-input").on("input", validarRut);
});
