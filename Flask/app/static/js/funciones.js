/**
 * Habilita un placeholder dinámico en un campo de entrada.
 * @param {string} inputId - ID del campo de entrada.
 * @param {Array} placeholders - Lista de textos para el placeholder.
 * @param {number} interval - Intervalo en milisegundos para cambiar el placeholder.
 */
/*Funcion para cambiar el placeholder dinamicamente en una barra de busqueda*/
function enableDynamicPlaceholder(inputId, placeholders, interval = 2000) {
    const searchInput = document.getElementById(inputId);
    if (!searchInput) {
        console.error(`No se encontró el input con ID '${inputId}'`);
        return;
    }

    let index = 0;

    function rotatePlaceholder() {
        searchInput.placeholder = placeholders[index];
        index = (index + 1) % placeholders.length;
    }

    setInterval(rotatePlaceholder, interval);
}