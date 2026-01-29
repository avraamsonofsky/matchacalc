// API клиент
const API = {
    baseURL: '/api/v1',
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        console.log(`API запрос: ${url}`);
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        // Добавляем токен, если есть
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(url, config);
            console.log(`API ответ: ${response.status} ${response.statusText}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Ошибка API:', response.status, errorText);
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            console.log('API данные:', data);
            return data;
        } catch (error) {
            console.error('API Error:', error);
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
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        // DELETE обычно возвращает 204 No Content
        return response.status === 204 ? null : response.json();
    },

    // Получить список районов
    async getLocationGroups() {
        return this.get('/reports/location-groups');
    },
    
    // Получить список сценариев
    async getScenarios() {
        return this.get('/reports/scenarios');
    },
    
    // Получить список отчётов
    async getReports() {
        return this.get('/reports');
    },
    
    // Расчёт калькулятора
    async calculate(data) {
        return this.post('/calc/preview', data);
    },
    
    // Авторизация
    async register(email, password) {
        return this.post('/auth/register', { email, password });
    },
    
    async login(email, password) {
        return this.post('/auth/login', { email, password });
    },
    
    async getMe() {
        return this.get('/auth/me');
    }
};
