# Инструкция по исправлению проблемы с bcrypt (ограничение 72 байта)

## Проблема
bcrypt имеет ограничение: пароль не может быть длиннее 72 байт. При попытке хешировать или проверять пароль длиннее 72 байт возникает ошибка.

## Решение

### 1. Исправление в `app/auth/service.py`

Функции `get_password_hash` и `verify_password` теперь автоматически обрезают пароль до 72 байт перед обработкой:

```python
def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    # bcrypt ограничен 72 байтами, обрезаем если нужно
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return pwd_context.hash(password_bytes.decode('utf-8', errors='ignore'))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    # bcrypt ограничен 72 байтами, обрезаем если нужно
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return pwd_context.verify(password_bytes.decode('utf-8', errors='ignore'), hashed_password)
```

### 2. Исправление в скрипте создания пользователя

Скрипт `scripts/create_test_user.py` также обновлён для обработки длинных паролей.

### 3. Перезапуск бэкенда

После внесения изменений необходимо перезапустить бэкенд:

```bash
# Остановить текущий процесс (если запущен)
pkill -f "uvicorn.*main:app" || true

# Запустить бэкенд заново
cd matchacalc-backend
source .venv/bin/activate  # если используется venv
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Проверка работы

После перезапуска попробуйте войти с тестовыми данными:
- Email: `premium@test.com`
- Пароль: `premium123`

## Дополнительные замечания

- Пароли длиннее 72 байт будут обрезаны, что может привести к коллизиям (два разных длинных пароля могут стать одинаковыми после обрезки)
- Рекомендуется ограничить максимальную длину пароля на уровне фронтенда (например, 64 символа)
- Для паролей длиннее 72 байт лучше использовать другой алгоритм хеширования (например, Argon2)

## CORS

Если возникают CORS ошибки, убедитесь, что в `app/main.py` настроен CORSMiddleware:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
