"""Transaction categorization service with multi-layer approach."""

import re
from typing import Tuple, Dict
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


class TransactionCategorizer:
    """Categorize transactions using multi-layer approach (rule-based + ML)."""
    
    MERCHANT_PATTERNS = {
        'Food': [
            r'restaurant|cafe|coffee|pizza|burger|food|swiggy|zomato|dominos|dunkin|subway|mcd|mcdonalds',
            r'bakery|bakehouse|dining|dine|food court|cloud kitchen'
        ],
        'Travel': [
            r'uber|ola|taxi|cab|bus|flight|railway|train|travel|hotel|airbnb|booking',
            r'airfare|transit|transport|parking|fuel|petrol|gas station'
        ],
        'Shopping': [
            r'amazon|flipkart|myntra|ebay|shop|mall|store|retail|shopping|clothes|clothing',
            r'apparels|fashion|market|bazaar|mall'
        ],
        'Bills': [
            r'electricity|water|gas|broadband|internet|bill|utility|phone|mobile|recharge',
            r'telecom|isp|postpaid|electricity bill|water bill'
        ],
        'Subscriptions': [
            r'netflix|spotify|prime|subscription|monthly|premium|app store|play store',
            r'youtube|aws|cloud|subscription fee|membership'
        ],
        'Investments': [
            r'mutual|sip|investment|broker|trading|stock|share|nse|bse|demat',
            r'investment fund|portfolio|trading platform'
        ],
        'Rent': [
            r'rent|landlord|lease|housing|apartment|flatmate|deposit',
            r'rental|accommodation'
        ],
        'Salary': [
            r'salary|wages|income|bonus|earning|payroll|compensation',
            r'stipend|fellowship|grant'
        ],
        'EMI': [
            r'emi|loan|credit|repayment|installment|mortgage|home loan',
            r'personal loan|auto loan|vehicle loan'
        ],
        'Other': []
    }
    
    ML_MODEL = None
    
    @staticmethod
    def rule_based_categorize(description: str) -> Tuple[str, float]:
        """Layer 1: Rule-based categorization using regex patterns.
        
        Args:
            description: Cleaned transaction description
            
        Returns:
            Tuple of (category, confidence)
        """
        description = description.lower()
        
        for category, patterns in TransactionCategorizer.MERCHANT_PATTERNS.items():
            if category == 'Other':
                continue
            
            for pattern in patterns:
                if re.search(pattern, description):
                    return category, 0.9  # High confidence for rule matches
        
        return 'Other', 0.3
    
    @staticmethod
    def ml_categorize(description: str, model=None) -> Tuple[str, float]:
        """Layer 2: ML-based categorization using trained model.
        
        Args:
            description: Cleaned transaction description
            model: Trained ML model (optional)
            
        Returns:
            Tuple of (category, confidence)
        """
        if model is None:
            # Fallback to rule-based if no model available
            return TransactionCategorizer.rule_based_categorize(description)
        
        try:
            # Use model prediction
            prediction = model.predict([description])[0]
            confidence = max(model.predict_proba([description])[0])
            
            return prediction, confidence
        except:
            # Fall back to rule-based if model fails
            return TransactionCategorizer.rule_based_categorize(description)
    
    @staticmethod
    def categorize_transaction(transaction: Dict, model=None) -> Dict:
        """Categorize single transaction using multi-layer approach.
        
        Args:
            transaction: Transaction dictionary
            model: Optional trained ML model
            
        Returns:
            Transaction with category and confidence
        """
        description = transaction.get('cleaned_description', '')
        
        # Try rule-based first (Layer 1)
        category, confidence = TransactionCategorizer.rule_based_categorize(description)
        
        # If confidence is low and model available, try ML (Layer 2)
        if confidence < 0.7 and model:
            ml_category, ml_confidence = TransactionCategorizer.ml_categorize(
                description, model
            )
            if ml_confidence > confidence:
                category, confidence = ml_category, ml_confidence
        
        transaction['category'] = category
        transaction['category_confidence'] = confidence
        
        return transaction
    
    @staticmethod
    def categorize_batch(transactions: list, model=None) -> list:
        """Categorize multiple transactions.
        
        Args:
            transactions: List of transaction dictionaries
            model: Optional trained ML model
            
        Returns:
            List of categorized transactions
        """
        return [
            TransactionCategorizer.categorize_transaction(t, model)
            for t in transactions
        ]
    
    @staticmethod
    def train_model(training_data: list, labels: list):
        """Train ML model from user data.
        
        Args:
            training_data: List of descriptions
            labels: List of corresponding categories
            
        Returns:
            Trained sklearn pipeline
        """
        if len(training_data) < 10:
            # Not enough data to train
            return None
        
        try:
            pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=1000, lowercase=True)),
                ('classifier', MultinomialNB())
            ])
            
            pipeline.fit(training_data, labels)
            TransactionCategorizer.ML_MODEL = pipeline
            
            return pipeline
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return None
    
    @staticmethod
    def get_model():
        """Get the trained ML model."""
        return TransactionCategorizer.ML_MODEL
    
    @staticmethod
    def set_model(model):
        """Set a pre-trained ML model."""
        TransactionCategorizer.ML_MODEL = model
