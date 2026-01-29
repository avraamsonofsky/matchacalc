# Стагинг на поддомене staging.commercial-invest.ru

Пошаговая настройка стагинга на поддомене.

---

## Шаг 1. DNS (у регистратора/хостинга)

1. Зайди в панель управления доменом **commercial-invest.ru** (NetAngels или где куплен домен).
2. Добавь **A-запись** для поддомена:
   - **Тип:** A  
   - **Имя/хост:** `staging` (или `staging.commercial-invest` — зависит от панели)  
   - **Значение/IP:** `91.201.53.228` (IP твоего VPS)  
   - **TTL:** по умолчанию (300–3600)
3. Сохрани. Подожди 5–15 минут (иногда до часа), пока DNS обновится.

Проверка (на своём компьютере):
```bash
# Должен вернуть IP 91.201.53.228
nslookup staging.commercial-invest.ru
```

---

## Шаг 2. Подключение к VPS

```bash
ssh root@91.201.53.228
```

---

## Шаг 3. Проверить, где лежит фронт стагинга

На VPS выполни:

```bash
ls -la /var/www/staging/
```

- Если видишь **index.html**, **css/**, **js/** прямо в `/var/www/staging/` — в конфиге Nginx используй `root /var/www/staging;`.
- Если видишь только папку **matchacalc-frontend/** — значит, scp создал вложенную структуру. Тогда в конфиге используй `root /var/www/staging/matchacalc-frontend;`.

---

## Шаг 4. Установить Nginx (если ещё не установлен)

```bash
apt update
apt install nginx -y
```

---

## Шаг 5. Создать конфиг для стагинга

```bash
nano /etc/nginx/sites-available/staging.commercial-invest.ru
```

Вставь содержимое из файла **nginx-staging.conf.example** в репозитории. Важно:

- Строка `root` — как в шаге 3: либо `/var/www/staging`, либо `/var/www/staging/matchacalc-frontend`.
- Остальное можно не менять (порт 8080 для API уже указан).

Пример готового блока (если фронт в `/var/www/staging/matchacalc-frontend`):

```nginx
server {
    listen 80;
    server_name staging.commercial-invest.ru;
    root /var/www/staging/matchacalc-frontend;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Сохрани файл (в nano: Ctrl+O, Enter, Ctrl+X).

---

## Шаг 6. Включить сайт и перезагрузить Nginx

```bash
ln -s /etc/nginx/sites-available/staging.commercial-invest.ru /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

Если `nginx -t` выдал ошибку — исправь конфиг и повтори.

---

## Шаг 7. Проверка

1. В браузере открой: **http://staging.commercial-invest.ru**
2. Должна открыться стагинг-версия сайта (фронт + запросы к API на порт 8080).

---

## Если стагинг не открывается

- Проверь DNS: `nslookup staging.commercial-invest.ru` → должен быть 91.201.53.228.
- На VPS: `curl -I http://127.0.0.1:8080/api/v1/health` — бэкенд стагинга должен ответить 200.
- Логи Nginx: `tail -20 /var/log/nginx/error.log`

---

## HTTPS (опционально)

Когда стагинг по HTTP заработает, можно выдать сертификат:

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d staging.commercial-invest.ru
```

Следуй подсказкам certbot. После этого стагинг будет доступен по **https://staging.commercial-invest.ru**.
