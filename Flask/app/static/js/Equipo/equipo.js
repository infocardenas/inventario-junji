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
    console.log(`Cargando modelos para marcaId: ${marcaId}, tipoId: ${tipoId}`); // Depuración
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
