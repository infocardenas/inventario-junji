function buscarFuncionarios(page = 1) {
    const query = document.getElementById("buscador_funcionario").value.toLowerCase();

    fetch(`/buscar_funcionarios?q=${encodeURIComponent(query)}&page=${page}`)
        .then(response => response.json())
        .then(data => {
            actualizarTablaFuncionarios(data.funcionarios);
            actualizarPaginacionFuncionarios(data.total_pages, data.current_page, query, data.visible_pages);
        })
        .catch(error => console.error("Error al buscar funcionarios:", error));
}

let funcionariosActuales = [];
let ordenActualFuncionario = { campo: null, asc: true };

function actualizarTablaFuncionarios(funcionarios) {
    funcionariosActuales = funcionarios;
    const tbody = document.getElementById("funcionarioTableBody");
    tbody.innerHTML = "";

    if (!funcionarios.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No hay datos disponibles.</td></tr>';
        return;
    }

    funcionarios.forEach(fun => {
        const row = document.createElement("tr");
        row.setAttribute("data-rut", fun.rutFuncionario);
        row.setAttribute("data-nombre", fun.nombreFuncionario);
        row.setAttribute("data-correo", fun.correoFuncionario);
        row.setAttribute("data-cargo", fun.cargoFuncionario);
        row.setAttribute("data-unidad", fun.idUnidad);

        row.innerHTML = `
            <td>${fun.rutFuncionario}</td>
            <td>${fun.nombreFuncionario}</td>
            <td>${fun.cargoFuncionario}</td>
            <td>${fun.nombreUnidad}</td>
            <td>${fun.correoFuncionario}</td>
            <td>
                <div class="d-flex justify-content-center gap-2">
                    <button class="btn btn-warning edit-button" data-bs-toggle="modal"
                        data-bs-target="#editFuncionarioModal" data-rut="${fun.rutFuncionario}"
                        data-nombre="${fun.nombreFuncionario}" data-correo="${fun.correoFuncionario}"
                        data-cargo="${fun.cargoFuncionario}" data-unidad="${fun.idUnidad}">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    ${fun.equipos_asignados == 0 ? `
                    <button type="button" class="btn btn-danger delete-button"
                        data-title="Eliminar funcionario"
                        data-message="¿Estás seguro de que deseas eliminar al funcionario ${fun.nombreFuncionario}?"
                        data-url="/delete_funcionario/${fun.rutFuncionario}">
                        <i class="bi bi-trash-fill"></i>
                    </button>
                    ` : `
                    <button type="button" class="btn btn-danger" data-bs-toggle="modal"
                        data-bs-target="#warningModal">
                        <i class="bi bi-trash-fill"></i>
                    </button>
                    `}
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function ordenarFuncionario(campo) {
    if (ordenActualFuncionario.campo === campo) {
        ordenActualFuncionario.asc = !ordenActualFuncionario.asc;
    } else {
        ordenActualFuncionario.campo = campo;
        ordenActualFuncionario.asc = true;
    }
    funcionariosActuales.sort((a, b) => {
        let valA = a[campo];
        let valB = b[campo];
        if (!isNaN(valA) && !isNaN(valB)) {
            valA = Number(valA);
            valB = Number(valB);
        } else {
            valA = (valA || '').toString().toLowerCase();
            valB = (valB || '').toString().toLowerCase();
        }
        if (valA < valB) return ordenActualFuncionario.asc ? -1 : 1;
        if (valA > valB) return ordenActualFuncionario.asc ? 1 : -1;
        return 0;
    });
    actualizarTablaFuncionarios(funcionariosActuales);
}

function actualizarPaginacionFuncionarios(totalPages, currentPage, query, visiblePages) {
    const pagination = document.getElementById("funcionario-pagination");
    pagination.innerHTML = "";

    visiblePages.forEach(page => {
        const li = document.createElement("li");
        if (page === "...") {
            li.className = "page-item disabled";
            li.innerHTML = `<span class="page-link">...</span>`;
        } else {
            li.className = `page-item ${page === currentPage ? "active" : ""}`;
            li.innerHTML = `<a class="page-link" href="#" onclick="buscarFuncionarios(${page});return false;">${page}</a>`;
        }
        pagination.appendChild(li);
    });

    // Botón "Anterior"
    if (currentPage > 1) {
        const prevLi = document.createElement("li");
        prevLi.className = "page-item";
        prevLi.innerHTML = `<a class="page-link" href="#" onclick="buscarFuncionarios(${currentPage - 1});return false;">Anterior</a>`;
        pagination.insertBefore(prevLi, pagination.firstChild);
    }

    // Botón "Siguiente"
    if (currentPage < totalPages) {
        const nextLi = document.createElement("li");
        nextLi.className = "page-item";
        nextLi.innerHTML = `<a class="page-link" href="#" onclick="buscarFuncionarios(${currentPage + 1});return false;">Siguiente</a>`;
        pagination.appendChild(nextLi);
    }
}

// Cargar todos los funcionarios al cargar la página
document.addEventListener("DOMContentLoaded", function () {
    buscarFuncionarios(1);
});

// --- Código para poblar el modal de edición y campos ocultos ---
$(document).ready(function () {
    $('#editFuncionarioModal').on('shown.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var rutCompleto = button.data('rut') ? String(button.data('rut')) : '';
        var nombre = button.data('nombre');
        var correoCompleto = button.data('correo');
        var cargo = button.data('cargo');
        var unidadId = button.data('unidad');

        var rutNumero = '';
        var rutDv = '';
        if (rutCompleto && rutCompleto.includes('-')) {
            var partesRut = rutCompleto.split('-');
            rutNumero = partesRut[0];
            rutDv = partesRut[1];
        } else {
            rutNumero = rutCompleto;
        }

        var correoLocal = '';
        var correoDominio = '';
        if (correoCompleto && correoCompleto.includes('@')) {
            var partesCorreo = correoCompleto.split('@');
            correoLocal = partesCorreo[0];
            correoDominio = ('@' + partesCorreo[1]).toLowerCase();
        } else {
            correoLocal = correoCompleto;
        }

        var modal = $(this);
        modal.find('#edit_rut_funcionario').val(rutNumero);
        modal.find('#edit_rut_verificador').val(rutDv);
        modal.find('#edit_nombre_funcionario').val(nombre);
        modal.find('#edit_correo_funcionario').val(correoLocal);
        modal.find('#edit_correo_dominio').val(correoDominio);
        modal.find('#edit_cargo_funcionario').val(cargo);
        modal.find('#edit_codigo_Unidad').val(unidadId);
        modal.find('#edit_rut_actual').val(rutCompleto);
        modal.find('#rut_completo').val(rutCompleto);
        modal.find('#edit_correo_oculto').val(correoCompleto);
    });

    $('#edit_rut_funcionario, #edit_rut_verificador').on('input', function () {
        var numero = $('#edit_rut_funcionario').val();
        var dv = $('#edit_rut_verificador').val();
        if (numero || dv) {
            $('#editFuncionarioModal').find('#rut_completo').val(numero + '-' + dv);
        } else {
            $('#editFuncionarioModal').find('#rut_completo').val('');
        }
    });

    $('#edit_correo_funcionario, #edit_correo_dominio').on('input change', function () {
        var local = $('#edit_correo_funcionario').val();
        var dominio = $('#edit_correo_dominio').val();
        if (local || dominio) {
            $('#editFuncionarioModal').find('#edit_correo_oculto').val(local + dominio);
        } else {
            $('#editFuncionarioModal').find('#edit_correo_oculto').val('');
        }
    });
});

// --- NUEVO: Manejar eliminación de funcionario ---
$(document).on('click', '.delete-button', function (e) {
    e.preventDefault();
    const url = $(this).data('url');
    const message = $(this).data('message') || "¿Estás seguro de eliminar?";
    if (confirm(message)) {
        fetch(url, { method: 'POST' })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    buscarFuncionarios(1);
                }
            })
            .catch(error => alert("Error al eliminar funcionario: " + error));
    }
});