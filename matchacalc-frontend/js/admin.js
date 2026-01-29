// Admin Panel Logic

const Admin = {
    async init() {
        if (!Auth.user || Auth.user.role !== 'admin') {
            window.location.href = 'login.html';
            return;
        }

        // Setup logout
        document.getElementById('nav-logout').addEventListener('click', (e) => {
            e.preventDefault();
            Auth.logout();
        });

        // Форма создания отчёта
        document.getElementById('form-new-report').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitNewReport();
        });

        await this.loadReports();
        await this.loadScenarios();
    },

    openNewReportModal() {
        document.getElementById('modal-new-report').classList.remove('hidden');
        document.getElementById('new-report-provider').value = '';
        document.getElementById('new-report-title').value = '';
        document.getElementById('new-report-period').value = '';
        document.getElementById('new-report-active').checked = true;
    },

    closeNewReportModal() {
        document.getElementById('modal-new-report').classList.add('hidden');
    },

    async submitNewReport() {
        const provider = document.getElementById('new-report-provider').value.trim();
        const title = document.getElementById('new-report-title').value.trim();
        const period = document.getElementById('new-report-period').value.trim();
        const active = document.getElementById('new-report-active').checked;
        if (!provider || !title || !period) {
            this.showError('Заполните провайдера, название и период');
            return;
        }
        try {
            await API.post('/admin/reports', { provider, title, period, active });
            this.showStatus('Отчёт создан');
            this.closeNewReportModal();
            await this.loadReports();
        } catch (error) {
            this.showError('Ошибка создания отчёта: ' + error.message);
        }
    },

    async loadReports() {
        try {
            const reports = await API.get('/admin/reports');
            this.renderReports(reports);
            this.populateReportSelector(reports);
        } catch (error) {
            this.showError('Не удалось загрузить отчёты: ' + error.message);
        }
    },

    renderReports(reports) {
        const tbody = document.querySelector('#reports-table tbody');
        tbody.innerHTML = '';
        
        reports.forEach(report => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${report.id}</td>
                <td><input type="text" value="${report.provider}" onchange="Admin.updateReport(${report.id}, 'provider', this.value)"></td>
                <td><input type="text" value="${report.title}" onchange="Admin.updateReport(${report.id}, 'title', this.value)"></td>
                <td><input type="text" value="${report.period}" onchange="Admin.updateReport(${report.id}, 'period', this.value)"></td>
                <td>
                    <select onchange="Admin.updateReport(${report.id}, 'active', this.value === 'true')">
                        <option value="true" ${report.active ? 'selected' : ''}>Активен</option>
                        <option value="false" ${!report.active ? 'selected' : ''}>Неактивен</option>
                    </select>
                </td>
                <td>
                    <button class="action-btn" onclick="Admin.loadValuesForReport(${report.id}, '${report.title}')">Значения</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    },

    populateReportSelector(reports) {
        const select = document.getElementById('report-selector');
        select.innerHTML = '<option value="">Выберите отчёт для просмотра деталей...</option>';
        reports.forEach(report => {
            const option = document.createElement('option');
            option.value = report.id;
            option.textContent = `${report.title} (${report.period})`;
            select.appendChild(option);
        });
    },

    async updateReport(id, field, value) {
        try {
            await API.put(`/admin/reports/${id}`, { [field]: value });
            this.showStatus('Отчёт обновлен');
        } catch (error) {
            this.showError('Ошибка обновления: ' + error.message);
        }
    },

    async loadValuesForReport(reportId, reportTitle) {
        if (!reportId) return;
        
        if (reportTitle) {
            document.getElementById('current-report-name').textContent = reportTitle;
            // Update selector if called from button
            document.getElementById('report-selector').value = reportId;
        }

        switchTab('values');

        try {
            const values = await API.get(`/admin/reports/${reportId}/values`);
            this.renderValues(values);
        } catch (error) {
            this.showError('Не удалось загрузить значения: ' + error.message);
        }
    },

    renderValues(values) {
        const tbody = document.querySelector('#values-table tbody');
        tbody.innerHTML = '';
        
        values.forEach(val => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${val.location_group_id}</td>
                <td>${val.property_class}</td>
                <td><input type="number" step="1" value="${val.rent_start}" onchange="Admin.updateValue(${val.id}, 'rent_start', this.value)"></td>
                <td><input type="number" step="0.01" value="${val.rent_growth_annual}" onchange="Admin.updateValue(${val.id}, 'rent_growth_annual', this.value)"></td>
                <td><input type="number" step="1" value="${val.price_per_m2_start || ''}" onchange="Admin.updateValue(${val.id}, 'price_per_m2_start', this.value)"></td>
                <td><input type="number" step="0.01" value="${val.price_growth_annual}" onchange="Admin.updateValue(${val.id}, 'price_growth_annual', this.value)"></td>
                <td><input type="number" step="0.01" value="${val.vacancy_rate || ''}" onchange="Admin.updateValue(${val.id}, 'vacancy_rate', this.value)"></td>
                <td>Saved</td>
            `;
            tbody.appendChild(tr);
        });
    },

    async updateValue(id, field, value) {
        try {
            // Convert empty string to null for optional fields
            const payload = { [field]: value === '' ? null : Number(value) };
            await API.put(`/admin/report-values/${id}`, payload);
            this.showStatus('Значение сохранено');
        } catch (error) {
            this.showError('Ошибка сохранения: ' + error.message);
        }
    },

    async loadScenarios() {
        try {
            const scenarios = await API.get('/reports/scenarios'); // Public endpoint is fine for reading
            this.renderScenarios(scenarios);
        } catch (error) {
            this.showError('Не удалось загрузить сценарии: ' + error.message);
        }
    },

    renderScenarios(scenarios) {
        const tbody = document.querySelector('#scenarios-table tbody');
        tbody.innerHTML = '';
        
        scenarios.forEach(scenario => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${scenario.id}</td>
                <td><input type="text" value="${scenario.name}" onchange="Admin.updateScenario('${scenario.id}', 'name', this.value)"></td>
                <td><input type="number" step="0.01" value="${scenario.rent_growth_multiplier}" onchange="Admin.updateScenario('${scenario.id}', 'rent_growth_multiplier', this.value)"></td>
                <td><input type="number" step="0.01" value="${scenario.price_growth_multiplier}" onchange="Admin.updateScenario('${scenario.id}', 'price_growth_multiplier', this.value)"></td>
                <td><input type="number" step="0.01" value="${scenario.discount_rate_adjustment || 0}" onchange="Admin.updateScenario('${scenario.id}', 'discount_rate_adjustment', this.value)"></td>
                <td>Saved</td>
            `;
            tbody.appendChild(tr);
        });
    },

    async updateScenario(id, field, value) {
        try {
            const payload = { [field]: field === 'name' ? value : Number(value) };
            await API.put(`/admin/scenarios/${id}`, payload);
            this.showStatus('Сценарий обновлен');
        } catch (error) {
            this.showError('Ошибка обновления сценария: ' + error.message);
        }
    },

    showError(msg) {
        const el = document.getElementById('error-message');
        el.textContent = msg;
        el.style.display = 'block';
        setTimeout(() => el.style.display = 'none', 5000);
    },

    showStatus(msg) {
        const el = document.getElementById('status-message');
        el.textContent = msg;
        el.style.color = 'green';
        setTimeout(() => el.textContent = '', 2000);
    }
};

// Global helpers
window.loadReportValues = (id) => Admin.loadValuesForReport(id);
window.createNewReport = () => Admin.openNewReportModal();

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.getElementById(`tab-${tabName}`).classList.remove('hidden');
    
    document.querySelectorAll('.admin-nav button').forEach(el => el.classList.remove('active'));
    // Simple way to highlight active tab button based on order/index or just trust the user clicked it
    // For now, let's just make the clicked button active if passed event, or finding by text
    const buttons = document.querySelectorAll('.admin-nav button');
    if (tabName === 'reports') buttons[0].classList.add('active');
    if (tabName === 'values') buttons[1].classList.add('active');
    if (tabName === 'scenarios') buttons[2].classList.add('active');
}

// Init: сначала восстанавливаем сессию из токена, потом проверяем роль
document.addEventListener('DOMContentLoaded', async () => {
    await Auth.init();
    Admin.init();
});
