# Price Tracker v2

Telegram-бот для отслеживания цен товаров (сейчас поддерживается Wildberries).

Проект умеет:
- добавлять товар по ссылке;
- хранить историю цены в PostgreSQL;
- периодически обновлять цены в фоне через Celery;
- отправлять уведомление в Telegram, если цена снизилась.

## Стек

- Python 3.10+
- aiogram 3
- SQLAlchemy (async) + asyncpg
- PostgreSQL
- Celery + Redis
- Playwright (парсинг с рендерингом JS)
- BeautifulSoup4

## Структура проекта

```text
price_tracker_v2/
├── database/              # Модели и операции с БД
├── parser/                # Парсер Wildberries
├── task_queue/            # Celery app, задачи и фоновый планировщик
├── teregram_bot/          # Telegram-бот (handlers + FSM)
└── README.md
```

## Переменные окружения

Создай файл `.env` в корне проекта:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql+asyncpg://price_tracker_user:54321@localhost:5432/price_tracker_db
REDIS_URL=redis://localhost:6379/0
```

## Установка

1. Создай и активируй виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Установи зависимости:

```bash
pip install aiogram celery redis sqlalchemy asyncpg python-dotenv playwright beautifulsoup4 lxml
playwright install chromium
```

3. Подними PostgreSQL и Redis (локально или в Docker).

## Подготовка БД

Таблицы создаются автоматически при старте бота через `init_db()`.

Важно:
- в таблице `products` цены хранятся как `NUMERIC(10,2)`;
- `products.id_product` связан с `users.id`.

## Запуск

Запускать нужно в двух терминалах.

Терминал 1: Celery worker

```bash
celery -A task_queue.celery_app worker --loglevel=info
```

Терминал 2: Telegram-бот

```bash
python3 -m teregram_bot.main_bot
```

После старта бота запускается фоновый цикл обновления цен:
- файл: `task_queue/background_price_updater.py`;
- текущий интервал в коде: `2 * 60` секунд (режим теста);
- для 2 часов поставь `2 * 60 * 60`.

## Команды бота

- `/start` — приветствие
- `/info` — информация о боте
- `/adding_by_link` — добавить товар по ссылке
- `/show_one_products` — показать товар по ID или URL
- `/show_all_products` — показать все отслеживаемые товары
- `/delete_product` — удалить товар по ID или URL

## Как работает уведомление о снижении цены

1. Планировщик ставит задачи в Celery для всех ссылок.
2. Задача парсит текущую цену.
3. Цена сравнивается с предыдущей в БД.
4. Если новая цена ниже предыдущей, бот отправляет сообщение пользователю.

## Частые проблемы

1. Ошибка `Object of type Bot is not JSON serializable`

Причина: передача объекта Bot в аргументах Celery-задачи.

Решение: передавать в задачу только примитивы (`int`, `str`, `dict`, `list`),
а `Bot(...)` создавать внутри worker-процесса.

2. Не отправляются уведомления

Проверь:
- что `TELEGRAM_BOT_TOKEN` корректный;
- что запущен Celery worker;
- что в `chat_id` используется `telegram_id`, а не внутренний id из таблицы;
- что цена действительно снизилась.

3. Парсер не находит цену

Иногда Wildberries меняет верстку. В этом случае нужно обновить селекторы
в `parser/wildberries/parser.py`.

## Текущее ограничение

Сейчас поддерживается только Wildberries.
