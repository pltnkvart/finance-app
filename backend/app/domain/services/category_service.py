from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_categories(self) -> List[Category]:
        """Get all categories"""
        return self.db.query(Category).all()

    def get_category(self, category_id: int) -> Optional[Category]:
        """Get a category by ID"""
        return self.db.query(Category).filter(Category.id == category_id).first()

    def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category"""
        category = Category(**category_data.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update_category(self, category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
        """Update a category"""
        category = self.get_category(category_id)
        if not category:
            return None

        update_data = category_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)

        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: int) -> bool:
        """Delete a category"""
        category = self.get_category(category_id)
        if not category:
            return False

        self.db.delete(category)
        self.db.commit()
        return True
