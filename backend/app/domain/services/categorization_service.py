from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
import re
from difflib import SequenceMatcher

from app.models.categorization_rule import CategorizationRule
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user_correction import UserCorrection
from app.core.config import settings
from app.domain.ml.categorizer import MLCategorizer


class CategorizationService:
    def __init__(self, db: Session):
        self.db = db
        self.ml_categorizer = MLCategorizer(min_samples=settings.MIN_TRAINING_SAMPLES)
        # Try to load existing model
        self.ml_categorizer.load_model()
    
    def predict_category(self, description: str) -> Optional[int]:
        """Predict category for a transaction description"""
        # First try ML-based prediction
        ml_prediction = self._predict_with_ml(description)
        if ml_prediction:
            return ml_prediction
        
        # Fallback to rule-based prediction
        rule_prediction = self._predict_with_rules(description)
        if rule_prediction:
            return rule_prediction
        
        # Last resort: return "Other" category
        return self._get_other_category_id()
    
    def _predict_with_ml(self, description: str) -> Optional[int]:
        """Use ML model for prediction"""
        if not self.ml_categorizer.is_trained:
            return None
        
        result = self.ml_categorizer.predict(description, threshold=settings.SIMILARITY_THRESHOLD)
        if result:
            category_id, confidence = result
            return category_id
        
        return None
    
    def _predict_with_rules(self, description: str) -> Optional[int]:
        """Use rule-based system for prediction"""
        normalized = self._normalize_text(description)
        rules = self.db.query(CategorizationRule).all()
        
        best_match = None
        best_similarity = 0.0
        
        for rule in rules:
            similarity = self._calculate_similarity(normalized, rule.pattern)
            
            if similarity > best_similarity and similarity >= settings.SIMILARITY_THRESHOLD:
                best_similarity = similarity
                best_match = rule
        
        if best_match:
            best_match.times_applied += 1
            self.db.commit()
            return best_match.category_id
        
        return None
    
    def learn_from_correction(
        self, 
        transaction_id: int, 
        old_category_id: Optional[int], 
        new_category_id: int,
        description: str
    ):
        """Learn from user correction"""
        # Record the correction
        correction = UserCorrection(
            transaction_id=transaction_id,
            old_category_id=old_category_id,
            new_category_id=new_category_id
        )
        self.db.add(correction)
        
        # Update ML model
        self.ml_categorizer.update_with_correction(description, new_category_id)
        
        # Create or update categorization rule
        normalized = self._normalize_text(description)
        
        existing_rule = self.db.query(CategorizationRule).filter(
            CategorizationRule.pattern == normalized
        ).first()
        
        if existing_rule:
            if existing_rule.category_id == new_category_id:
                existing_rule.times_correct += 1
            else:
                existing_rule.category_id = new_category_id
                existing_rule.times_correct = 1
                existing_rule.times_applied = 1
            
            existing_rule.confidence = (
                existing_rule.times_correct / existing_rule.times_applied
            )
        else:
            new_rule = CategorizationRule(
                pattern=normalized,
                category_id=new_category_id,
                confidence=1.0,
                times_applied=1,
                times_correct=1
            )
            self.db.add(new_rule)
        
        self.db.commit()
    
    def train_ml_model(self) -> dict:
        """
        Train the ML model on all existing categorized transactions
        """
        transactions = self.db.query(Transaction).filter(
            Transaction.category_id.isnot(None)
        ).all()
        
        if len(transactions) < settings.MIN_TRAINING_SAMPLES:
            return {
                "success": False,
                "message": f"Not enough training data. Need at least {settings.MIN_TRAINING_SAMPLES} transactions.",
                "current_count": len(transactions)
            }
        
        success = self.ml_categorizer.train(transactions)
        
        if success:
            stats = self.ml_categorizer.get_stats()
            return {
                "success": True,
                "message": "ML model trained successfully",
                "stats": stats
            }
        else:
            return {
                "success": False,
                "message": "Training failed. Not enough diverse data.",
                "stats": self.ml_categorizer.get_stats()
            }
    
    def get_categorization_stats(self) -> dict:
        """Get statistics about categorization"""
        total_rules = self.db.query(func.count(CategorizationRule.id)).scalar()
        avg_confidence = self.db.query(
            func.avg(CategorizationRule.confidence)
        ).scalar() or 0.0
        
        total_corrections = self.db.query(func.count(UserCorrection.id)).scalar()
        
        ml_stats = self.ml_categorizer.get_stats()
        
        return {
            "rule_based": {
                "total_rules": total_rules,
                "average_confidence": float(avg_confidence)
            },
            "machine_learning": ml_stats,
            "user_corrections": total_corrections,
            "threshold": settings.SIMILARITY_THRESHOLD
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = ' '.join(text.split())
        return text
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _get_other_category_id(self) -> Optional[int]:
        """Get the ID of the 'Other' category"""
        other_category = self.db.query(Category).filter(
            Category.name == "Other"
        ).first()
        return other_category.id if other_category else None
