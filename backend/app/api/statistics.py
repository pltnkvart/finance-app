from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.domain.services.statistics_service import StatisticsService

router = APIRouter()


@router.get("/summary")
async def get_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get transaction statistics summary"""
    service = StatisticsService(db)
    return service.get_summary(start_date, end_date)


@router.get("/by-category")
async def get_by_category(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get spending by category"""
    service = StatisticsService(db)
    return service.get_by_category(start_date, end_date)
