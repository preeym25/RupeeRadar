"""Transaction cleaner service for normalizing descriptions."""

import re
from typing import Dict, Tuple


class TransactionCleaner:
    """Clean and normalize transaction descriptions."""
    
    @staticmethod
    def clean_description(description: str) -> str:
        """Clean and normalize transaction description.
        
        Args:
            description: Raw transaction description
            
        Returns:
            Cleaned description
        """
        if not description:
            return "Unknown"
        
        description = str(description)
        
        # Remove extra spaces
        description = ' '.join(description.split())
        
        # Remove special characters but keep meaningful ones
        description = re.sub(r'[^\w\s\-\.\@]', '', description)
        
        # Convert to title case
        description = description.title()
        
        # Limit length
        description = description[:500]
        
        return description if description else "Unknown"
    
    @staticmethod
    def extract_merchant(description: str) -> str:
        """Extract merchant name from description.
        
        Args:
            description: Cleaned transaction description
            
        Returns:
            Extracted merchant name
        """
        if not description:
            return "Unknown"
        
        # Common patterns for merchant names
        patterns = [
            r'^([A-Z][A-Za-z0-9\s\-\.]+?)(?:\s+(?:online|store|payment|transfer))?$',
            r'(?:at|@|via)\s+([A-Z][A-Za-z0-9\s\-\.]+)',
            r'([A-Z][A-Za-z0-9\s\-\.]+)\s+(?:online|store|payment)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                merchant = match.group(1).strip()
                if merchant and len(merchant) > 1:
                    return merchant
        
        # Fallback: use first few words
        words = description.split()
        if len(words) > 0:
            return ' '.join(words[:3])
        
        return description
    
    @staticmethod
    def standardize_amount(amount: float) -> float:
        """Standardize amount to positive value.
        
        Args:
            amount: Transaction amount (can be positive or negative)
            
        Returns:
            Absolute amount value
        """
        try:
            return abs(float(amount))
        except:
            return 0.0
    
    @staticmethod
    def detect_transaction_type(amount: float) -> str:
        """Detect if transaction is credit or debit.
        
        Args:
            amount: Transaction amount
            
        Returns:
            'CREDIT' or 'DEBIT'
        """
        try:
            return 'DEBIT' if float(amount) < 0 else 'CREDIT'
        except:
            return 'DEBIT'
    
    @staticmethod
    def clean_transaction(transaction: Dict) -> Dict:
        """Clean entire transaction object.
        
        Args:
            transaction: Raw transaction dictionary
            
        Returns:
            Cleaned transaction dictionary
        """
        description = transaction.get('description', '')
        amount = transaction.get('amount', 0)
        
        cleaned = {
            **transaction,
            'cleaned_description': TransactionCleaner.clean_description(description),
            'merchant_name': TransactionCleaner.extract_merchant(
                TransactionCleaner.clean_description(description)
            ),
            'amount': TransactionCleaner.standardize_amount(amount),
            'type': TransactionCleaner.detect_transaction_type(amount)
        }
        
        return cleaned
    
    @staticmethod
    def remove_duplicates(transactions: list) -> list:
        """Remove duplicate transactions from list.
        
        Args:
            transactions: List of transactions
            
        Returns:
            List with duplicates removed
        """
        seen = set()
        unique = []
        
        for trans in transactions:
            # Create a signature for the transaction
            key = (
                str(trans.get('date')),
                str(trans.get('amount')),
                trans.get('cleaned_description', '')
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(trans)
        
        return unique
