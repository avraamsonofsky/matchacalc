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
    // На мобильных всегда показываем
    const updateNavbar = () => {
        if (!navbar) return;
        
        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            navbar.classList.remove('hidden');
            return;
        }
        
        const scrollTop = window.scrollY;
        if (scrollTop > 100) {
            navbar.classList.add('hidden');
        } else {
            navbar.classList.remove('hidden');
        }
    };
    
    // Кнопка "Начать расчёт" — плавная прокрутка к калькулятору с учётом шапки
    if (scrollToCalcBtn && calculatorSection) {
        scrollToCalcBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const navbarHeight = navbar ? navbar.offsetHeight : 60;
            const targetPosition = calculatorSection.offsetTop - navbarHeight - 10;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
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
