# Инструкция по настройке CI/CD

## 1. Настройка GitHub Secrets

Перейди в настройки репозитория: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Добавь следующие секреты:

### Обязательные секреты:

- **`VPS_HOST`** - IP адрес или домен VPS (например: `91.201.53.228`)
- **`VPS_USER`** - пользователь для SSH (обычно `root`)
- **`VPS_SSH_KEY`** - приватный SSH ключ для подключения к серверу
- **`VPS_SSH_PORT`** - порт SSH (обычно `22`, можно не указывать)

### Секреты для подключения к БД и Redis:

- **`STAGING_DATABASE_URL`** - строка подключения к БД для staging (например: `postgresql://user:pass@host:5432/dbname`)
- **`STAGING_REDIS_URL`** - строка подключения к Redis для staging (например: `redis://host:6379`)
- **`PROD_DATABASE_URL`** - строка подключения к БД для production
- **`PROD_REDIS_URL`** - строка подключения к Redis для production

### Секреты для JWT:

- **`JWT_SECRET`** - секретный ключ для JWT токенов (должен быть одинаковым для staging и prod, или создать отдельные)

## 2. Получение SSH ключа

Если у тебя уже есть SSH ключ на локальной машине:

```bash
cat ~/.ssh/id_rsa
# или
cat ~/.ssh/id_ed25519
```

Скопируй весь вывод (включая `-----BEGIN ... KEY-----` и `-----END ... KEY-----`) и вставь в секрет `VPS_SSH_KEY`.

Если ключа нет, создай новый:

```bash
ssh-keygen -t ed25519 -C "github-actions"
```

Затем добавь публичный ключ на сервер:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@91.201.53.228
```

И скопируй приватный ключ в GitHub Secrets.

## 3. Проверка работы

После настройки секретов:

1. Создай ветку `staging` (если её нет):
   ```bash
   git checkout -b staging
   git push origin staging
   ```

2. Сделай любой коммит в ветку `staging`:
   ```bash
   git commit --allow-empty -m "Test staging deploy"
   git push origin staging
   ```

3. Проверь GitHub Actions: `Actions` → должен запуститься workflow `Deploy to Staging`

4. После успешного деплоя проверь:
   - **Staging (отдельный фронт + бэк):** фронт в `/var/www/staging`, бэк на порту 8080 из `/root/matchacalc-backend-staging`. Доступ: `http://91.201.53.228:8080` (бэк) или через Nginx по поддомену.
   - **Production:** фронт в `/var/www/lattecalc`, бэк на порту 3000 из `/root/matchacalc-backend`. Доступ: `http://91.201.53.228:3000` (бэк) или основной домен.

## 4. Разделение Staging и Production

- **Staging** (ветка `staging`): деплой только в стагинг-каталоги; прод не трогается.
  - Бэкенд: `/root/matchacalc-backend-staging`, порт **8080**.
  - Фронтенд: `/var/www/staging`.
- **Production** (ветка `main`): деплой только в прод-каталоги; стагинг не трогается.
  - Бэкенд: `/root/matchacalc-backend`, порт **3000**.
  - Фронтенд: `/var/www/lattecalc`.

Один фронт привязан к одному бэку: стагинг-фронт ходит в стагинг-бэк (через Nginx или порт 8080), прод-фронт — в прод-бэк (через Nginx или порт 3000).

## 5. Настройка Nginx (опционально)

Если хочешь использовать домены вместо IP:порт, настрой Nginx на сервере:

```nginx
# /etc/nginx/sites-available/staging.commercial-invest.ru (стагинг: свой фронт + свой бэк)
server {
    listen 80;
    server_name staging.commercial-invest.ru;
    root /var/www/staging;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# /etc/nginx/sites-available/commercial-invest.ru (прод)
server {
    listen 80;
    server_name commercial-invest.ru;
    root /var/www/lattecalc;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Пример со старым именем (если нужно):

```nginx
# /etc/nginx/sites-available/staging.matchacalc.ru
server {
    listen 80;
    server_name staging.matchacalc.ru;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# /etc/nginx/sites-available/commercial-invest.ru
server {
    listen 80;
    server_name commercial-invest.ru;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 5. Структура деплоя

- **Staging** (ветка `staging`) → порт `8080` → контейнер `matchacalc-staging`
- **Production** (ветка `main`) → порт `3000` → контейнер `matchacalc-prod`

Оба контейнера работают параллельно на разных портах.
