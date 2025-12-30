# FinTrack - Financial Tracking Application

A full-stack financial tracking application with Telegram bot integration for automatic transaction parsing and categorization.

## Features

- Telegram bot for easy transaction input via messages
- Automatic transaction parsing from natural language
- Smart categorization with machine learning
- Analytics dashboard with visualizations
- CSV export functionality
- RESTful API backend

## Tech Stack

### Backend
- FastAPI (Python web framework)
- PostgreSQL (Database)
- SQLAlchemy + Alembic (ORM + Migrations)
- python-telegram-bot (Telegram integration)
- scikit-learn (ML categorization)

### Frontend
- Next.js 16 (React framework)
- Redux Toolkit + RTK Query (State management)
- Tailwind CSS (Styling)
- shadcn/ui (UI components)

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Telegram account (for bot setup)

### Setup

1. Clone the repository

2. Create a Telegram bot:
   - Open Telegram and search for @BotFather
   - Send `/newbot` and follow the prompts
   - Copy your bot token
   - See `backend/TELEGRAM_SETUP.md` for detailed instructions

3. Copy `.env.example` to `.env` and fill in your values:
\`\`\`bash
cp .env.example .env
\`\`\`

Edit `.env`:
\`\`\`
DATABASE_URL=postgresql://fintrack_user:fintrack_pass@localhost:5432/fintrack
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
SECRET_KEY=your_secret_key_here
ENVIRONMENT=development
NEXT_PUBLIC_API_URL=http://localhost:8000
\`\`\`

4. Start all services with Docker:
\`\`\`bash
docker-compose up -d
\`\`\`

This will start:
- PostgreSQL database
- FastAPI backend (with auto migrations)
- Telegram bot (polling mode)

5. Verify services are running:
\`\`\`bash
docker-compose ps
\`\`\`

6. Start the Next.js frontend:
\`\`\`bash
npm install
npm run dev
\`\`\`

7. Access the application:
   - Frontend: http://localhost:3000
   - API docs: http://localhost:8000/docs
   - API: http://localhost:8000

### Testing the Bot

1. Open Telegram and search for your bot
2. Send `/start` to initialize
3. Try sending: `100 groceries`
4. Check the dashboard to see your transaction

## Project Structure

\`\`\`
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── bot/         # Telegram bot
│   │   ├── core/        # Core configuration
│   │   ├── domain/      # Business logic
│   │   ├── models/      # Database models
│   │   └── schemas/     # Pydantic schemas
│   ├── migrations/      # Alembic migrations
│   ├── scripts/         # Utility scripts
│   └── requirements.txt
├── app/                 # Next.js frontend
│   ├── api/            # API route handlers
│   ├── components/     # React components
│   └── lib/            # Utilities
├── docker-compose.yml
└── README.md
\`\`\`

## Development Commands

### Backend

\`\`\`bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# View logs
docker-compose logs backend
docker-compose logs telegram-bot

# Run tests
docker-compose exec backend pytest
\`\`\`

### Frontend

\`\`\`bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
\`\`\`

## Bot Usage

### Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/stats` - View statistics

### Transaction Formats
- `100 groceries` - Amount + description
- `coffee 5` - Description + amount
- `100` - Just amount

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Roadmap

- [x] Setup Project Structure & Docker
- [x] Create Database Models & Migrations
- [x] Build Core API Endpoints
- [x] Implement Telegram Bot Parser
- [ ] Build Categorization Engine
- [ ] Create React Dashboard

## License

MIT
