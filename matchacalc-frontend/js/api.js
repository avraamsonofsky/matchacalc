// API клиент
const API = {
    baseURL: '/api/v1',

    _httpError(status, body) {
        if (AppDebug.enabled) {
            return `HTTP ${status}: ${body}`;
        }
        if (status === 401) return 'Требуется вход';
        if (status === 403) return 'Недостаточно прав';
        if (status === 429) return 'Слишком много запросов. Подождите немного';
        return 'Запрос не выполнен. Попробуйте позже';
    },

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        AppDebug.log(`API запрос: ${url}`);
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, config);
            AppDebug.log(`API ответ: ${response.status} ${response.statusText}`);

            if (!response.ok) {
                const errorText = await response.text();
                AppDebug.error('Ошибка API:', response.status, errorText);
                throw new Error(this._httpError(response.status, errorText));
            }

            const data = await response.json();
            AppDebug.log('API данные:', data);
            return data;
        } catch (error) {
            AppDebug.error('API Error:', error);
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Не удалось подключиться к серверу. Проверьте подключение к интернету.');
            }
            throw error;
        }
    },

    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined
        });
    },

    async delete(endpoint) {
        const url = `${this.baseURL}${endpoint}`;
        const token = localStorage.getItem('access_token');
        const response = await fetch(url, {
            method: 'DELETE',
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(this._httpError(response.status, errorText));
        }
        return response.status === 204 ? null : response.json();
    },

    async getLocationGroups() {
        return this.get('/reports/location-groups');
    },

    async getScenarios() {
        return this.get('/reports/scenarios');
    },

    async getReports() {
        return this.get('/reports/');
    },

    async calculate(data) {
        return this.post('/calc/preview', data);
    },

    async register(email, password) {
        return this.post('/auth/register', { email, password });
    },

    async login(email, password) {
        return this.post('/auth/login', { email, password });
    },

    async getMe() {
        return this.get('/auth/me');
    },

    async uploadFile(formData) {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${this.baseURL}/lots/upload-image`, {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(this._httpError(response.status, errorText));
        }
        return response.json();
    }
};
