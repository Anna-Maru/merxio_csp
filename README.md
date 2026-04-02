# Merxio Shop — E-commerce API с аналитикой продаж

Мини-платформа электронной коммерции с REST API,
веб-интерфейсом и аналитическим дашбордом.

## Стек технологий

- **Backend:** Python 3.14, FastAPI, SQLAlchemy (async), asyncpg, Alembic
- **База данных:** PostgreSQL 18
- **Аутентификация:** JWT (PyJWT), bcrypt
- **Аналитика и экспорт:** pandas, openpyxl, reportlab, Chart.js
- **Тестирование:** pytest, pytest-asyncio, httpx, coverage 77%
- **Качество кода:** black, ruff
- **Контейнеризация:** Docker, Docker Compose

## Структура проекта
```
merxio_csp/
├── app/
│   ├── api/          # роутеры FastAPI
│   ├── core/         # конфиг, JWT, валидация
│   ├── db/           # подключение к БД, сессии
│   ├── models/       # SQLAlchemy модели
│   ├── schemas/      # Pydantic схемы
│   ├── services/     # бизнес-логика
│   └── main.py       # точка входа
├── frontend/         # HTML/CSS/JS интерфейс
├── tests/            # pytest тесты
├── alembic/          # миграции БД
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Быстрый старт

### 1. Клонировать репозиторий
```bash
git clone https://github.com/Anna-Maru/merxio_csp.git
cd merxio_csp
```

### 2. Создать файл переменных окружения
```bash
cp .env.example .env
```

Отредактируй `.env` — укажите свои значения (особенно `SECRET_KEY`).

### 3. Запустить через Docker Compose
```bash
docker-compose up --build
```

### 4. Применить миграции

В отдельном терминале (пока контейнеры запущены):
```bash
# Временно измените POSTGRES_HOST=localhost в .env
alembic upgrade head
# Верните POSTGRES_HOST=db
```

### 5. Создать администратора

Зарегистрируйтесь через API или фронтенд, затем вручную
установите `is_admin=true` в базе данных через pgAdmin или psql:
```sql
UPDATE users SET is_admin = true WHERE email = 'ваш@email.com';
```

## Переменные окружения

| Переменная | Описание | Пример |
|---|---|---|
| `POSTGRES_USER` | Пользователь БД | `shop_user` |
| `POSTGRES_PASSWORD` | Пароль БД | `shop_pass` |
| `POSTGRES_DB` | Имя базы данных | `shop_db` |
| `POSTGRES_HOST` | Хост БД (db в Docker) | `db` |
| `POSTGRES_PORT` | Порт БД | `5432` |
| `SECRET_KEY` | Секрет для JWT | случайная строка 32+ символа |
| `ALGORITHM` | Алгоритм JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена | `60` |
| `DEBUG` | Режим отладки | `True` / `False` |

Сгенерировать `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## API эндпоинты

| Метод | Путь | Доступ | Описание |
|---|---|---|---|
| POST | `/auth/register` | все | Регистрация |
| POST | `/auth/login` | все | Авторизация → JWT |
| GET | `/products/` | авторизован | Каталог с фильтрами |
| POST | `/products/` | admin | Создать товар |
| PUT | `/products/{id}` | admin | Обновить товар |
| DELETE | `/products/{id}` | admin | Удалить товар |
| GET | `/cart/` | авторизован | Получить корзину |
| POST | `/cart/items` | авторизован | Добавить товары |
| PATCH | `/cart/items/{id}` | авторизован | Изменить количество |
| DELETE | `/cart/items/{id}` | авторизован | Удалить позицию |
| DELETE | `/cart/` | авторизован | Очистить корзину |
| GET | `/cart/total` | авторизован | Сумма корзины |
| POST | `/orders/` | авторизован | Оформить заказ |
| GET | `/orders/` | авторизован | История заказов |
| PATCH | `/orders/{id}/status` | admin | Сменить статус |
| GET | `/analytics/summary` | admin | KPI сводка |
| GET | `/analytics/top-products` | admin | Топ товаров |
| GET | `/analytics/categories` | admin | По категориям |
| GET | `/analytics/dynamics` | admin | Динамика продаж |
| GET | `/analytics/export/xlsx` | admin | Экспорт Excel |
| GET | `/analytics/export/pdf` | admin | Экспорт PDF |

## Документация API

После запуска доступна автоматически:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Веб-интерфейс

| Страница | URL |
|---|---|
| Вход | `http://localhost:8000/frontend/login.html` |
| Регистрация | `http://localhost:8000/frontend/register.html` |
| Каталог товаров | `http://localhost:8000/frontend/index.html` |
| Мои заказы | `http://localhost:8000/frontend/orders.html` |
| Админ-панель | `http://localhost:8000/frontend/admin.html` |

## Запуск тестов
```bash
# Активировать виртуальное окружение
.\.venv\Scripts\Activate.ps1   # Windows
source .venv/bin/activate       # Linux/Mac

# Установить зависимости
pip install -r requirements.txt

# Запустить тесты с покрытием
pytest tests/ -v --cov=app --cov-report=term-missing
```

Покрытие: **77%** (требование ТЗ: ≥75%)

## Качество кода
```bash
# Форматирование
black app/ tests/

# Линтинг
ruff check app/ tests/
```