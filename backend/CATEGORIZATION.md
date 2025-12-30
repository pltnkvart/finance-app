# Categorization Engine Documentation

The categorization engine uses a hybrid approach combining rule-based and machine learning methods to automatically categorize transactions.

## How It Works

### 1. Dual-System Architecture

**ML-Based (Primary)**
- Uses TF-IDF (Term Frequency-Inverse Document Frequency) vectorization
- Calculates cosine similarity between transaction descriptions
- Trains on historical categorized transactions
- More accurate with sufficient training data

**Rule-Based (Fallback)**
- Simple pattern matching using string similarity
- Uses Levenshtein distance for comparison
- Works immediately without training
- Good for exact matches

### 2. Learning Process

The engine learns from two sources:

**Initial Training**
- Processes all existing categorized transactions
- Builds TF-IDF vocabulary from descriptions
- Creates category vectors (mean of all transactions in category)
- Saves model to disk for persistence

**Continuous Learning**
- Updates when users correct categories
- Adds new patterns to the model
- Retrains category vectors dynamically
- Improves accuracy over time

## Configuration

Settings in `app/core/config.py`:

\`\`\`python
MIN_TRAINING_SAMPLES: int = 3  # Minimum transactions per category
SIMILARITY_THRESHOLD: float = 0.7  # Confidence threshold (0-1)
\`\`\`

- **MIN_TRAINING_SAMPLES**: Minimum number of transactions needed per category before ML training
- **SIMILARITY_THRESHOLD**: Minimum confidence score to accept a prediction (lower = more predictions, higher = more conservative)

## API Endpoints

### Train the Model

\`\`\`bash
POST /api/categorization/train
\`\`\`

Trains the ML model on all existing categorized transactions. Should be called:
- After importing historical data
- Periodically to incorporate new corrections
- When accuracy seems low

Example:
\`\`\`bash
curl -X POST http://localhost:8000/api/categorization/train
\`\`\`

Response:
\`\`\`json
{
  "success": true,
  "message": "ML model trained successfully",
  "stats": {
    "is_trained": true,
    "num_categories": 8,
    "total_samples": 127,
    "min_samples": 3
  }
}
\`\`\`

### Get Statistics

\`\`\`bash
GET /api/categorization/stats
\`\`\`

Returns current categorization system statistics.

Example:
\`\`\`bash
curl http://localhost:8000/api/categorization/stats
\`\`\`

Response:
\`\`\`json
{
  "rule_based": {
    "total_rules": 45,
    "average_confidence": 0.85
  },
  "machine_learning": {
    "is_trained": true,
    "num_categories": 8,
    "total_samples": 127,
    "min_samples": 3
  },
  "user_corrections": 23,
  "threshold": 0.7
}
\`\`\`

### Test Prediction

\`\`\`bash
POST /api/categorization/predict?description=coffee%20at%20starbucks
\`\`\`

Tests category prediction for a description.

## Usage Flow

### Initial Setup

1. **Create transactions** via Telegram bot or API
2. **Manually categorize** at least 3 transactions per category
3. **Train the model** using `/api/categorization/train`
4. **Verify stats** to ensure model is trained

### Ongoing Operation

1. User sends transaction via Telegram
2. Engine predicts category automatically
3. User reviews in dashboard
4. If incorrect, user corrects the category
5. System learns from the correction
6. Future similar transactions categorized correctly

## Improving Accuracy

### Tips for Better Results

1. **Consistent Descriptions**
   - Use similar wording for similar expenses
   - "Coffee at Starbucks" vs "starbucks coffee" - both work
   - More descriptive = better categorization

2. **Training Data Quality**
   - Aim for 10+ transactions per category
   - Correct obvious mistakes promptly
   - Regular retraining helps

3. **Category Design**
   - Don't create too many categories (stick to 5-10)
   - Make categories distinct
   - Avoid overlapping categories

4. **Threshold Tuning**
   - Lower threshold (0.5-0.6): More auto-categorization, less accuracy
   - Higher threshold (0.7-0.8): Fewer predictions, higher accuracy
   - Default 0.7 is a good balance

## Technical Details

### Text Preprocessing

Descriptions are normalized:
- Converted to lowercase
- Special characters removed
- Extra whitespace trimmed
- Stop words filtered (for ML)

### TF-IDF Features

- **Max features**: 100 (vocabulary size limit)
- **N-gram range**: (1, 2) (uses single words and pairs)
- **Stop words**: English (ignores common words like "the", "a")

### Similarity Calculation

- Uses cosine similarity for ML predictions
- Uses SequenceMatcher (Levenshteven) for rule-based
- Scores range from 0.0 (no match) to 1.0 (exact match)

### Model Persistence

- Models saved to `app/domain/ml/models/categorizer.pkl`
- Automatically loaded on service initialization
- Updated on every correction
- Includes vectorizer and category vectors

## Troubleshooting

### Model Not Training

**Problem**: `/train` endpoint returns "not enough data"

**Solution**:
- Ensure you have at least 3 transactions per category
- Check that transactions have `category_id` set
- Review statistics: `GET /api/categorization/stats`

### Low Accuracy

**Problem**: Many transactions categorized as "Other"

**Solutions**:
1. Lower the similarity threshold
2. Add more training data
3. Retrain the model
4. Use more descriptive transaction descriptions

### Inconsistent Results

**Problem**: Similar transactions get different categories

**Solutions**:
1. Retrain the model after corrections
2. Check for overlapping categories
3. Review and clean training data
4. Increase minimum samples per category

## Example Workflow

\`\`\`bash
# 1. Create some transactions
curl -X POST http://localhost:8000/api/transactions/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50,
    "description": "groceries at whole foods",
    "transaction_date": "2024-01-15T10:00:00",
    "category_id": 1
  }'

# 2. Add more transactions (repeat with different categories)

# 3. Train the model
curl -X POST http://localhost:8000/api/categorization/train

# 4. Check stats
curl http://localhost:8000/api/categorization/stats

# 5. Test prediction
curl -X POST "http://localhost:8000/api/categorization/predict?description=coffee"

# 6. Send transaction via Telegram (auto-categorized)
# Send message to bot: "5 coffee"
\`\`\`

## Performance

- **Training**: O(n * m) where n = transactions, m = features
- **Prediction**: O(k) where k = number of categories (typically < 10)
- **Memory**: ~1-5MB for typical model with 1000 transactions
- **Speed**: < 100ms for prediction on standard hardware

## Future Enhancements

Potential improvements:
- Multi-label classification (transaction can have multiple categories)
- Deep learning models for better accuracy
- User-specific models (personalized categorization)
- Automatic category suggestion based on spending patterns
- Budget alerts based on category spending
