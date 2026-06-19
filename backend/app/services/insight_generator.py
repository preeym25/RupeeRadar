"""Insights generator service for financial analysis."""

from typing import List, Dict
import statistics


class InsightGenerator:
    """Generate personalized financial insights from transactions."""
    
    @staticmethod
    def generate_insights(
        transactions: List[Dict],
        recurring: List[Dict] = None
    ) -> List[Dict]:
        """Generate personalized financial insights.
        
        Args:
            transactions: List of all transactions
            recurring: List of recurring payment patterns
            
        Returns:
            List of insight dictionaries
        """
        if recurring is None:
            recurring = []
        
        insights = []
        
        # Calculate metrics
        total_income = sum([t.get('amount', 0) for t in transactions if t.get('type') == 'CREDIT'])
        total_spend = sum([t.get('amount', 0) for t in transactions if t.get('type') == 'DEBIT'])
        savings = total_income - total_spend
        
        if total_income == 0:
            return insights
        
        # Insight 1: Top spending category
        category_spend = {}
        for trans in transactions:
            if trans.get('type') == 'DEBIT':
                cat = trans.get('category', 'Other')
                category_spend[cat] = category_spend.get(cat, 0) + trans.get('amount', 0)
        
        if category_spend:
            top_category = max(category_spend, key=category_spend.get)
            top_amount = category_spend[top_category]
            top_percentage = (top_amount / total_spend) * 100 if total_spend > 0 else 0
            
            insights.append({
                'text': f"You spent ₹{top_amount:,.0f} on {top_category} - {top_percentage:.1f}% of your total spending",
                'type': 'spending_pattern',
                'metric': f"{top_percentage:.1f}%",
                'metric_unit': 'percentage',
                'priority': 'high' if top_percentage > 40 else 'medium',
                'is_actionable': True
            })
        
        # Insight 2: Recurring subscriptions and EMIs
        monthly_recurring = sum([
            r.get('avg_amount', 0) for r in recurring
            if r.get('frequency') == 'monthly'
        ])
        
        if monthly_recurring > 0:
            annual_recurring = monthly_recurring * 12
            insights.append({
                'text': f"You have ₹{monthly_recurring:,.0f}/month in recurring payments (₹{annual_recurring:,.0f}/year)",
                'type': 'recurring_cost',
                'metric': f"{annual_recurring:,.0f}",
                'metric_unit': 'currency',
                'priority': 'high',
                'is_actionable': True
            })
        
        # Insight 3: Savings rate
        savings_rate = (savings / total_income) * 100 if total_income > 0 else 0
        
        if savings_rate < 0:
            insights.append({
                'text': f"You spent ₹{abs(savings):,.0f} more than your income this month. Consider reviewing your expenses.",
                'type': 'deficit_alert',
                'metric': f"{abs(savings_rate):.1f}%",
                'metric_unit': 'percentage',
                'priority': 'critical',
                'is_actionable': True
            })
        elif savings_rate < 10:
            insights.append({
                'text': f"Your savings rate is {savings_rate:.1f}%. Try to increase savings by reviewing discretionary spending.",
                'type': 'low_savings',
                'metric': f"{savings_rate:.1f}%",
                'metric_unit': 'percentage',
                'priority': 'high',
                'is_actionable': True
            })
        else:
            insights.append({
                'text': f"Great! You saved {savings_rate:.1f}% of your income (₹{savings:,.0f}) this month.",
                'type': 'savings_rate',
                'metric': f"{savings_rate:.1f}%",
                'metric_unit': 'percentage',
                'priority': 'medium',
                'is_actionable': False
            })
        
        # Insight 4: Biggest transaction
        debit_transactions = [t for t in transactions if t.get('type') == 'DEBIT']
        if debit_transactions:
            biggest = max(debit_transactions, key=lambda x: x.get('amount', 0))
            date_str = biggest.get('date').strftime('%d %b') if hasattr(biggest.get('date'), 'strftime') else str(biggest.get('date'))
            
            insights.append({
                'text': f"Your biggest expense was ₹{biggest.get('amount', 0):,.0f} on {biggest.get('merchant_name', 'Unknown')} ({date_str})",
                'type': 'biggest_transaction',
                'metric': f"{biggest.get('amount', 0):,.0f}",
                'metric_unit': 'currency',
                'priority': 'medium',
                'is_actionable': False
            })
        
        # Insight 5: Unusual spending alert
        if debit_transactions and len(debit_transactions) > 3:
            all_amounts = [t.get('amount', 0) for t in debit_transactions]
            
            try:
                mean = statistics.mean(all_amounts)
                stdev = statistics.stdev(all_amounts)
                threshold = mean + (2 * stdev)
                
                unusual = [t for t in debit_transactions if t.get('amount', 0) > threshold]
                
                if unusual:
                    insights.append({
                        'text': f"You had {len(unusual)} unusually large transaction(s) this period (₹{threshold:,.0f}+)",
                        'type': 'unusual_spending',
                        'metric': f"{len(unusual)}",
                        'metric_unit': 'count',
                        'priority': 'medium',
                        'is_actionable': True
                    })
            except:
                pass
        
        # Insight 6: Category distribution
        if len(category_spend) > 1:
            second_category = sorted(category_spend.items(), key=lambda x: x[1], reverse=True)[1]
            insights.append({
                'text': f"Your second highest spending is {second_category[0]} at ₹{second_category[1]:,.0f}",
                'type': 'category_distribution',
                'metric': f"{second_category[1]:,.0f}",
                'metric_unit': 'currency',
                'priority': 'low',
                'is_actionable': False
            })
        
        # Return top 5 insights sorted by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        insights.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 4))
        
        return insights[:5]
    
    @staticmethod
    def generate_spending_summary(transactions: List[Dict]) -> Dict:
        """Generate spending summary.
        
        Args:
            transactions: List of transactions
            
        Returns:
            Summary dictionary
        """
        total_income = sum([t.get('amount', 0) for t in transactions if t.get('type') == 'CREDIT'])
        total_spend = sum([t.get('amount', 0) for t in transactions if t.get('type') == 'DEBIT'])
        savings = total_income - total_spend
        
        # Category breakdown
        category_spend = {}
        for trans in transactions:
            if trans.get('type') == 'DEBIT':
                cat = trans.get('category', 'Other')
                category_spend[cat] = category_spend.get(cat, 0) + trans.get('amount', 0)
        
        return {
            'total_income': total_income,
            'total_spend': total_spend,
            'savings': savings,
            'savings_rate': (savings / total_income * 100) if total_income > 0 else 0,
            'category_breakdown': category_spend,
            'transaction_count': len(transactions),
            'income_count': sum(1 for t in transactions if t.get('type') == 'CREDIT'),
            'debit_count': sum(1 for t in transactions if t.get('type') == 'DEBIT')
        }
