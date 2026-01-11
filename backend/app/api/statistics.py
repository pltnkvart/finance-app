from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, datetime, time
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.domain.services.statistics_service import StatisticsService

router = APIRouter()


@router.get("/summary")
async def get_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transaction statistics summary"""
    service = StatisticsService(db)
    start_datetime = datetime.combine(start_date, time.min) if start_date else None
    end_datetime = datetime.combine(end_date, time.max) if end_date else None
    return service.get_summary(current_user.id, start_datetime, end_datetime)


@router.get("/by-category")
async def get_by_category(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get spending by category"""
    service = StatisticsService(db)
    start_datetime = datetime.combine(start_date, time.min) if start_date else None
    end_datetime = datetime.combine(end_date, time.max) if end_date else None
    return service.get_by_category(current_user.id, start_datetime, end_datetime)


@router.get("/trend")
async def get_spending_trend(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly spending trend"""
    service = StatisticsService(db)
    start_datetime = datetime.combine(start_date, time.min) if start_date else None
    end_datetime = datetime.combine(end_date, time.max) if end_date else None
    return service.get_spending_trend(current_user.id, start_datetime, end_datetime)
