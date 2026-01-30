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
            e.stopPropagation();
            // Навбар может быть скрыт, берём фиксированное значение
            const navbarHeight = 70;
            const targetPosition = calculatorSection.getBoundingClientRect().top + window.scrollY - navbarHeight;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
            console.log('Scroll to calculator:', targetPosition);
        });
        console.log('Scroll button initialized');
    } else {
        console.warn('Scroll button or calculator section not found', { scrollToCalcBtn, calculatorSection });
    }
    
    // Слушатель scroll для навбара
    window.addEventListener('scroll', updateNavbar, { passive: true });
    
    // Инициализация
    if (navbar) {
        navbar.classList.remove('hidden');
    }
    
    console.log('Simple scroll initialized');
});
