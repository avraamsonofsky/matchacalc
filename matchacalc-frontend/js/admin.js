// Admin Panel Logic

const Admin = {
    reports: [],

    async init() {
        if (!Auth.user || Auth.user.role !== 'admin') {
            window.location.href = 'login.html';
            return;
        }

        document.getElementById('nav-logout').addEventListener('click', (e) => {
            e.preventDefault();
            Auth.logout();
        });

        await this.loadReports();
        await this.loadScenarios();
        await this.loadValuesMatrix();
    },

    async loadReports() {
        try {
            const reports = await API.get('/admin/reports');
            this.reports = reports;
            this.renderReports(reports);
        } catch (error) {
            this.showError('Не удалось загрузить отчёты: ' + error.message);
        }
    },

    renderReports(reports) {
        const tbody = document.querySelector('#reports-table tbody');
        tbody.innerHTML = '';

        reports.forEach(report => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-report-id', report.id);
            const esc = s => String(s || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            tr.innerHTML = `
                <td>${report.id}</td>
                <td><input type="text" data-field="provider" value="${esc(report.provider)}"></td>
                <td><input type="text" data-field="title" value="${esc(report.title)}"></td>
                <td><input type="text" data-field="period" value="${esc(report.period)}"></td>
                <td>
                    <select data-field="active">
                        <option value="true" ${report.active ? 'selected' : ''}>Активен</option>
                        <option value="false" ${!report.active ? 'selected' : ''}>Неактивен</option>
                    </select>
                </td>
                <td><button type="button" class="action-btn save-row-btn" onclick="Admin.saveReportRow(${report.id})">Сохранить</button></td>
            `;
            tbody.appendChild(tr);
        });
    },

    async saveReportRow(reportId) {
        const tr = document.querySelector(`#reports-table tbody tr[data-report-id="${reportId}"]`);
        if (!tr) return;
        const provider = tr.querySelector('[data-field="provider"]').value;
        const title = tr.querySelector('[data-field="title"]').value;
        const period = tr.querySelector('[data-field="period"]').value;
        const active = tr.querySelector('[data-field="active"]').value === 'true';
        try {
            await API.put(`/admin/reports/${reportId}`, { provider, title, period, active });
            this.showStatus('Отчёт обновлён');
        } catch (error) {
            this.showError('Ошибка: ' + error.message);
        }
    },

    async loadValuesMatrix() {
        if (!this.reports || this.reports.length === 0) return;
        try {
            const valuesPerReport = await Promise.all(
                this.reports.map(r => API.get(`/admin/reports/${r.id}/values`))
            );
            this.renderValuesMatrix(this.reports, valuesPerReport);
        } catch (error) {
            this.showError('Не удалось загрузить коэффициенты: ' + error.message);
        }
    },

    renderValuesMatrix(reports, valuesPerReport) {
        const rowKeys = new Set();
        valuesPerReport.forEach(values => {
            values.forEach(v => rowKeys.add(`${v.location_group_id}|${v.property_class}`));
        });
        const rows = Array.from(rowKeys).sort();

        const thead = document.getElementById('values-matrix-thead');
        const esc = s => String(s || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        thead.innerHTML = '<tr><th>Район / Класс</th>' + reports.map(r =>
            `<th><input type="text" class="report-title-in-matrix" data-report-id="${r.id}" value="${esc(r.title)}" placeholder="Название"><button type="button" class="action-btn save-cell-btn" onclick="Admin.saveReportTitleFromBtn(this)">Сохранить</button></th>`
        ).join('') + '<th></th></tr>';

        const tbody = document.getElementById('values-matrix-tbody');
        tbody.innerHTML = '';

        const valueByKey = (reportIndex) => {
            const vals = valuesPerReport[reportIndex] || [];
            return (loc, cl) => vals.find(v => v.location_group_id === loc && v.property_class === cl);
        };

        rows.forEach(rowKey => {
            const [loc, cl] = rowKey.split('|');
            const tr = document.createElement('tr');
            let cellsHtml = `<td><strong>${loc}</strong> / ${cl}</td>`;
            reports.forEach((report, reportIndex) => {
                const val = valueByKey(reportIndex)(loc, cl);
                if (!val) {
                    cellsHtml += '<td class="values-cell">—</td>';
                    return;
                }
                const r = val.rent_start ?? '';
                const rg = val.rent_growth_annual ?? '';
                const p = val.price_per_m2_start ?? '';
                const pg = val.price_growth_annual ?? '';
                const vac = val.vacancy_rate ?? '';
                cellsHtml += `
                    <td class="values-cell" data-value-id="${val.id}">
                        <div>Ар: <input type="number" step="1" data-v="rent_start" value="${r}"></div>
                        <div>Рост ар: <input type="number" step="0.01" data-v="rent_growth_annual" value="${rg}"></div>
                        <div>Цена: <input type="number" step="1" data-v="price_per_m2_start" value="${p}"></div>
                        <div>Рост ц: <input type="number" step="0.01" data-v="price_growth_annual" value="${pg}"></div>
                        <div>Вакан: <input type="number" step="0.01" data-v="vacancy_rate" value="${vac}"></div>
                        <button type="button" class="action-btn save-cell-btn" onclick="Admin.saveValueCell(${val.id})">Сохранить</button>
                    </td>
                `;
            });
            cellsHtml += '<td></td>';
            tr.innerHTML = cellsHtml;
            tbody.appendChild(tr);
        });
    },

    saveReportTitleFromBtn(btn) {
        const input = btn.previousElementSibling;
        const reportId = parseInt(input.dataset.reportId, 10);
        this.saveReportTitle(reportId, input.value);
    },
    async saveReportTitle(reportId, title) {
        try {
            await API.put(`/admin/reports/${reportId}`, { title });
            this.showStatus('Название обновлено');
        } catch (e) {
            this.showError('Ошибка: ' + e.message);
        }
    },

    async saveValueCell(valueId) {
        const cell = document.querySelector(`#values-matrix-tbody [data-value-id="${valueId}"]`);
        if (!cell) return;
        const rent_start = cell.querySelector('[data-v="rent_start"]').value;
        const rent_growth_annual = cell.querySelector('[data-v="rent_growth_annual"]').value;
        const price_per_m2_start = cell.querySelector('[data-v="price_per_m2_start"]').value;
        const price_growth_annual = cell.querySelector('[data-v="price_growth_annual"]').value;
        const vacancy_rate = cell.querySelector('[data-v="vacancy_rate"]').value;
        const payload = {
            rent_start: rent_start === '' ? null : Number(rent_start),
            rent_growth_annual: rent_growth_annual === '' ? null : Number(rent_growth_annual),
            price_per_m2_start: price_per_m2_start === '' ? null : Number(price_per_m2_start),
            price_growth_annual: price_growth_annual === '' ? null : Number(price_growth_annual),
            vacancy_rate: vacancy_rate === '' ? null : Number(vacancy_rate)
        };
        try {
            await API.put(`/admin/report-values/${valueId}`, payload);
            this.showStatus('Значение сохранено');
        } catch (error) {
            this.showError('Ошибка: ' + error.message);
        }
    },

    async loadScenarios() {
        try {
            const scenarios = await API.get('/reports/scenarios');
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
            tr.setAttribute('data-scenario-id', scenario.id);
            const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            const adj = scenario.discount_rate_adjustment != null ? scenario.discount_rate_adjustment : '';
            const idAttr = String(scenario.id).replace(/"/g, '&quot;');
            tr.innerHTML = `
                <td>${idAttr}</td>
                <td><input type="text" data-field="name" value="${esc(scenario.name)}"></td>
                <td><input type="number" step="0.01" data-field="rent_growth_multiplier" value="${scenario.rent_growth_multiplier ?? ''}"></td>
                <td><input type="number" step="0.01" data-field="price_growth_multiplier" value="${scenario.price_growth_multiplier ?? ''}"></td>
                <td><input type="number" step="0.01" data-field="discount_rate_adjustment" value="${adj}"></td>
                <td><button type="button" class="action-btn save-row-btn" onclick="Admin.saveScenarioRowFromBtn(this)">Сохранить</button></td>
            `;
            tbody.appendChild(tr);
        });
    },

    saveScenarioRowFromBtn(btn) {
        const tr = btn.closest('tr');
        const scenarioId = tr?.getAttribute('data-scenario-id');
        if (scenarioId) this.saveScenarioRow(scenarioId);
    },
    async saveScenarioRow(scenarioId) {
        const tr = document.querySelector(`#scenarios-table tbody tr[data-scenario-id="${scenarioId}"]`);
        if (!tr) return;
        const name = tr.querySelector('[data-field="name"]').value;
        const rent = tr.querySelector('[data-field="rent_growth_multiplier"]').value;
        const price = tr.querySelector('[data-field="price_growth_multiplier"]').value;
        const adj = tr.querySelector('[data-field="discount_rate_adjustment"]').value;
        const payload = {
            name,
            rent_growth_multiplier: rent === '' ? null : Number(rent),
            price_growth_multiplier: price === '' ? null : Number(price),
            discount_rate_adjustment: adj === '' ? null : Number(adj)
        };
        try {
            await API.put(`/admin/scenarios/${scenarioId}`, payload);
            this.showStatus('Сценарий обновлён');
        } catch (error) {
            this.showError('Ошибка: ' + error.message);
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

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.getElementById(`tab-${tabName}`).classList.remove('hidden');
    document.querySelectorAll('.admin-nav button').forEach(el => el.classList.remove('active'));
    const buttons = document.querySelectorAll('.admin-nav button');
    if (tabName === 'reports') buttons[0].classList.add('active');
    if (tabName === 'values') buttons[1].classList.add('active');
    if (tabName === 'scenarios') buttons[2].classList.add('active');
}

document.addEventListener('DOMContentLoaded', async () => {
    await Auth.init();
    Admin.init();
});
