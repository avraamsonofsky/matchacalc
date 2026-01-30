/**
 * Управление коллекциями - упрощённый UX
 */

const Collections = {
    currentUser: null,
    collections: [],
    currentCollectionId: null,
    currentLots: [],
    
    async init() {
        // Проверяем авторизацию
        try {
            this.currentUser = await API.get('/auth/me');
            
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
            this.openModal();
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
        
        // Добавление URL инпутов
        document.getElementById('btn-add-more-url')?.addEventListener('click', () => {
            this.addUrlInput();
        });
        
        // Сохранение коллекции
        document.getElementById('btn-save-collection')?.addEventListener('click', async () => {
            await this.saveCollection();
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
            this.collections = await API.get('/collections');
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
                this.openModal(id);
            });
        });
    },
    
    // Открыть модалку (создание или редактирование)
    async openModal(collectionId = null) {
        this.currentCollectionId = collectionId;
        this.currentLots = [];
        
        const modal = document.getElementById('collection-modal');
        const title = document.getElementById('modal-title');
        const nameInput = document.getElementById('collection-name');
        const descInput = document.getElementById('collection-description');
        const publishBtn = document.getElementById('btn-publish-collection');
        const linkContainer = document.getElementById('public-link-container');
        const existingLotsSection = document.getElementById('existing-lots-section');
        
        // Сбросить URL инпуты
        this.resetUrlInputs();
        
        if (collectionId) {
            // Редактирование существующей
            title.textContent = 'Редактировать подборку';
            publishBtn.classList.remove('hidden');
            
            try {
                const collection = await API.get(`/collections/${collectionId}`);
                nameInput.value = collection.name;
                descInput.value = collection.description || '';
                this.currentLots = collection.lots || [];
                
                // Публичная ссылка
                if (collection.public_slug) {
                    linkContainer.classList.remove('hidden');
                    document.getElementById('public-link-input').value = 
                        window.location.origin + '/c/' + collection.public_slug;
                } else {
                    linkContainer.classList.add('hidden');
                }
                
                // Показать существующие лоты
                if (this.currentLots.length > 0) {
                    existingLotsSection.classList.remove('hidden');
                    this.renderLots(this.currentLots);
                } else {
                    existingLotsSection.classList.add('hidden');
                }
            } catch (e) {
                alert('Ошибка загрузки коллекции: ' + e.message);
                return;
            }
        } else {
            // Создание новой
            title.textContent = 'Новая подборка';
            nameInput.value = '';
            descInput.value = '';
            publishBtn.classList.add('hidden');
            linkContainer.classList.add('hidden');
            existingLotsSection.classList.add('hidden');
        }
        
        modal.classList.remove('hidden');
        nameInput.focus();
    },
    
    // Сохранить коллекцию (создать или обновить) + импорт лотов
    async saveCollection() {
        const name = document.getElementById('collection-name').value.trim();
        const description = document.getElementById('collection-description').value.trim();
        
        if (!name) {
            alert('Введите название подборки');
            return;
        }
        
        const saveBtn = document.getElementById('btn-save-collection');
        saveBtn.disabled = true;
        saveBtn.textContent = 'Сохраняем...';
        
        try {
            let collectionId = this.currentCollectionId;
            
            // Создание или обновление
            if (!collectionId) {
                // Создаём новую
                const collection = await API.post('/collections', {
                    name,
                    description: description || null
                });
                collectionId = collection.id;
                this.currentCollectionId = collectionId;
            } else {
                // Обновляем существующую (TODO: добавить API для обновления)
                // Пока просто продолжаем
            }
            
            // Импорт лотов
            const urls = this.getUrls();
            if (urls.length > 0) {
                await this.importLots(collectionId, urls);
            }
            
            // Обновляем список и закрываем
            await this.loadCollections();
            this.hideAllModals();
            
        } catch (e) {
            alert('Ошибка сохранения: ' + e.message);
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = 'Сохранить';
        }
    },
    
    // Получить URL из инпутов
    getUrls() {
        const inputs = document.querySelectorAll('#url-inputs-container .url-input');
        const urls = [];
        
        inputs.forEach(input => {
            const url = input.value.trim();
            if (url) {
                urls.push(url);
            }
        });
        
        return urls;
    },
    
    // Импорт лотов
    async importLots(collectionId, urls) {
        const progress = document.getElementById('import-progress');
        const progressFill = progress.querySelector('.progress-fill');
        const progressText = progress.querySelector('.progress-text');
        
        progress.classList.remove('hidden');
        progressFill.style.width = '0%';
        progressText.textContent = 'Импортируем лоты...';
        
        try {
            const result = await API.post(`/collections/${collectionId}/lots`, {
                cian_urls: urls
            });
            
            progressFill.style.width = '100%';
            progressText.textContent = `Импортировано: ${result.total_added} из ${urls.length}`;
            
            if (result.errors && result.errors.length > 0) {
                console.warn('Ошибки импорта:', result.errors);
            }
            
            // Небольшая задержка чтобы показать результат
            await new Promise(resolve => setTimeout(resolve, 800));
            
        } catch (e) {
            throw e;
        } finally {
            progress.classList.add('hidden');
            progressFill.style.width = '0';
        }
    },
    
    renderLots(lots) {
        const grid = document.getElementById('lots-list');
        
        if (!lots || lots.length === 0) {
            grid.innerHTML = '<p class="lots-empty-text">Нет объектов</p>';
            return;
        }
        
        grid.innerHTML = lots.map(lot => `
            <div class="lot-card" data-id="${lot.id}">
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
        if (!this.currentCollectionId) {
            alert('Сначала сохраните подборку');
            return;
        }
        
        try {
            const result = await API.post(`/collections/${this.currentCollectionId}/publish`);
            
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
    
    // URL инпуты
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
    
    async removeLotFromCollection(lotId) {
        if (!confirm('Удалить лот из подборки?')) return;
        
        try {
            await API.delete(`/collections/${this.currentCollectionId}/lots/${lotId}`);
            
            // Обновляем локальный список
            this.currentLots = this.currentLots.filter(l => l.id !== lotId);
            
            if (this.currentLots.length > 0) {
                this.renderLots(this.currentLots);
            } else {
                document.getElementById('existing-lots-section').classList.add('hidden');
            }
            
            await this.loadCollections();
        } catch (e) {
            alert('Ошибка удаления: ' + e.message);
        }
    },
    
    async openLotCalculator(lot) {
        // Заполняем данные
        document.getElementById('lot-image').src = lot.layout_image_url || 'img/placeholder.png';
        document.getElementById('lot-address').textContent = lot.address;
        document.getElementById('lot-price').textContent = this.formatPrice(
            lot.discounted_price || lot.original_price
        );
        document.getElementById('lot-area').textContent = lot.area;
        
        // Загружаем отчёты
        try {
            const reports = await API.get('/reports');
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
            const result = await API.post(`/calc/from-lot/${lotId}`, data);
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
