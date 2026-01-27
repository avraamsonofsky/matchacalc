/**
 * Full-page scroll controller
 * Управляет прокруткой между секциями и скрытием навбара
 */

document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.getElementById('navbar');
    const sections = document.querySelectorAll('.fullpage-section');
    const scrollToCalcBtn = document.getElementById('scroll-to-calc');
    
    let currentSection = 0;
    let isScrolling = false;
    let scrollTimeout;
    
    // Определяем текущую секцию при прокрутке
    const updateCurrentSection = () => {
        if (!navbar) return;
        
        const scrollTop = window.scrollY;
        const windowHeight = window.innerHeight;
        
        sections.forEach((section, index) => {
            const rect = section.getBoundingClientRect();
            if (rect.top <= windowHeight / 2 && rect.bottom >= windowHeight / 2) {
                currentSection = index;
            }
        });
        
        // Скрываем/показываем навбар только если мы действительно не на первой секции
        // И только если навбар уже инициализирован (не скрыт другими скриптами)
        if (currentSection > 0 && scrollTop > 50) {
            navbar.classList.add('hidden');
        } else {
            navbar.classList.remove('hidden');
        }
    };
    
    // Прокрутка к секции
    const scrollToSection = (index) => {
        if (index < 0 || index >= sections.length) return;
        if (isScrolling) return;
        
        isScrolling = true;
        currentSection = index;
        
        sections[index].scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
        
        // Разблокируем прокрутку через некоторое время
        setTimeout(() => {
            isScrolling = false;
        }, 800);
    };
    
    // Обработчик прокрутки колёсиком/тачпадом
    const handleWheel = (e) => {
        if (isScrolling) {
            return; // CSS scroll-snap сам остановит на секции
        }
        
        // Проверяем, есть ли скроллируемый контент внутри секции
        const target = e.target;
        const scrollableParent = findScrollableParent(target);
        
        if (scrollableParent && scrollableParent !== document.documentElement) {
            const { scrollTop, scrollHeight, clientHeight } = scrollableParent;
            const isAtTop = scrollTop === 0;
            const isAtBottom = scrollTop + clientHeight >= scrollHeight - 1;
            
            // Если есть скроллируемый контент и не на границе, не перехватываем
            if (scrollHeight > clientHeight) {
                if (e.deltaY < 0 && !isAtTop) return;
                if (e.deltaY > 0 && !isAtBottom) return;
            }
        }
        
        // Дебаунс для предотвращения множественных срабатываний
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            if (e.deltaY > 0) {
                // Прокрутка вниз
                scrollToSection(currentSection + 1);
            } else if (e.deltaY < 0) {
                // Прокрутка вверх
                scrollToSection(currentSection - 1);
            }
        }, 50);
    };
    
    // Находим скроллируемый родительский элемент
    const findScrollableParent = (element) => {
        while (element && element !== document.body) {
            const style = window.getComputedStyle(element);
            const overflowY = style.overflowY;
            
            if (overflowY === 'scroll' || overflowY === 'auto') {
                if (element.scrollHeight > element.clientHeight) {
                    return element;
                }
            }
            element = element.parentElement;
        }
        return document.documentElement;
    };
    
    // Обработчик свайпа на тач-устройствах
    let touchStartY = 0;
    let touchEndY = 0;
    
    const handleTouchStart = (e) => {
        touchStartY = e.touches[0].clientY;
    };
    
    const handleTouchEnd = (e) => {
        touchEndY = e.changedTouches[0].clientY;
        const diff = touchStartY - touchEndY;
        
        if (Math.abs(diff) > 50) {
            if (diff > 0) {
                // Свайп вверх - прокрутка вниз
                scrollToSection(currentSection + 1);
            } else {
                // Свайп вниз - прокрутка вверх
                scrollToSection(currentSection - 1);
            }
        }
    };
    
    // Кнопка "Начать расчёт"
    if (scrollToCalcBtn) {
        scrollToCalcBtn.addEventListener('click', (e) => {
            e.preventDefault();
            scrollToSection(1);
        });
    }
    
    // Слушатели событий
    window.addEventListener('scroll', updateCurrentSection, { passive: true });
    
    // Wheel события для тачпада - CSS scroll-snap делает основную работу,
    // но добавляем JS для более точного контроля
    window.addEventListener('wheel', handleWheel, { passive: true });
    
    // Touch события для сенсорных экранов
    document.addEventListener('touchstart', handleTouchStart, { passive: true });
    document.addEventListener('touchend', handleTouchEnd, { passive: true });
    
    // Инициализация - откладываем, чтобы навбар успел инициализироваться
    // Убеждаемся, что навбар виден на первой секции
    if (navbar) {
        navbar.classList.remove('hidden');
    }
    
    // Обновляем состояние после небольшой задержки
    setTimeout(() => {
        updateCurrentSection();
    }, 100);
    
    // Клавиатурная навигация
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown' || e.key === 'PageDown') {
            e.preventDefault();
            scrollToSection(currentSection + 1);
        } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
            e.preventDefault();
            scrollToSection(currentSection - 1);
        } else if (e.key === 'Home') {
            e.preventDefault();
            scrollToSection(0);
        } else if (e.key === 'End') {
            e.preventDefault();
            scrollToSection(sections.length - 1);
        }
    });
    
    console.log('Fullpage scroll initialized');
});
