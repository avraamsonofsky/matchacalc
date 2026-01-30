/**
 * Управление коллекциями
 */

const Collections = {
    currentUser: null,
    collections: [],
    currentCollectionId: null,
    
    async init() {
        // Проверяем авторизацию
        try {
            this.currentUser = await API.get('/api/v1/auth/me');
            
            // Проверяем подписку (любая активная) или роль admin
            const hasSubscription = this.currentUser.subscription && 
                this.currentUser.subscription.status === 'ACTIVE' &&
                this.currentUser.subscription.plan !== 'NONE';
            
            if (hasSubscription || this.currentUser.role === 'ADMIN') {
                document.getElementById('no-subscription-notice').classList.add('hidden');
                document.getElementById('collections-content').classList.remove('hidden');
                await this.loadCollections();
            } else {
                document.getElementById('no-subscription-notice').classList.remove('hidden');
                document.getElementById('collections-content').classList.add('hidden');
            }
        } catch (e) {
            // Не авторизован
            document.getElementById('no-subscription-notice').classList.remove('hidden');
            document.getElementById('collections-content').classList.add('hidden');
        }
        
        this.setupEventListeners();
    },
    
    setupEventListeners() {
        // Создание коллекции
        document.getElementById('btn-create-collection')?.addEventListener('click', () => {
            this.showModal('create-collection-modal');
        });
        
        document.getElementById('create-collection-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.createCollection();
        });
        
        // Закрытие модалок
        document.querySelectorAll('.modal-close, .modal-cancel, .modal-overlay').forEach(el => {
            el.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal-overlay') || 
                    e.target.classList.contains('modal-close') ||
                    e.target.classList.contains('modal-cancel')) {
                    this.hideAllModals();
                }
            });
        });
        
        // Добавление лотов
        document.getElementById('btn-add-lots')?.addEventListener('click', () => {
            this.hideModal('view-collection-modal');
            this.showModal('add-lots-modal');
            this.resetUrlInputs();
        });
        
        document.getElementById('btn-add-more-url')?.addEventListener('click', () => {
            this.addUrlInput();
        });
        
        document.getElementById('btn-import-lots')?.addEventListener('click', async () => {
            await this.importLots();
        });
        
        // Публикация коллекции
        document.getElementById('btn-publish-collection')?.addEventListener('click', async () => {
            await this.publishCollection();
        });
        
        // Копирование ссылки
        document.getElementById('btn-copy-link')?.addEventListener('click', () => {
            this.copyPublicLink();
        });
        
        // Расчёт по лоту
        document.getElementById('lot-years')?.addEventListener('input', (e) => {
            document.getElementById('lot-years-value').textContent = e.target.value;
        });
        
        document.getElementById('btn-calc-lot')?.addEventListener('click', async () => {
            await this.calculateLot();
        });
    },
    
    async loadCollections() {
        try {
            this.collections = await API.get('/api/v1/collections');
            this.renderCollections();
        } catch (e) {
            console.error('Ошибка загрузки коллекций:', e);
        }
    },
    
    renderCollections() {
        const list = document.getElementById('collections-list');
        const emptyState = document.getElementById('empty-state');
        
        if (this.collections.length === 0) {
            list.innerHTML = '';
            emptyState.classList.remove('hidden');
            return;
        }
        
        emptyState.classList.add('hidden');
        
        list.innerHTML = this.collections.map(coll => `
            <div class="collection-card" data-id="${coll.id}">
                <h3>${this.escapeHtml(coll.name)}</h3>
                <p>${this.escapeHtml(coll.description || 'Без описания')}</p>
                <div class="collection-meta">
                    <span class="collection-lots-count">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        </svg>
                        ${coll.lots_count} лотов
                    </span>
                    <span class="collection-status ${coll.public_slug ? 'published' : ''}">
                        ${coll.public_slug ? '✓ Опубликовано' : 'Черновик'}
                    </span>
                </div>
            </div>
        `).join('');
        
        // Обработчики кликов
        list.querySelectorAll('.collection-card').forEach(card => {
            card.addEventListener('click', () => {
                const id = parseInt(card.dataset.id);
                this.openCollection(id);
            });
        });
    },
    
    async createCollection() {
        const name = document.getElementById('collection-name').value.trim();
        const description = document.getElementById('collection-description').value.trim();
        
        if (!name) {
            alert('Введите название подборки');
            return;
        }
        
        try {
            const collection = await API.post('/api/v1/collections', {
                name,
                description: description || null
            });
            
            this.collections.unshift(collection);
            this.renderCollections();
            this.hideModal('create-collection-modal');
            
            // Очищаем форму
            document.getElementById('collection-name').value = '';
            document.getElementById('collection-description').value = '';
            
            // Открываем созданную коллекцию
            this.openCollection(collection.id);
        } catch (e) {
            alert('Ошибка создания коллекции: ' + e.message);
        }
    },
    
    async openCollection(id) {
        this.currentCollectionId = id;
        
        try {
            const collection = await API.get(`/api/v1/collections/${id}`);
            
            document.getElementById('view-collection-title').textContent = collection.name;
            document.getElementById('view-collection-description').textContent = 
                collection.description || '';
            
            // Публичная ссылка
            const linkContainer = document.getElementById('public-link-container');
            if (collection.public_slug) {
                linkContainer.classList.remove('hidden');
                document.getElementById('public-link-input').value = 
                    window.location.origin + '/c/' + collection.public_slug;
            } else {
                linkContainer.classList.add('hidden');
            }
            
            // Лоты
            this.renderLots(collection.lots);
            
            this.showModal('view-collection-modal');
        } catch (e) {
            alert('Ошибка загрузки коллекции: ' + e.message);
        }
    },
    
    renderLots(lots) {
        const grid = document.getElementById('lots-list');
        const empty = document.getElementById('lots-empty');
        
        if (!lots || lots.length === 0) {
            grid.innerHTML = '';
            empty.classList.remove('hidden');
            return;
        }
        
        empty.classList.add('hidden');
        
        grid.innerHTML = lots.map(lot => `
            <div class="lot-card" data-id="${lot.id}" style="position: relative;">
                <img src="${lot.layout_image_url || 'img/placeholder.png'}" 
                     alt="Планировка" class="lot-card-image"
                     onerror="this.src='img/placeholder.png'">
                <div class="lot-card-info">
                    <div class="lot-card-address">${this.escapeHtml(lot.address)}</div>
                    <div class="lot-card-price">
                        ${lot.discounted_price ? `
                            <span class="lot-card-price-old">${this.formatPrice(lot.original_price)}</span>
                            ${this.formatPrice(lot.discounted_price)}
                            <span class="lot-card-discount">-${lot.discount_percent}%</span>
                        ` : this.formatPrice(lot.original_price)}
                    </div>
                    <div class="lot-card-area">${lot.area} м²</div>
                </div>
                <button class="lot-card-remove" data-lot-id="${lot.id}" title="Удалить">&times;</button>
            </div>
        `).join('');
        
        // Обработчики
        grid.querySelectorAll('.lot-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.classList.contains('lot-card-remove')) {
                    const lotId = parseInt(card.dataset.id);
                    const lot = lots.find(l => l.id === lotId);
                    if (lot) {
                        this.openLotCalculator(lot);
                    }
                }
            });
        });
        
        grid.querySelectorAll('.lot-card-remove').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const lotId = parseInt(btn.dataset.lotId);
                await this.removeLotFromCollection(lotId);
            });
        });
    },
    
    async publishCollection() {
        if (!this.currentCollectionId) return;
        
        try {
            const result = await API.post(`/api/v1/collections/${this.currentCollectionId}/publish`);
            
            document.getElementById('public-link-container').classList.remove('hidden');
            document.getElementById('public-link-input').value = 
                window.location.origin + result.public_url;
            
            // Обновляем список
            await this.loadCollections();
            
            alert('Коллекция опубликована!');
        } catch (e) {
            alert('Ошибка публикации: ' + e.message);
        }
    },
    
    copyPublicLink() {
        const input = document.getElementById('public-link-input');
        input.select();
        document.execCommand('copy');
        
        const btn = document.getElementById('btn-copy-link');
        btn.innerHTML = '✓';
        setTimeout(() => {
            btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>`;
        }, 1500);
    },
    
    // URL инпуты для добавления лотов
    resetUrlInputs() {
        const container = document.getElementById('url-inputs-container');
        container.innerHTML = `
            <div class="url-input-row">
                <input type="url" class="url-input" placeholder="https://www.cian.ru/sale/commercial/...">
                <button type="button" class="btn-remove-url hidden">&times;</button>
            </div>
        `;
    },
    
    addUrlInput() {
        const container = document.getElementById('url-inputs-container');
        const rows = container.querySelectorAll('.url-input-row');
        
        if (rows.length >= 20) {
            alert('Максимум 20 ссылок');
            return;
        }
        
        const row = document.createElement('div');
        row.className = 'url-input-row';
        row.innerHTML = `
            <input type="url" class="url-input" placeholder="https://www.cian.ru/sale/commercial/...">
            <button type="button" class="btn-remove-url">&times;</button>
        `;
        
        row.querySelector('.btn-remove-url').addEventListener('click', () => {
            row.remove();
        });
        
        container.appendChild(row);
        row.querySelector('.url-input').focus();
    },
    
    async importLots() {
        const inputs = document.querySelectorAll('#url-inputs-container .url-input');
        const urls = [];
        
        inputs.forEach(input => {
            const url = input.value.trim();
            if (url) {
                urls.push(url);
            }
        });
        
        if (urls.length === 0) {
            alert('Добавьте хотя бы одну ссылку');
            return;
        }
        
        const progress = document.getElementById('import-progress');
        const progressFill = progress.querySelector('.progress-fill');
        const progressText = progress.querySelector('.progress-text');
        
        progress.classList.remove('hidden');
        document.getElementById('btn-import-lots').disabled = true;
        
        try {
            const result = await API.post(`/api/v1/collections/${this.currentCollectionId}/lots`, {
                cian_urls: urls
            });
            
            progressFill.style.width = '100%';
            progressText.textContent = `Импортировано: ${result.total_added} из ${urls.length}`;
            
            if (result.errors && result.errors.length > 0) {
                console.warn('Ошибки импорта:', result.errors);
            }
            
            // Обновляем коллекцию
            setTimeout(async () => {
                this.hideModal('add-lots-modal');
                progress.classList.add('hidden');
                progressFill.style.width = '0';
                document.getElementById('btn-import-lots').disabled = false;
                
                await this.openCollection(this.currentCollectionId);
                await this.loadCollections();
            }, 1000);
            
        } catch (e) {
            alert('Ошибка импорта: ' + e.message);
            progress.classList.add('hidden');
            document.getElementById('btn-import-lots').disabled = false;
        }
    },
    
    async removeLotFromCollection(lotId) {
        if (!confirm('Удалить лот из подборки?')) return;
        
        try {
            await API.delete(`/api/v1/collections/${this.currentCollectionId}/lots/${lotId}`);
            await this.openCollection(this.currentCollectionId);
            await this.loadCollections();
        } catch (e) {
            alert('Ошибка удаления: ' + e.message);
        }
    },
    
    async openLotCalculator(lot) {
        this.hideModal('view-collection-modal');
        
        // Заполняем данные
        document.getElementById('lot-image').src = lot.layout_image_url || 'img/placeholder.png';
        document.getElementById('lot-address').textContent = lot.address;
        document.getElementById('lot-price').textContent = this.formatPrice(
            lot.discounted_price || lot.original_price
        );
        document.getElementById('lot-area').textContent = lot.area;
        
        // Загружаем отчёты
        try {
            const reports = await API.get('/api/v1/reports');
            const select = document.getElementById('lot-report');
            select.innerHTML = reports.map(r => 
                `<option value="${r.id}">${r.provider} • ${r.period}</option>`
            ).join('');
        } catch (e) {
            console.error('Ошибка загрузки отчётов:', e);
        }
        
        // Сохраняем ID лота для расчёта
        document.getElementById('lot-calculator-modal').dataset.lotId = lot.id;
        document.getElementById('lot-results').classList.add('hidden');
        
        this.showModal('lot-calculator-modal');
    },
    
    async calculateLot() {
        const modal = document.getElementById('lot-calculator-modal');
        const lotId = parseInt(modal.dataset.lotId);
        
        const data = {
            holding_years: parseInt(document.getElementById('lot-years').value),
            scenario_id: document.getElementById('lot-scenario').value,
            report_id: parseInt(document.getElementById('lot-report').value)
        };
        
        try {
            const result = await API.post(`/api/v1/calc/from-lot/${lotId}`, data);
            this.showLotResults(result);
        } catch (e) {
            alert('Ошибка расчёта: ' + e.message);
        }
    },
    
    showLotResults(result) {
        const container = document.getElementById('lot-results');
        
        container.innerHTML = `
            <div class="results-grid">
                <div class="result-item">
                    <span class="result-label">Срок окупаемости (аренда + продажа)</span>
                    <span class="result-value">${this.formatYears(result.static_metrics.payback_rent_and_sale_years)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Прибыль от аренды</span>
                    <span class="result-value">${this.formatPrice(result.dynamic_metrics.rent_income_total)} 
                        <small>(${result.dynamic_metrics.rent_income_yield_percent.toFixed(1)}% годовых)</small>
                    </span>
                </div>
                <div class="result-item">
                    <span class="result-label">Прибыль от продажи</span>
                    <span class="result-value">${this.formatPrice(result.dynamic_metrics.sale_profit)}
                        <small>(+${result.dynamic_metrics.sale_profit_percent.toFixed(1)}%)</small>
                    </span>
                </div>
                <div class="result-item">
                    <span class="result-label">Совокупная прибыль</span>
                    <span class="result-value highlight">${this.formatPrice(result.dynamic_metrics.total_profit)}
                        <small>(+${result.dynamic_metrics.total_profit_percent.toFixed(1)}%)</small>
                    </span>
                </div>
                <div class="result-item">
                    <span class="result-label">NPV</span>
                    <span class="result-value">${this.formatPrice(result.dynamic_metrics.npv)}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">IRR</span>
                    <span class="result-value">${result.dynamic_metrics.irr_percent.toFixed(2)}%</span>
                </div>
            </div>
        `;
        
        container.classList.remove('hidden');
    },
    
    // Утилиты
    showModal(id) {
        document.getElementById(id)?.classList.remove('hidden');
    },
    
    hideModal(id) {
        document.getElementById(id)?.classList.add('hidden');
    },
    
    hideAllModals() {
        document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));
    },
    
    formatPrice(value) {
        if (!value) return '—';
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            maximumFractionDigits: 0
        }).format(value);
    },
    
    formatYears(years) {
        if (!years) return '—';
        const y = Math.floor(years);
        const m = Math.round((years - y) * 12);
        return m > 0 ? `${y} лет ${m} мес` : `${y} лет`;
    },
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    Auth.init();
    Collections.init();
});
