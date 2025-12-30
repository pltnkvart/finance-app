from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.services.categorization_service import CategorizationService

router = APIRouter()


@router.post("/train")
async def train_categorization_model(
    db: Session = Depends(get_db)
):
    """
    Train the ML categorization model on existing transactions
    
    This will use all categorized transactions as training data
    and build a TF-IDF based classifier.
    """
    service = CategorizationService(db)
    result = service.train_ml_model()
    return result


@router.get("/stats")
async def get_categorization_stats(
    db: Session = Depends(get_db)
):
    """
    Get statistics about the categorization system
    
    Includes both rule-based and ML metrics
    """
    service = CategorizationService(db)
    return service.get_categorization_stats()


@router.post("/predict")
async def predict_category(
    description: str,
    db: Session = Depends(get_db)
):
    """
    Test category prediction for a given description
    """
    service = CategorizationService(db)
    category_id = service.predict_category(description)
    
    if category_id:
        from app.models.category import Category
        category = db.query(Category).filter(Category.id == category_id).first()
        return {
            "category_id": category_id,
            "category_name": category.name if category else None
        }
    else:
        return {
            "category_id": None,
            "category_name": "Unable to predict"
        }
