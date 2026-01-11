from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.api import transactions, categories, statistics, telegram, export, accounts, deposits, auth
from app.core.config import settings
from app.core.database import SessionLocal
from app.domain.services.deposit_service import DepositService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.PROJECT_NAME}...")
    scheduler = BackgroundScheduler()

    def close_overdue_deposits_job():
        db = SessionLocal()
        try:
            service = DepositService(db)
            closed_count = service.close_overdue_deposits()
            if closed_count:
                logger.info("Closed overdue deposits: %s", closed_count)
        finally:
            db.close()

    scheduler.add_job(
        close_overdue_deposits_job,
        CronTrigger(hour=0, minute=5),
        id="close_overdue_deposits",
        replace_existing=True
    )
    scheduler.start()
    yield
    # Shutdown
    scheduler.shutdown()
    print("Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])
app.include_router(telegram.router, prefix="/api/telegram", tags=["telegram"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(deposits.router, prefix="/api/deposits", tags=["deposits"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
