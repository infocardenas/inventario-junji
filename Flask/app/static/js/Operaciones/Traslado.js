document.getElementById("Origen").addEventListener("change", function() {
    fetch(`/traslado/equipos_unidad/${this.value}`)
    .then(response => response.json())
    .then(data => {
        let equiposLista = document.getElementById("equiposLista");
        equiposLista.innerHTML = "";
        data.forEach(equipo => {
            equiposLista.innerHTML += `<div><input type='checkbox' name='trasladar[]' value='${equipo.idEquipo}'> ${equipo.nombreModeloequipo} - ${equipo.Num_serieEquipo}</div>`;
        });
    });
});

document.getElementById("trasladoForm").addEventListener("submit", function(event) {
    event.preventDefault();
    let formData = new FormData(this);

    fetch(`/traslado/create_traslado/${document.getElementById("Origen").value}`, {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let tableBody = document.getElementById("trasladoTableBody");
            let newRow = document.createElement("tr");
            newRow.innerHTML = `
                <td>${data.fechatraslado}</td>
                <td><a href="/traslado/mostrar_pdf/${data.idTraslado}" class="info-button">Acta</a></td>
                <td>${data.nombreOrigen}</td>
                <td>${data.nombreDestino}</td>
                <td>
                    <a href="/traslado/delete_traslado/${data.idTraslado}" class="delete-button">Eliminar</a>
                    <a href="/mostrar_asociados_traslado/${data.idTraslado}" class="info-button">Equipos</a>
                </td>`;
            tableBody.appendChild(newRow);
            $('#trasladoModal').modal('hide');
            this.reset();
        } else {
            alert("Error al agregar traslado");
        }
    });
});