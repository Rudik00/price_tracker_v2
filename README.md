# Price Tracker v2

Telegram-бот + API + Telegram Mini App для отслеживания цен на товары
(сейчас поддерживается Wildberries).

## Возможности

- Добавление товара по ссылке в боте
- Хранение цен в PostgreSQL
- Фоновое обновление цен через Celery + Redis
- Уведомление в Telegram, если цена снизилась
- Мини-приложение Telegram для красивого вывода всех товаров

## Структура проекта

```text
price_tracker_v2/
├── app/                   # FastAPI (backend для Mini App)
├── database/              # SQLAlchemy модели и запросы
├── frontend/              # HTML/CSS/JS для Telegram Mini App
├── parser/
│   ├── wildberries/       # Парсер Wildberries
│   └── ozon/              # Парсер Ozon (в разработке)
├── task_queue/            # Celery app и фоновые задачи
├── teregram_bot/          # Telegram бот (aiogram)
├── requirements.txt       # Список библиотек
└── README.md
```

## Требования

- macOS/Linux/WSL
- Python 3.10+
- PostgreSQL 14+
- Redis 6+

## Полная установка с нуля (если проект уже скачан)

### 1. Перейти в папку проекта

```bash
cd /Users/ilarudyj78gmail.com/Программирование/price_tracker_v2
```

### 2. Создать и активировать виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
```

### 3. Установить Python-зависимости

```bash
pip install -r requirements.txt
```

### 4. Установить браузер для Playwright

```bash
playwright install chromium
```

### 5. Поднять PostgreSQL и Redis

Вариант A (локально через Homebrew):

```bash
brew install postgresql@16 redis
brew services start postgresql@16
brew services start redis
```

Вариант B (Docker, если удобно):

```bash
docker run -d --name pt-postgres -e POSTGRES_PASSWORD=54321 -e POSTGRES_USER=price_tracker_user -e POSTGRES_DB=price_tracker_db -p 5432:5432 postgres:16
docker run -d --name pt-redis -p 6379:6379 redis:7
```

### 6. Создать файл .env

Создай `.env` в корне проекта со значениями:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql+asyncpg://price_tracker_user:54321@localhost:5432/price_tracker_db
REDIS_URL=redis://localhost:6379/0

# Для Mini App
USE_MINI_APP=true
MINI_APP_URL=https://your-public-url
```

## Как запускать весь проект

Нужно 4 терминала.

### Терминал 1: FastAPI (API + frontend)

```bash
source venv/bin/activate
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

### Терминал 2: ngrok (для публичного HTTPS URL)

```bash
ngrok http 8000
```

Скопируй значение из строки вида:

```text
Forwarding https://xxxxx.ngrok-free.app -> http://localhost:8000
```

Это и есть `MINI_APP_URL` в `.env`.

После изменения `.env` перезапусти бот.

### Терминал 3: Celery worker

```bash
source venv/bin/activate
celery -A task_queue.celery_app worker --loglevel=info
```

### Терминал 4: Telegram бот

```bash
source venv/bin/activate
python3 -m teregram_bot.main_bot
```

## Что происходит при запуске

- Бот на старте вызывает `init_db()` и создает таблицы при необходимости
- Celery worker обрабатывает задачи парсинга
- Фоновый цикл ставит задачи обновления цен по товарам
- Команда `/show_all_products` отправляет кнопку открытия Mini App
- Mini App берет `initData` из Telegram, API валидирует подпись и возвращает товары этого пользователя

## Команды бота

- `/start` — приветствие
- `/info` — информация о боте
- `/adding_by_link` — добавить товар по ссылке
- `/show_one_products` — показать товар по local_id или URL
- `/show_all_products` — открыть Mini App со всеми товарами
- `/delete_product` — удалить товар по local_id или URL

## Проверка после установки

1. В Telegram отправить `/adding_by_link` и добавить товар Wildberries
2. Проверить, что товар появился по `/show_one_products`
3. Отправить `/show_all_products`
4. Нажать кнопку Mini App и убедиться, что список загрузился

## Частые проблемы

1. Бот не отвечает на `/show_all_products`
- Проверь, что в `.env` заполнен `MINI_APP_URL`
- Проверь, что `USE_MINI_APP=true`
- Перезапусти бот после изменения `.env`

2. Mini App не открывается
- Проверь, что ngrok запущен
- Проверь, что `MINI_APP_URL` начинается с `https://`

3. API отдает 401 для Mini App
- Это обычно невалидный `initData` (открытие страницы вне Telegram)

4. Ошибка `Object of type Bot is not JSON serializable`
- В Celery-задачи передавать только примитивы, не объекты `Bot`

## Что хранится в базе данных

Таблица `users`:
- `telegram_id` — ID пользователя в Telegram
- `local_id` — порядковый номер товара у этого пользователя (1, 2, 3...)
- `url` — ссылка на товар

Таблица `products`:
- `price_now` / `price_start` / `price_max` / `price_min` — цены (NUMERIC 10,2)
- `currency` — валюта (берётся с сайта при парсинге)
- `img` — URL картинки товара

> При удалении товара `local_id` остальных товаров автоматически пересчитывается.

## Блокировка Ozon

Ozon может показать страницу «Доступ ограничен» при парсинге.  
Способы снизить риск:
- Ставить редкий интервал обновления (30–120 мин)
- Использовать прокси
- Убедиться, что IP-адрес не датацентровый

## Ограничения

- Сейчас поддерживается только Wildberries
- Адрес ngrok временный и меняется при новом запуске
- `img` заполняется только при первом парсинге; если элемент не найден — будет `null`
