$(document).ready(function() {
    // Inicializar DataTables
    let table = $('#posts').DataTable({
      "paging": true,
      "searching": true,
      "ordering": true,
      "info": true,
      "lengthChange": false,
      "pageLength": 8,
      "language": {
        "search": "<div style='text-align: center; width: 100%;'>Buscar Unidad:</div>"
      }
    });
  
    // Asegurarse de que los estilos se apliquen después de la inicialización
    table.on('draw', function() {
      // Centrar el campo de búsqueda
      $("#posts_filter").css({
        "text-align": "center",
        "width": "100%",
        "display": "flex",
        "justify-content": "center"
      });
  
      // Centrar el paginador
      $(".dataTables_paginate").css({
        "text-align": "center",
        "width": "100%",
        "display": "flex",
        "justify-content": "center"
      });
  
      // Centrar los botones de paginación
      $(".dataTables_paginate > .paginate_button").css({
        "margin": "0 5px"
      });
    });
  });
  