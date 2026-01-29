/**
 * Простой контроллер прокрутки
 * Только кнопка "Начать расчёт" плавно скроллит к калькулятору
 * Остальная прокрутка — обычная браузерная
 */

document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.getElementById('navbar');
    const scrollToCalcBtn = document.getElementById('scroll-to-calc');
    const calculatorSection = document.getElementById('calculator');
    
    // Показываем/скрываем навбар в зависимости от позиции прокрутки
    const updateNavbar = () => {
        if (!navbar) return;
        
        const scrollTop = window.scrollY;
        
        // Скрываем навбар, если прокрутили вниз больше чем на 100px
        if (scrollTop > 100) {
            navbar.classList.add('hidden');
        } else {
            navbar.classList.remove('hidden');
        }
    };
    
    // Кнопка "Начать расчёт" — плавная прокрутка к калькулятору
    if (scrollToCalcBtn && calculatorSection) {
        scrollToCalcBtn.addEventListener('click', (e) => {
            e.preventDefault();
            calculatorSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
    }
    
    // Слушатель scroll для навбара
    window.addEventListener('scroll', updateNavbar, { passive: true });
    
    // Инициализация
    if (navbar) {
        navbar.classList.remove('hidden');
    }
    
    console.log('Simple scroll initialized');
});
