// Аутентификация
const Auth = {
    user: null,
    
    init: async () => {
        await Auth.checkAuthStatus();
        Auth.setupLogout();
    },
    
    checkAuthStatus: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            Auth.user = null;
            Auth.showGuestMenu();
            return;
        }
        
        try {
            const user = await API.getMe();
            Auth.user = user;
            Auth.showAuthenticatedMenu(user);
        } catch (error) {
            console.error('Ошибка проверки авторизации:', error);
            localStorage.removeItem('access_token');
            Auth.user = null;
            Auth.showGuestMenu();
        }
    },
    
    showGuestMenu: () => {
        const navLogin = document.getElementById('nav-login');
        const navRegister = document.getElementById('nav-register');
        const navProfile = document.getElementById('nav-profile');
        const navLogout = document.getElementById('nav-logout');
        const navCollections = document.getElementById('nav-collections');
        const navAdmin = document.getElementById('nav-admin');
        
        if (navLogin && navLogin.parentElement) {
            const parent = navLogin.parentElement;
            parent.classList.remove('hidden');
            parent.style.display = 'list-item'; // Явно устанавливаем display для li
        }
        if (navRegister && navRegister.parentElement) {
            const parent = navRegister.parentElement;
            parent.classList.remove('hidden');
            parent.style.display = 'list-item';
        }
        if (navProfile && navProfile.parentElement) {
            const parent = navProfile.parentElement;
            parent.classList.add('hidden');
            parent.style.display = 'none';
        }
        if (navLogout && navLogout.parentElement) {
            const parent = navLogout.parentElement;
            parent.classList.add('hidden');
            parent.style.display = 'none';
        }
        if (navCollections && navCollections.parentElement) {
            const parent = navCollections.parentElement;
            parent.classList.add('hidden');
            parent.style.display = 'none';
        }
        if (navAdmin) {
            navAdmin.classList.add('hidden');
            navAdmin.style.display = 'none';
        }
    },
    
    showAuthenticatedMenu: (user) => {
        console.log('showAuthenticatedMenu called with user:', user);
        console.log('Subscription:', user.subscription);
        
        const navLogin = document.getElementById('nav-login');
        const navRegister = document.getElementById('nav-register');
        const navProfile = document.getElementById('nav-profile');
        const navLogout = document.getElementById('nav-logout');
        const navCollections = document.getElementById('nav-collections');
        const navAdmin = document.getElementById('nav-admin');
        
        if (navLogin && navLogin.parentElement) {
            const parent = navLogin.parentElement;
            parent.classList.add('hidden');
            parent.style.display = 'none';
        }
        if (navRegister && navRegister.parentElement) {
            const parent = navRegister.parentElement;
            parent.classList.add('hidden');
            parent.style.display = 'none';
        }
        if (navProfile && navProfile.parentElement) {
            const parent = navProfile.parentElement;
            parent.classList.remove('hidden');
            parent.style.display = 'list-item'; // Явно устанавливаем display для li
        }
        if (navLogout && navLogout.parentElement) {
            const parent = navLogout.parentElement;
            parent.classList.remove('hidden');
            parent.style.display = 'list-item';
        }
        
        // Admin link
        if (navAdmin) {
            if (user.role === 'admin') {
                navAdmin.classList.remove('hidden');
                navAdmin.style.display = 'list-item';
            } else {
                navAdmin.classList.add('hidden');
                navAdmin.style.display = 'none';
            }
        }
        
        // Проверяем платную подписку (agent или developer)
        const hasPaidSubscription = user.subscription && 
            user.subscription.status === 'active' && 
            (user.subscription.plan === 'agent' || user.subscription.plan === 'developer');
        
        if (hasPaidSubscription) {
            if (navCollections && navCollections.parentElement) {
                const parent = navCollections.parentElement;
                parent.classList.remove('hidden');
                parent.style.display = 'list-item';
            }
            // Разблокировать поле Циан
            const cianInput = document.getElementById('cian-url');
            if (cianInput) {
                cianInput.disabled = false;
                cianInput.removeAttribute('disabled');
                const wrapper = cianInput.closest('.cian-input-wrapper');
                if (wrapper) {
                    wrapper.classList.remove('disabled');
                    wrapper.style.opacity = '1';
                }
            }
            // Убираем подсказку "только по подписке"
            const infoIcon = document.querySelector('.cian-input-wrapper .info-icon');
            if (infoIcon) {
                infoIcon.style.display = 'none';
            }
        } else {
            if (navCollections && navCollections.parentElement) {
                const parent = navCollections.parentElement;
                parent.classList.add('hidden');
                parent.style.display = 'none';
            }
        }
        
        const profileLink = document.getElementById('nav-profile');
        if (profileLink) {
            profileLink.textContent = user.email || 'Профиль';
        }
    },
    
    logout: () => {
        localStorage.removeItem('access_token');
        window.location.reload();
    },

    setupLogout: () => {
        const logoutLink = document.getElementById('nav-logout');
        if (logoutLink) {
            logoutLink.addEventListener('click', (e) => {
                e.preventDefault();
                Auth.logout();
            });
        }
    }
};

// Инициализация будет вызвана из основного скрипта после загрузки DOM
