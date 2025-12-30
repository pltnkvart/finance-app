from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
import io
import csv

from app.core.database import get_db
from app.domain.services.export_service import ExportService

router = APIRouter()


@router.get("/csv")
async def export_transactions_csv(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Export transactions to CSV"""
    service = ExportService(db)
    csv_data = service.export_to_csv(
        start_date=start_date,
        end_date=end_date,
        category_id=category_id
    )
    
    # Create streaming response
    output = io.StringIO()
    output.write(csv_data)
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=transactions_{date.today()}.csv"
        }
    )
