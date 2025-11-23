// Funções gerais para o site

document.addEventListener('DOMContentLoaded', function() {
    // Filtro de categorias
    const categoryButtons = document.querySelectorAll('.category-btn');
    if (categoryButtons.length > 0) {
        categoryButtons.forEach(button => {
            button.addEventListener('click', function() {
                const categoria = this.getAttribute('data-categoria') || 'todos';
                // Redireciona para a página de receitas com o filtro de categoria
                window.location.href = `/receitas?categoria=${encodeURIComponent(categoria)}`;
            });
        });
    }
    
    // Busca de receitas (implementação futura)
    const searchInput = document.querySelector('.search-bar input');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                // Implementação futura de busca
                // Por enquanto, não faz nada
            }
        });
    }
    
    // Validação de formulários
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Validação básica - você pode expandir conforme necessário
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'red';
                } else {
                    field.style.borderColor = '';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                // Remove o alert, apenas previne o submit
            }
        });
    });
    
    // Paginação (implementação futura)
    const paginationButtons = document.querySelectorAll('.pagination-btn');
    if (paginationButtons.length > 0) {
        paginationButtons.forEach(button => {
            button.addEventListener('click', function() {
                if (!this.classList.contains('active')) {
                    // Remove a classe active de todos os botões
                    paginationButtons.forEach(btn => btn.classList.remove('active'));
                    // Adiciona a classe active ao botão clicado
                    this.classList.add('active');
                    
                    // Implementação futura de paginação
                    // Por enquanto, não faz nada
                }
            });
        });
    }
    
    // Newsletter (implementação futura)
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Implementação futura de newsletter
            // Por enquanto, apenas reseta o formulário
            this.reset();
        });
    }
    
    // User menu dropdown
    const userMenuToggle = document.getElementById('userMenuToggle');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenuToggle && userDropdown) {
        userMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            userDropdown.classList.toggle('active');
        });
        
        // Fechar dropdown ao clicar em um link dentro dele
        const dropdownLinks = userDropdown.querySelectorAll('a');
        dropdownLinks.forEach(link => {
            link.addEventListener('click', function() {
                userDropdown.classList.remove('active');
            });
        });
        
        // Fechar dropdown ao clicar fora
        document.addEventListener('click', function(e) {
            if (!userMenuToggle.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.remove('active');
            }
        });
    }
});