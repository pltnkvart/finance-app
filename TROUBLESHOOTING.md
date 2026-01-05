# Решение проблем

## Ошибки сети при сборке Docker образа

### Проблема: "Name or service not known" при установке pip пакетов

Если вы видите ошибку:
```
ERROR: Could not find a version that satisfies the requirement fastapi==0.109.0
NewConnectionError: Failed to establish a new connection: [Errno -2] Name or service not known
```

Это означает, что Docker контейнер не может подключиться к интернету для загрузки Python пакетов.

### Решения:

#### 1. Перезапустите Docker Desktop
```bash
# Остановите все контейнеры
docker-compose down

# Перезапустите Docker Desktop полностью
# После перезапуска попробуйте снова
docker-compose up --build
```

#### 2. Проверьте DNS настройки Docker

Откройте Docker Desktop → Settings → Resources → Network и убедитесь, что DNS настроен правильно.

Или добавьте DNS в файл `/etc/docker/daemon.json` (для Linux/Mac):
```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

После изменения перезапустите Docker:
```bash
sudo systemctl restart docker  # Linux
```

#### 3. Используйте системный network driver

Попробуйте запустить с системным network:
```bash
docker-compose build --network=host
```

#### 4. Проверьте прокси (если вы за корпоративным фаерволом)

Если вы используете корпоративный прокси, добавьте в Dockerfile.backend:
```dockerfile
ENV HTTP_PROXY=http://your-proxy:port
ENV HTTPS_PROXY=http://your-proxy:port
```

#### 5. Попробуйте собрать образ напрямую

```bash
# Соберите backend образ отдельно с логами
docker build -f Dockerfile.backend --progress=plain --network=host -t fintrack-backend .

# Если успешно, запустите все сервисы
docker-compose up
```

#### 6. Используйте готовые образы (временное решение)

Если ничего не помогает, можно установить зависимости локально:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # для Linux/Mac
# или venv\Scripts\activate для Windows
pip install -r requirements.txt
```

Затем запустите только базу данных через Docker:
```bash
docker-compose up postgres
```

И бэкенд локально:
```bash
cd backend
export DATABASE_URL="postgresql://fintrack_user:fintrack_pass@localhost:5432/fintrack"
export TELEGRAM_BOT_TOKEN="your_token"
python -m alembic upgrade head
uvicorn app.main:app --reload
```

## Другие проблемы

### Ошибка: "Permission denied" для скриптов

```bash
chmod +x backend/scripts/run_migrations.sh
docker-compose up --build
```

### База данных не подключается

Убедитесь, что PostgreSQL контейнер запущен:
```bash
docker-compose ps
docker-compose logs postgres
```

### Порт уже занят

Если порты 8000 или 5432 заняты, измените их в docker-compose.yml:
```yaml
ports:
  - "8001:8000"  # вместо 8000:8000
