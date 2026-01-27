// Утилиты
const Utils = {
    formatNumber: (num) => {
        if (num === null || num === undefined || isNaN(num)) return '—';
        return new Intl.NumberFormat('ru-RU', {
            maximumFractionDigits: 2
        }).format(num);
    },
    
    formatCurrency: (num) => {
        if (num === null || num === undefined || isNaN(num)) return '—';
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            maximumFractionDigits: 0
        }).format(num);
    },
    
    formatPercent: (num) => {
        if (num === null || num === undefined || isNaN(num)) return '—';
        return `${(num * 100).toFixed(2)}%`;
    },
    
    formatYears: (years) => {
        if (years === null || years === undefined || isNaN(years)) return '—';
        const rounded = Math.round(years * 10) / 10;
        if (rounded === 1) return '1 год';
        if (rounded < 5) return `${rounded} года`;
        return `${rounded} лет`;
    },
    
    showElement: (element) => {
        if (element) {
            element.classList.remove('hidden');
            element.style.display = '';
        }
    },
    
    hideElement: (element) => {
        if (element) {
            element.classList.add('hidden');
            element.style.display = 'none';
        }
    }
};
