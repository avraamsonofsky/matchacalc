// Калькулятор
const Calculator = {
    debounceTimer: null,
    
    init: () => {
        Calculator.loadDropdowns();
        Calculator.setupSlider();
        Calculator.setupForm();
        Calculator.setupYearSelect();
        Calculator.setupPriceInput();
        Calculator.setDefaultScenario();
    },
    
    async loadDropdowns() {
        try {
            console.log('Начинаем загрузку данных для выпадающих списков...');
            
            // Загружаем районы
            console.log('Загружаем районы...');
            const locations = await API.getLocationGroups();
            console.log('Получены районы:', locations);
            const locationSelect = document.getElementById('location-group');
            if (!locationSelect) {
                console.error('Элемент location-group не найден!');
                return;
            }
            if (!locations || locations.length === 0) {
                console.warn('Районы не получены или пустой массив');
            } else {
                locations.forEach(loc => {
                    const option = document.createElement('option');
                    option.value = loc.id;
                    option.textContent = loc.name;
                    locationSelect.appendChild(option);
                });
                console.log(`Добавлено ${locations.length} районов`);
            }
            
            // Загружаем сценарии
            console.log('Загружаем сценарии...');
            const scenarios = await API.getScenarios();
            console.log('Получены сценарии:', scenarios);
            const scenarioSelect = document.getElementById('scenario');
            if (!scenarioSelect) {
                console.error('Элемент scenario не найден!');
                return;
            }
            if (!scenarios || scenarios.length === 0) {
                console.warn('Сценарии не получены или пустой массив');
            } else {
                scenarios.forEach(scenario => {
                    const option = document.createElement('option');
                    option.value = scenario.id;
                    option.textContent = scenario.name;
                    scenarioSelect.appendChild(option);
                });
                console.log(`Добавлено ${scenarios.length} сценариев`);
                
                // Предустановка на "Базовый"
                const baseScenario = scenarios.find(s => s.name.toLowerCase().includes('базов'));
                if (baseScenario) {
                    scenarioSelect.value = baseScenario.id;
                    console.log('Установлен базовый сценарий по умолчанию');
                }
            }
            
            // Загружаем отчёты
            console.log('Загружаем отчёты...');
            const reports = await API.getReports();
            console.log('Получены отчёты:', reports);
            const reportSelect = document.getElementById('report');
            if (!reportSelect) {
                console.error('Элемент report не найден!');
                return;
            }
            if (!reports || reports.length === 0) {
                console.warn('Отчёты не получены или пустой массив');
            } else {
                reports.forEach(report => {
                    const option = document.createElement('option');
                    option.value = report.id;
                    // Форматируем название красиво: "Nikoliers • Q4 2025"
                    const providerName = Calculator.formatProviderName(report.provider);
                    const periodFormatted = Calculator.formatPeriod(report.period);
                    option.textContent = `${providerName} • ${periodFormatted}`;
                    reportSelect.appendChild(option);
                });
                console.log(`Добавлено ${reports.length} отчётов`);
            }
            
            console.log('Загрузка данных завершена успешно!');
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
            console.error('Детали ошибки:', error.message, error.stack);
            alert('Ошибка загрузки данных. Проверьте консоль браузера (F12).');
        }
    },
    
    setupSlider() {
        const slider = document.getElementById('holding-years');
        const valueDisplay = document.getElementById('holding-years-value');
        
        if (slider && valueDisplay) {
            slider.addEventListener('input', (e) => {
                const years = parseInt(e.target.value);
                const yearWord = years === 1 ? 'год' : years <= 4 ? 'года' : 'лет';
                valueDisplay.textContent = `${years} ${yearWord}`;
                
                // Авто-расчёт при перемещении ползунка (с дебаунсом)
                Calculator.autoCalculateDebounced();
            });
        }
    },
    
    // Форматирование ввода стоимости с разделителями тысяч
    setupPriceInput() {
        const priceInput = document.getElementById('purchase-price');
        if (!priceInput) return;
        
        priceInput.addEventListener('input', (e) => {
            // Сохраняем позицию курсора
            const cursorPos = e.target.selectionStart;
            const oldLength = e.target.value.length;
            
            // Удаляем все нечисловые символы
            let value = e.target.value.replace(/\D/g, '');
            
            // Форматируем с разделителями тысяч (обычные пробелы)
            if (value) {
                // toLocaleString использует неразрывный пробел (U+00A0), заменяем на обычный
                value = parseInt(value).toLocaleString('ru-RU').replace(/\s/g, ' ');
            }
            
            e.target.value = value;
            
            // Восстанавливаем позицию курсора с учётом добавленных пробелов
            const newLength = value.length;
            const diff = newLength - oldLength;
            e.target.setSelectionRange(cursorPos + diff, cursorPos + diff);
        });
    },
    
    // Предустановка прогноза на "Базовый"
    setDefaultScenario() {
        // Будет вызвано после загрузки сценариев
    },
    
    // Авто-расчёт с дебаунсом (чтобы не перегружать сервер)
    autoCalculateDebounced() {
        if (Calculator.debounceTimer) {
            clearTimeout(Calculator.debounceTimer);
        }
        
        Calculator.debounceTimer = setTimeout(() => {
            // Проверяем, что основные поля заполнены
            const priceInput = document.getElementById('purchase-price');
            const areaInput = document.getElementById('area');
            const locationSelect = document.getElementById('location-group');
            const scenarioSelect = document.getElementById('scenario');
            const reportSelect = document.getElementById('report');
            
            const price = priceInput ? priceInput.value.replace(/\D/g, '') : '';
            const area = areaInput ? areaInput.value : '';
            const location = locationSelect ? locationSelect.value : '';
            const scenario = scenarioSelect ? scenarioSelect.value : '';
            const report = reportSelect ? reportSelect.value : '';
            
            // Выполняем расчёт только если основные поля заполнены
            if (price && area && location && scenario && report) {
                Calculator.calculate(true); // true = silent mode (без изменения кнопки)
            }
        }, 300); // 300ms задержка
    },
    
    setupYearSelect() {
        const yearSelect = document.getElementById('rve-year');
        if (!yearSelect) return;
        
        const currentYear = new Date().getFullYear();
        for (let year = currentYear; year <= currentYear + 5; year++) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearSelect.appendChild(option);
        }
    },
    
    // Форматирование названия провайдера
    formatProviderName(provider) {
        const providerNames = {
            'nikoliers': 'Nikoliers',
            'nf_group': 'NF Group',
            'cbre': 'CBRE',
            'jll': 'JLL',
            'knight_frank': 'Knight Frank',
            'colliers': 'Colliers',
            'cushman': 'Cushman & Wakefield'
        };
        return providerNames[provider.toLowerCase()] || 
               provider.charAt(0).toUpperCase() + provider.slice(1).replace(/_/g, ' ');
    },
    
    // Форматирование периода
    formatPeriod(period) {
        // "2025-Q4" -> "Q4 2025"
        const match = period.match(/(\d{4})-Q(\d)/);
        if (match) {
            return `Q${match[2]} ${match[1]}`;
        }
        return period;
    },
    
    setupForm() {
        const form = document.getElementById('calculator-form');
        const calculateBtn = document.getElementById('calculate-btn');
        
        if (calculateBtn) {
            calculateBtn.addEventListener('click', async (e) => {
                // Проверяем ограничения перед расчётом
                if (AccessControl && !AccessControl.canCalculate()) {
                    e.preventDefault();
                    AccessControl.showSubscriptionModal();
                    return false;
                }
                
                // Записываем нажатие
                if (AccessControl) {
                    AccessControl.recordCalculate();
                }
                
                await Calculator.calculate();
            });
        }
    },
    
    async calculate(silent = false) {
        const form = document.getElementById('calculator-form');
        
        // В тихом режиме не проверяем валидность формы
        if (!silent && !form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        // Получаем цену, удаляя разделители тысяч
        const priceValue = document.getElementById('purchase-price').value.replace(/\D/g, '');
        const purchasePrice = parseFloat(priceValue);
        const area = parseFloat(document.getElementById('area').value);
        const locationGroupId = document.getElementById('location-group').value;
        const month = document.getElementById('rve-month').value;
        const year = document.getElementById('rve-year').value;
        const holdingYears = parseInt(document.getElementById('holding-years').value);
        const scenarioId = document.getElementById('scenario').value;
        const reportId = parseInt(document.getElementById('report').value);
        
        // Дата ввода необязательна - если не выбрана, считаем что лот уже введён
        let rveDate = null;
        if (month && year && month !== 'Мес' && year !== 'Год') {
            const monthNum = Calculator.getMonthNumber(month);
            if (monthNum) {
                rveDate = `${year}-${monthNum.padStart(2, '0')}-01`;
            }
        }
        
        // WACC (необязательно)
        const waccInput = document.getElementById('wacc');
        const waccValue = waccInput ? parseFloat(waccInput.value) : NaN;

        const data = {
            purchase_price: purchasePrice,
            area: area,
            location_group_id: locationGroupId,
            holding_years: holdingYears,
            scenario_id: scenarioId,
            report_id: reportId
        };

        // Добавляем WACC, если введён
        if (!isNaN(waccValue) && waccValue >= 0) {
            data.wacc = waccValue;
        }
        
        // Добавляем дату только если она указана
        if (rveDate) {
            data.rve_date = rveDate;
        }
        
        try {
            const calculateBtn = document.getElementById('calculate-btn');
            
            if (!silent) {
                calculateBtn.disabled = true;
                calculateBtn.textContent = 'Вычисляем...';
            }
            
            const result = await API.calculate(data);
            Calculator.displayResults(result);
        } catch (error) {
            if (!silent) {
                alert('Ошибка расчёта: ' + error.message);
            }
            console.error('Ошибка расчёта:', error);
        } finally {
            if (!silent) {
                const calculateBtn = document.getElementById('calculate-btn');
                calculateBtn.disabled = false;
                calculateBtn.innerHTML = 'Рассчитать доходность <svg class="arrow" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6 3L12 9L6 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
            }
        }
    },
    
    // Конвертация названия месяца в номер
    getMonthNumber(month) {
        const months = {
            'Янв': '01', 'Фев': '02', 'Мар': '03', 'Апр': '04',
            'Май': '05', 'Июн': '06', 'Июл': '07', 'Авг': '08',
            'Сен': '09', 'Окт': '10', 'Ноя': '11', 'Дек': '12'
        };
        return months[month] || null;
    },
    
    displayResults(data) {
        const resultsPanel = document.getElementById('results');
        Utils.showElement(resultsPanel);
        
        // Функция для обновления значения и активации
        const updateValue = (elementId, value) => {
            const el = document.getElementById(elementId);
            if (el) {
                el.textContent = value;
                el.classList.remove('placeholder');
                el.classList.add('active');
            }
        };
        
        // Статические метрики
        if (data.static_metrics) {
            updateValue('payback-rent', Utils.formatYears(data.static_metrics.payback_rent_years));
            updateValue('payback-rent-sale', Utils.formatYears(data.static_metrics.payback_rent_sale_years));
            updateValue('double-price', Utils.formatYears(data.static_metrics.double_price_years));
        }
        
        // Динамические метрики
        if (data.dynamic_metrics) {
            // Прибыль от аренды (rent_income_yield_percent уже доля, formatPercent умножит на 100)
            updateValue('rent-income', Utils.formatCurrency(data.dynamic_metrics.rent_income_total));
            updateValue('rent-yield', `(${Utils.formatPercent(data.dynamic_metrics.rent_income_yield_percent)})`);
            
            // Прибыль от продажи
            updateValue('sale-profit', Utils.formatCurrency(data.dynamic_metrics.sale_profit));
            updateValue('sale-profit-percent', `(${Utils.formatPercent(data.dynamic_metrics.sale_profit_percent)})`);
            
            // Совокупная прибыль
            updateValue('total-profit', Utils.formatCurrency(data.dynamic_metrics.total_profit));
            updateValue('total-profit-percent', `(${Utils.formatPercent(data.dynamic_metrics.total_profit_percent)})`);
            
            // NPV (показываем "—" если не рассчитан из-за отсутствия WACC) и IRR
            if (data.dynamic_metrics.npv != null) {
                updateValue('npv', Utils.formatCurrency(data.dynamic_metrics.npv));
            } else {
                updateValue('npv', '— (укажите WACC)');
            }
            updateValue('irr', Utils.formatPercent(data.dynamic_metrics.irr_percent));
        }
        
        // Прокрутка к результатам (на мобильных скроллим к началу блока)
        const isMobile = window.innerWidth <= 768;
        const resultsContainer = document.getElementById('results-panel');
        if (isMobile && resultsContainer) {
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    },
    
    // Сброс результатов к placeholder
    resetResults() {
        const placeholderData = {
            'payback-rent': '12 лет 4 мес',
            'payback-rent-sale': '7 лет 8 мес',
            'double-price': '9 лет 2 мес',
            'rent-income': '28 350 000 ₽',
            'rent-yield': '(56.7%)',
            'sale-profit': '42 500 000 ₽',
            'sale-profit-percent': '(85%)',
            'total-profit': '70 850 000 ₽',
            'total-profit-percent': '(141.7%)',
            'npv': '— (укажите WACC)',
            'irr': '15.3%'
        };
        
        Object.entries(placeholderData).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el) {
                el.textContent = value;
                el.classList.add('placeholder');
                el.classList.remove('active');
            }
        });
    }
};

// Инициализация при загрузке
function initCalculator() {
    console.log('Инициализация калькулятора...');
    console.log('DOM готов:', document.readyState);
    
    // Проверяем наличие элементов
    const locationSelect = document.getElementById('location-group');
    const scenarioSelect = document.getElementById('scenario');
    const reportSelect = document.getElementById('report');
    
    if (!locationSelect) {
        console.error('Элемент location-group не найден в DOM!');
        return;
    }
    if (!scenarioSelect) {
        console.error('Элемент scenario не найден в DOM!');
        return;
    }
    if (!reportSelect) {
        console.error('Элемент report не найден в DOM!');
        return;
    }
    
    console.log('Все элементы найдены, запускаем инициализацию...');
    Calculator.init();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCalculator);
} else {
    // DOM уже загружен
    setTimeout(initCalculator, 100); // Небольшая задержка для гарантии
}
