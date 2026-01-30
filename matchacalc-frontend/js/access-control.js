// Управление доступом и ограничениями
const AccessControl = {
    user: null,
    subscription: null,
    calculateCount: 0,
    lastCalculateTime: null,
    calculateLimit: 3, // 3 нажатия подряд
    calculateCooldown: 180000, // 3 минуты в миллисекундах
    
    async init() {
        // Используем данные из Auth, если они уже загружены
        if (Auth && Auth.user) {
            this.user = Auth.user;
            this.subscription = Auth.user.subscription || null;
        } else {
            await this.loadUser();
        }
        
        // Если есть подписка — сбрасываем все ограничения и скрываем модалку
        if (this.hasActiveSubscription()) {
            this.calculateCount = 0;
            this.lastCalculateTime = null;
            this.hideSubscriptionModal();
        }
    },
    
    async loadUser() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            this.user = null;
            this.subscription = null;
            return;
        }
        
        try {
            const userData = await API.getMe();
            this.user = userData;
            this.subscription = userData.subscription || null;
            
            // Синхронизируем с Auth
            if (Auth) {
                Auth.user = userData;
            }
        } catch (error) {
            console.error('Ошибка загрузки пользователя:', error);
            localStorage.removeItem('access_token');
            this.user = null;
            this.subscription = null;
            if (Auth) {
                Auth.user = null;
            }
        }
    },
    
    hasActiveSubscription() {
        return this.subscription && 
               this.subscription.status === 'ACTIVE' && 
               (this.subscription.plan === 'AGENT' || this.subscription.plan === 'DEVELOPER');
    },
    
    canCalculate() {
        // С подпиской - можно рассчитывать каждые 10 секунд
        if (this.hasActiveSubscription()) {
            const now = Date.now();
            const lastCalculate = this.lastCalculateTime || 0;
            return (now - lastCalculate) >= 10000; // 10 секунд
        }
        
        // Без подписки - 3 нажатия подряд, потом 3 минуты
        if (this.calculateCount < this.calculateLimit) {
            return true;
        }
        
        const now = Date.now();
        const lastCalculate = this.lastCalculateTime || 0;
        return (now - lastCalculate) >= this.calculateCooldown;
    },
    
    recordCalculate() {
        this.lastCalculateTime = Date.now();
        
        // С подпиской — никаких ограничений, кроме 10 сек между расчётами
        if (this.hasActiveSubscription()) {
            return; // Ничего не делаем, модалку не показываем
        }
        
        // Без подписки - увеличиваем счётчик
        this.calculateCount++;
        
        // Если достигли лимита, показываем модалку
        if (this.calculateCount >= this.calculateLimit) {
            this.showSubscriptionModal();
        }
    },
    
    resetCalculateCount() {
        // Сбрасываем счётчик, если прошло достаточно времени
        if (this.lastCalculateTime) {
            const now = Date.now();
            if (now - this.lastCalculateTime >= this.calculateCooldown) {
                this.calculateCount = 0;
                this.lastCalculateTime = null;
            }
        }
    },
    
    showSubscriptionModal() {
        const modal = document.getElementById('subscription-limit-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    },
    
    hideSubscriptionModal() {
        const modal = document.getElementById('subscription-limit-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    },
    
    canUseCian() {
        return this.hasActiveSubscription();
    }
};
