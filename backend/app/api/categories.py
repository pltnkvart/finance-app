from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.domain.services.category_service import CategoryService

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all categories"""
    service = CategoryService(db)
    return service.get_categories()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a category by ID"""
    service = CategoryService(db)
    category = service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category


@router.post("/", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new category"""
    service = CategoryService(db)
    return service.create_category(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a category"""
    service = CategoryService(db)
    category = service.update_category(category_id, category_update)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a category"""
    service = CategoryService(db)
    success = service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return {"message": "Категория удалена"}
