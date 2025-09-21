// Espera o documento carregar completamente
document.addEventListener('DOMContentLoaded', function() {
    // Seleciona todos os elementos de alerta
    const alertList = document.querySelectorAll('.alert');

    // Para cada alerta encontrado...
    alertList.forEach(function(alert) {
        // ...define um temporizador para 3 segundos (3000 milissegundos)
        setTimeout(function() {
            // Cria uma instância do componente Alert do Bootstrap para o elemento
            // e chama o método .close() para acionar a animação de fade out
            new bootstrap.Alert(alert).close();
        }, 2000);
    });
});