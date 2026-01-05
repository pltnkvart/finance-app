# FinTrack - Приложение для учета финансов

Полнофункциональное приложение для отслеживания финансов с интеграцией Telegram-бота для автоматического парсинга и категоризации транзакций.

## Возможности

- Telegram-бот для простого ввода транзакций через сообщения
- Автоматический парсинг транзакций из естественного языка
- Умная категоризация с машинным обучением
- Панель аналитики с визуализацией
- Экспорт в CSV
- Управление счетами и вкладами
- Расчет общего баланса
- RESTful API бэкенд

## Технологии

### Бэкенд
- FastAPI (Python веб-фреймворк)
- PostgreSQL (База данных)
- SQLAlchemy + Alembic (ORM + Миграции)
- python-telegram-bot (Интеграция с Telegram)
- scikit-learn (ML категоризация)

### Фронтенд
- Next.js 16 (React фреймворк)
- Tailwind CSS (Стилизация)
- shadcn/ui (UI компоненты)

## Начало работы

### Требования
- Docker и Docker Compose
- Node.js 18+ (для разработки фронтенда)
- Python 3.11+ (для разработки бэкенда)
- Telegram аккаунт (для настройки бота)

### Установка

1. Клонируйте репозиторий

2. Создайте Telegram-бота:
   - Откройте Telegram и найдите @BotFather
   - Отправьте `/newbot` и следуйте инструкциям
   - Скопируйте токен бота
   - См. `backend/TELEGRAM_SETUP.md` для подробных инструкций

3. Скопируйте `.env.example` в `.env` и заполните значения:
```bash
cp .env.example .env
```

Отредактируйте `.env`:
```
DATABASE_URL=postgresql://fintrack_user:fintrack_pass@localhost:5432/fintrack
TELEGRAM_BOT_TOKEN=ваш_токен_telegram_бота
SECRET_KEY=ваш_секретный_ключ
ENVIRONMENT=development
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Запустите все сервисы через Docker:
```bash
docker-compose up --build
```

⚠️ **Если возникает ошибка сети при сборке**, см. `TROUBLESHOOTING.md`

Это запустит:
- PostgreSQL базу данных
- FastAPI бэкенд (с автоматическими миграциями)
- Telegram-бот (режим polling)

5. Проверьте, что сервисы запущены:
```bash
docker-compose ps
```

6. Запустите Next.js фронтенд:
```bash
npm install
npm run dev
```

7. Откройте приложение:
   - Фронтенд: http://localhost:3000
   - API документация: http://localhost:8000/docs
   - API: http://localhost:8000

### Тестирование бота

1. Откройте Telegram и найдите вашего бота
2. Отправьте `/start` для инициализации
3. Попробуйте отправить: `100 продукты`
4. Проверьте дашборд - там появится ваша транзакция

## Структура проекта

```
├── backend/              # FastAPI бэкенд
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── bot/         # Telegram бот
│   │   ├── core/        # Основная конфигурация
│   │   ├── domain/      # Бизнес-логика
│   │   ├── models/      # Модели базы данных
│   │   └── schemas/     # Pydantic схемы
│   ├── migrations/      # Alembic миграции
│   ├── scripts/         # Утилиты
│   └── requirements.txt
├── app/                 # Next.js фронтенд
│   ├── accounts/       # Страница счетов
│   ├── analytics/      # Аналитика
│   ├── export/         # Экспорт данных
│   ├── transactions/   # Транзакции
│   └── settings/       # Настройки
├── components/          # React компоненты
├── docker-compose.yml
├── TROUBLESHOOTING.md   # Решение проблем
└── README.md
```

## Команды разработки

### Бэкенд

```bash
# Запуск миграций
docker-compose exec backend alembic upgrade head

# Создание новой миграции
docker-compose exec backend alembic revision --autogenerate -m "описание"

# Просмотр логов
docker-compose logs backend
docker-compose logs telegram-bot

# Запуск тестов
docker-compose exec backend pytest

# Остановка сервисов
docker-compose down
```

### Фронтенд

```bash
# Запуск dev сервера
npm run dev

# Сборка для продакшена
npm run build

# Запуск продакшн сервера
npm start
```

## Использование бота

### Команды
- `/start` - Запустить бота
- `/help` - Показать помощь
- `/stats` - Посмотреть статистику

### Форматы транзакций
- `100 продукты` - Сумма + описание
- `кофе 5` - Описание + сумма
- `100` - Только сумма

## Документация API

После запуска бэкенда доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Основные эндпоинты:

- `GET /api/transactions` - Список транзакций
- `POST /api/transactions` - Создать транзакцию
- `GET /api/accounts` - Список счетов
- `POST /api/accounts` - Создать счет
- `GET /api/deposits` - Список вкладов
- `POST /api/deposits` - Создать вклад
- `GET /api/statistics` - Статистика и общий баланс
- `POST /api/export/csv` - Экспорт в CSV

## Решение проблем

Если при запуске возникают проблемы, см. `TROUBLESHOOTING.md`:
- Ошибки сети при сборке Docker образа
- Проблемы с DNS
- Permission denied для скриптов
- База данных не подключается
- Порты заняты

## План разработки

- [x] Настройка структуры проекта и Docker
- [x] Создание моделей базы данных и миграций
- [x] Создание основных API endpoints
- [x] Реализация Telegram бота
- [x] Создание движка категоризации с ML
- [x] Создание React дашборда
- [x] Русификация интерфейса
- [x] Добавление счетов и вкладов
- [x] Общий баланс

## Лицензия

MIT
