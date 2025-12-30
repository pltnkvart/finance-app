"""
Machine Learning categorization engine using TF-IDF and similarity matching
"""
import pickle
import re
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user_correction import UserCorrection


class MLCategorizer:
    """
    ML-based categorizer using TF-IDF vectorization
    """
    
    def __init__(self, min_samples: int = 3):
        self.min_samples = min_samples
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 2),
            stop_words='english'
        )
        self.is_trained = False
        self.category_vectors: Dict[int, np.ndarray] = {}
        self.category_descriptions: Dict[int, List[str]] = {}
        self.model_path = Path("app/domain/ml/models")
        self.model_path.mkdir(parents=True, exist_ok=True)
    
    def train(self, transactions: List[Transaction]):
        """
        Train the categorizer on existing transactions
        """
        if len(transactions) < self.min_samples:
            return False
        
        # Group transactions by category
        category_data: Dict[int, List[str]] = {}
        
        for transaction in transactions:
            if transaction.category_id:
                if transaction.category_id not in category_data:
                    category_data[transaction.category_id] = []
                category_data[transaction.category_id].append(
                    self._preprocess_text(transaction.description)
                )
        
        # Filter categories with enough samples
        valid_categories = {
            cat_id: descriptions 
            for cat_id, descriptions in category_data.items() 
            if len(descriptions) >= self.min_samples
        }
        
        if not valid_categories:
            return False
        
        # Prepare training data
        all_descriptions = []
        for descriptions in valid_categories.values():
            all_descriptions.extend(descriptions)
        
        # Fit vectorizer
        self.vectorizer.fit(all_descriptions)
        
        # Create category vectors (mean of all transaction vectors in category)
        self.category_vectors = {}
        self.category_descriptions = valid_categories
        
        for cat_id, descriptions in valid_categories.items():
            vectors = self.vectorizer.transform(descriptions)
            mean_vector = np.mean(vectors.toarray(), axis=0)
            self.category_vectors[cat_id] = mean_vector
        
        self.is_trained = True
        self._save_model()
        return True
    
    def predict(self, description: str, threshold: float = 0.3) -> Optional[Tuple[int, float]]:
        """
        Predict category for a description
        Returns: (category_id, confidence) or None
        """
        if not self.is_trained or not self.category_vectors:
            return None
        
        # Preprocess and vectorize
        preprocessed = self._preprocess_text(description)
        vector = self.vectorizer.transform([preprocessed]).toarray()[0]
        
        # Calculate similarity with each category
        best_category = None
        best_score = 0.0
        
        for cat_id, cat_vector in self.category_vectors.items():
            similarity = cosine_similarity(
                vector.reshape(1, -1), 
                cat_vector.reshape(1, -1)
            )[0][0]
            
            if similarity > best_score:
                best_score = similarity
                best_category = cat_id
        
        # Only return if confidence is above threshold
        if best_score >= threshold:
            return (best_category, float(best_score))
        
        return None
    
    def update_with_correction(self, description: str, category_id: int):
        """
        Update the model with a user correction
        """
        preprocessed = self._preprocess_text(description)
        
        # Add to category descriptions
        if category_id not in self.category_descriptions:
            self.category_descriptions[category_id] = []
        self.category_descriptions[category_id].append(preprocessed)
        
        # Retrain if we have enough samples
        if len(self.category_descriptions[category_id]) >= self.min_samples:
            self._retrain_category(category_id)
    
    def _retrain_category(self, category_id: int):
        """
        Retrain vector for a specific category
        """
        if category_id not in self.category_descriptions:
            return
        
        descriptions = self.category_descriptions[category_id]
        if len(descriptions) < self.min_samples:
            return
        
        # Refit vectorizer with all current descriptions
        all_descriptions = []
        for desc_list in self.category_descriptions.values():
            all_descriptions.extend(desc_list)
        
        self.vectorizer.fit(all_descriptions)
        
        # Update category vector
        vectors = self.vectorizer.transform(descriptions)
        mean_vector = np.mean(vectors.toarray(), axis=0)
        self.category_vectors[category_id] = mean_vector
        
        self.is_trained = True
        self._save_model()
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for vectorization
        """
        # Convert to lowercase
        text = text.lower()
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def _save_model(self):
        """
        Save the trained model to disk
        """
        model_data = {
            'vectorizer': self.vectorizer,
            'category_vectors': self.category_vectors,
            'category_descriptions': self.category_descriptions,
            'is_trained': self.is_trained
        }
        
        model_file = self.model_path / 'categorizer.pkl'
        with open(model_file, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self) -> bool:
        """
        Load a trained model from disk
        """
        model_file = self.model_path / 'categorizer.pkl'
        
        if not model_file.exists():
            return False
        
        try:
            with open(model_file, 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.category_vectors = model_data['category_vectors']
            self.category_descriptions = model_data['category_descriptions']
            self.is_trained = model_data['is_trained']
            
            return True
        except Exception:
            return False
    
    def get_stats(self) -> dict:
        """
        Get statistics about the trained model
        """
        return {
            'is_trained': self.is_trained,
            'num_categories': len(self.category_vectors),
            'total_samples': sum(
                len(descriptions) 
                for descriptions in self.category_descriptions.values()
            ),
            'min_samples': self.min_samples
        }
