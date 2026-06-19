"""Recurring payment detection service."""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import statistics


class RecurringDetector:
    """Detect recurring payment patterns in transactions."""
    
    @staticmethod
    def detect_recurring(transactions: List[Dict]) -> List[Dict]:
        """Detect recurring payment patterns.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of recurring pattern dictionaries
        """
        recurring = []
        
        # Group transactions by merchant and amount
        merchant_groups = {}
        
        for trans in sorted(transactions, key=lambda x: x['date']):
            merchant = trans.get('merchant_name', 'Unknown')
            amount = round(trans.get('amount', 0), 2)
            
            key = f"{merchant}_{amount}"
            
            if key not in merchant_groups:
                merchant_groups[key] = []
            
            merchant_groups[key].append(trans)
        
        # Analyze groups for recurrence
        for key, group in merchant_groups.items():
            if len(group) >= 3:  # Minimum 3 occurrences
                is_recurring, frequency, confidence = RecurringDetector._analyze_frequency(group)
                
                if is_recurring:
                    pattern = {
                        'merchant_name': group[0].get('merchant_name'),
                        'category': group[0].get('category'),
                        'frequency': frequency,
                        'avg_amount': statistics.mean([t.get('amount', 0) for t in group]),
                        'last_occurrence': max([t.get('date') for t in group]),
                        'occurrences_count': len(group),
                        'confidence_score': confidence,
                        'transaction_ids': [t.get('id') for t in group if t.get('id')]
                    }
                    recurring.append(pattern)
        
        return recurring
    
    @staticmethod
    def _analyze_frequency(transactions: List[Dict]) -> Tuple[bool, str, float]:
        """Analyze frequency of transaction occurrences.
        
        Args:
            transactions: List of transactions for same merchant/amount
            
        Returns:
            Tuple of (is_recurring, frequency, confidence_score)
        """
        dates = sorted([t.get('date') for t in transactions if t.get('date')])
        
        if len(dates) < 2:
            return False, 'Unknown', 0.0
        
        # Calculate intervals in days
        intervals = []
        for i in range(1, len(dates)):
            delta = (dates[i] - dates[i-1]).days
            intervals.append(delta)
        
        avg_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
        
        # Determine frequency based on average interval
        if 1 <= avg_interval <= 3:
            frequency = 'daily'
            expected_std = 0.5
        elif 4 <= avg_interval <= 10:
            frequency = 'weekly'
            expected_std = 2
        elif 20 <= avg_interval <= 35:
            frequency = 'monthly'
            expected_std = 5
        elif 85 <= avg_interval <= 100:
            frequency = 'quarterly'
            expected_std = 10
        elif 350 <= avg_interval <= 370:
            frequency = 'yearly'
            expected_std = 20
        else:
            return False, 'irregular', 0.0
        
        # Calculate confidence (lower std = higher confidence)
        # Allow some variance around expected
        variance_ratio = std_interval / avg_interval if avg_interval > 0 else 0
        
        # High variance tolerance (up to 30% is acceptable)
        if variance_ratio > 0.3:
            confidence = max(0, 1 - (variance_ratio / 0.3) * 0.5)
        else:
            confidence = 1 - (variance_ratio / 0.3) * 0.5
        
        # Require minimum confidence
        is_recurring = confidence > 0.4
        
        return is_recurring, frequency, confidence
    
    @staticmethod
    def detect_with_amount_variation(
        transactions: List[Dict],
        tolerance: float = 0.15
    ) -> List[Dict]:
        """Detect recurring payments allowing for amount variations.
        
        Args:
            transactions: List of transactions
            tolerance: Amount variation tolerance (0.15 = 15%)
            
        Returns:
            List of recurring patterns allowing amount variance
        """
        recurring = []
        
        # Group by merchant only (not amount)
        merchant_groups = {}
        
        for trans in sorted(transactions, key=lambda x: x['date']):
            merchant = trans.get('merchant_name', 'Unknown')
            
            if merchant not in merchant_groups:
                merchant_groups[merchant] = []
            
            merchant_groups[merchant].append(trans)
        
        # Analyze groups
        for merchant, group in merchant_groups.items():
            if len(group) >= 3:
                amounts = [t.get('amount', 0) for t in group]
                avg_amount = statistics.mean(amounts)
                
                # Check if amounts vary within tolerance
                variations = [abs(a - avg_amount) / avg_amount for a in amounts if avg_amount > 0]
                max_variation = max(variations) if variations else 0
                
                if max_variation <= tolerance:
                    # Likely recurring
                    is_recurring, frequency, confidence = RecurringDetector._analyze_frequency(group)
                    
                    if is_recurring:
                        pattern = {
                            'merchant_name': merchant,
                            'category': group[0].get('category'),
                            'frequency': frequency,
                            'avg_amount': avg_amount,
                            'amount_variation': max_variation,
                            'last_occurrence': max([t.get('date') for t in group]),
                            'occurrences_count': len(group),
                            'confidence_score': confidence
                        }
                        recurring.append(pattern)
        
        return recurring
    
    @staticmethod
    def detect_with_gaps(
        transactions: List[Dict],
        max_gap_months: int = 2
    ) -> List[Dict]:
        """Detect recurring payments allowing for missing months.
        
        Args:
            transactions: List of transactions
            max_gap_months: Maximum allowed gap in months
            
        Returns:
            List of recurring patterns with gap information
        """
        recurring = []
        
        # Group by merchant and amount
        merchant_groups = {}
        
        for trans in sorted(transactions, key=lambda x: x['date']):
            merchant = trans.get('merchant_name', 'Unknown')
            amount = round(trans.get('amount', 0), 2)
            key = f"{merchant}_{amount}"
            
            if key not in merchant_groups:
                merchant_groups[key] = []
            
            merchant_groups[key].append(trans)
        
        # Analyze with gap tolerance
        for key, group in merchant_groups.items():
            if len(group) >= 3:
                dates = sorted([t.get('date') for t in group])
                intervals = []
                gaps = []
                
                for i in range(1, len(dates)):
                    delta_months = (dates[i].year - dates[i-1].year) * 12 + \
                                   (dates[i].month - dates[i-1].month)
                    intervals.append(delta_months)
                    
                    if delta_months > max_gap_months:
                        gaps.append({'from': dates[i-1], 'to': dates[i]})
                
                # Check if excluding gap transactions shows clear pattern
                if gaps and len(intervals) >= 3:
                    normal_intervals = [i for i in intervals if i <= max_gap_months]
                    avg_interval = statistics.mean(normal_intervals) if normal_intervals else 0
                    
                    pattern = {
                        'merchant_name': group[0].get('merchant_name'),
                        'category': group[0].get('category'),
                        'avg_interval_months': avg_interval,
                        'gaps_detected': len(gaps),
                        'last_occurrence': max(dates),
                        'occurrences_count': len(group),
                        'confidence_score': 0.7,  # Lower confidence due to gaps
                        'status': 'paused' if gaps else 'active'
                    }
                    recurring.append(pattern)
        
        return recurring
