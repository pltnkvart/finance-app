# Setup Instructions

## Prerequisites
- Docker and Docker Compose installed
- Telegram account (to create a bot)

## Quick Start

### 1. Get Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (looks like `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Configure Environment Variables

**Copy the example file and edit it:**

```bash
cp .env.example .env
```

Open the `.env` file in the root directory and update these values:

```env
# Replace with your actual bot token from @BotFather
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Generate a secure random key for production
SECRET_KEY=your_secure_random_secret_key_here
```

**To generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Important:** Never commit the `.env` file to Git! It's already in `.gitignore`.

### 3. Start the Application

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 4. Verify Everything Works

1. **Check backend API**: Open http://localhost:8000/docs in your browser
2. **Check Telegram bot**: Send `/start` to your bot in Telegram
3. **Test transaction**: Send a message like `100 grocery store` to your bot

### 5. Access the Dashboard

Open http://localhost:3000 in your browser to view the React dashboard.

## How It Works

1. **PostgreSQL** runs on port 5432 with the database `fintrack`
2. **Backend API** runs on port 8000 with automatic migrations
3. **Telegram Bot** connects to Telegram and listens for messages
4. **Frontend Dashboard** runs on port 3000 (Next.js)

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (including database)
docker-compose down -v
```

## Troubleshooting

### Permission Issues
If you get permission errors, try:
```bash
chmod +x backend/scripts/run_migrations.sh
docker-compose up --build
```

### Bot Not Responding
1. Check that `TELEGRAM_BOT_TOKEN` is set correctly in `.env`
2. Check bot logs: `docker-compose logs telegram-bot`
3. Verify backend is running: `docker-compose logs backend`

### Database Connection Issues
1. Wait 10-15 seconds for PostgreSQL to fully start
2. Check database logs: `docker-compose logs postgres`
3. Restart services: `docker-compose restart`

## Development

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f telegram-bot
```

### Rebuild After Code Changes
```bash
docker-compose up --build
```

### Access Database
```bash
docker-compose exec postgres psql -U fintrack_user -d fintrack
