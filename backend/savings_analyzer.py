"""
Savings Analyzer - Analyzes user spending patterns and suggests savings strategies
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SavingsGoal:
    """Represents a savings goal with target amount and timeframe"""
    target_amount: float
    months_to_save: int
    monthly_target: float
    
    def __post_init__(self):
        self.monthly_target = self.target_amount / self.months_to_save

@dataclass
class SpendingCategory:
    """Represents a spending category with current and suggested amounts"""
    category: str
    current_monthly: float
    suggested_monthly: float
    reduction_amount: float
    reduction_percentage: float
    priority: int  # 1 = highest priority for reduction

@dataclass
class SavingsAnalysis:
    """Complete savings analysis result"""
    goal: SavingsGoal
    current_monthly_income: float
    current_monthly_expenses: float
    current_monthly_savings: float
    can_achieve_goal: bool
    shortfall: float
    suggested_cuts: List[SpendingCategory]
    total_suggested_savings: float
    remaining_shortfall: float
    alternative_strategies: List[str]

class SavingsAnalyzer:
    """Analyzes spending patterns and suggests savings strategies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_spending_patterns(self, df: pd.DataFrame, amount_col: str, date_col: str) -> Dict[str, float]:
        """
        Analyze spending patterns over the last 3 months
        
        Args:
            df: DataFrame with transaction data
            amount_col: Column name for transaction amounts
            date_col: Column name for transaction dates
            
        Returns:
            Dictionary with category -> monthly average spending
        """
        try:
            # Convert date column to datetime
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=[date_col, amount_col])
            
            if len(df) == 0:
                return {}
            
            # Convert amount to numeric
            df[amount_col] = pd.to_numeric(
                df[amount_col].astype(str).str.replace('$', '').str.replace(',', ''), 
                errors='coerce'
            )
            
            # Get last 3 months of data
            end_date = df[date_col].max()
            start_date = end_date - pd.Timedelta(days=90)  # Approximately 3 months
            
            df_recent = df[df[date_col] >= start_date].copy()
            
            if len(df_recent) == 0:
                return {}
            
            # Separate income and expenses
            income_data = df_recent[df_recent[amount_col] > 0]
            expense_data = df_recent[df_recent[amount_col] < 0]
            
            # Calculate monthly averages
            monthly_income = income_data[amount_col].sum() / 3  # 3 months
            monthly_expenses = abs(expense_data[amount_col].sum()) / 3
            
            # Group expenses by category if available
            category_spending = {}
            if 'ml_category' in df_recent.columns:
                expense_categories = expense_data.groupby('ml_category')[amount_col].sum().abs() / 3
                category_spending = expense_categories.to_dict()
            
            # Add summary data
            category_spending['_total_income'] = monthly_income
            category_spending['_total_expenses'] = monthly_expenses
            category_spending['_net_savings'] = monthly_income - monthly_expenses
            
            return category_spending
            
        except Exception as e:
            self.logger.error(f"Error analyzing spending patterns: {e}")
            return {}
    
    def categorize_spending_priority(self, category: str, amount: float) -> int:
        """
        Categorize spending by priority for reduction (1 = highest priority)
        
        Args:
            category: Spending category name
            amount: Monthly spending amount
            
        Returns:
            Priority level (1-5, where 1 is highest priority for reduction)
        """
        # High priority for reduction (discretionary spending)
        high_priority = [
            'entertainment', 'dining', 'shopping', 'recreation', 'hobbies',
            'subscriptions', 'luxury', 'personal_care', 'clothing', 'travel'
        ]
        
        # Medium priority (somewhat discretionary)
        medium_priority = [
            'utilities', 'transportation', 'groceries', 'healthcare',
            'insurance', 'communication', 'education'
        ]
        
        # Low priority (essential spending)
        low_priority = [
            'rent', 'mortgage', 'debt_payment', 'savings', 'investment',
            'income', 'taxes', 'essential'
        ]
        
        category_lower = category.lower()
        
        # Check for high priority keywords
        for keyword in high_priority:
            if keyword in category_lower:
                return 1
        
        # Check for medium priority keywords
        for keyword in medium_priority:
            if keyword in category_lower:
                return 2
        
        # Check for low priority keywords
        for keyword in low_priority:
            if keyword in category_lower:
                return 3
        
        # Default based on amount (higher amounts get higher priority for reduction)
        if amount > 500:
            return 2
        elif amount > 200:
            return 3
        else:
            return 4
    
    def suggest_spending_cuts(self, spending_data: Dict[str, float], target_monthly_savings: float) -> List[SpendingCategory]:
        """
        Suggest specific spending cuts to reach target savings
        
        Args:
            spending_data: Dictionary of category -> monthly spending
            target_monthly_savings: Target monthly savings amount
            
        Returns:
            List of suggested spending cuts
        """
        suggestions = []
        
        # Filter out non-spending categories
        spending_categories = {k: v for k, v in spending_data.items() 
                             if not k.startswith('_') and v > 0}
        
        # Sort by priority and amount
        category_priorities = []
        for category, amount in spending_categories.items():
            priority = self.categorize_spending_priority(category, amount)
            category_priorities.append((category, amount, priority))
        
        # Sort by priority (ascending) then by amount (descending)
        category_priorities.sort(key=lambda x: (x[2], -x[1]))
        
        remaining_target = target_monthly_savings
        
        for category, current_amount, priority in category_priorities:
            if remaining_target <= 0:
                break
            
            # Calculate suggested reduction (10-50% based on priority)
            if priority == 1:  # High priority - can reduce more
                reduction_pct = min(0.5, remaining_target / current_amount)
            elif priority == 2:  # Medium priority
                reduction_pct = min(0.3, remaining_target / current_amount)
            elif priority == 3:  # Low priority
                reduction_pct = min(0.15, remaining_target / current_amount)
            else:  # Very low priority
                reduction_pct = min(0.1, remaining_target / current_amount)
            
            # Ensure we don't suggest more than needed
            reduction_pct = min(reduction_pct, 1.0)
            
            if reduction_pct > 0.05:  # Only suggest if reduction is meaningful (>5%)
                reduction_amount = current_amount * reduction_pct
                suggested_amount = current_amount - reduction_amount
                
                suggestions.append(SpendingCategory(
                    category=category,
                    current_monthly=current_amount,
                    suggested_monthly=suggested_amount,
                    reduction_amount=reduction_amount,
                    reduction_percentage=reduction_pct * 100,
                    priority=priority
                ))
                
                remaining_target -= reduction_amount
        
        return suggestions
    
    def generate_alternative_strategies(self, shortfall: float, months: int) -> List[str]:
        """
        Generate alternative strategies if spending cuts aren't enough
        
        Args:
            shortfall: Remaining shortfall after suggested cuts
            months: Number of months to save
            
        Returns:
            List of alternative strategy suggestions
        """
        strategies = []
        
        if shortfall > 0:
            monthly_shortfall = shortfall / months
            
            if monthly_shortfall > 1000:
                strategies.append("Consider increasing income through side hustles or freelance work")
                strategies.append("Look for higher-paying job opportunities")
            
            if monthly_shortfall > 500:
                strategies.append("Sell unused items or assets to generate one-time income")
                strategies.append("Consider temporary part-time work")
            
            if monthly_shortfall > 200:
                strategies.append("Extend the savings timeline to reduce monthly pressure")
                strategies.append("Look for ways to reduce fixed costs (utilities, insurance, etc.)")
            
            strategies.append("Consider a more aggressive investment strategy for existing savings")
            strategies.append("Look for government assistance programs or tax benefits")
        
        return strategies
    
    def analyze_savings_goal(self, df: pd.DataFrame, amount_col: str, date_col: str, 
                           target_amount: float, months: int) -> SavingsAnalysis:
        """
        Complete savings goal analysis
        
        Args:
            df: DataFrame with transaction data
            amount_col: Column name for transaction amounts
            date_col: Column name for transaction dates
            target_amount: Target savings amount
            months: Number of months to save
            
        Returns:
            Complete savings analysis
        """
        try:
            # Create savings goal
            goal = SavingsGoal(target_amount, months, target_amount / months)
            
            # Analyze spending patterns
            spending_data = self.analyze_spending_patterns(df, amount_col, date_col)
            
            if not spending_data:
                            return SavingsAnalysis(
                goal=goal,
                current_monthly_income=0.0,
                current_monthly_expenses=0.0,
                current_monthly_savings=0.0,
                can_achieve_goal=False,
                shortfall=float(goal.monthly_target),
                suggested_cuts=[],
                total_suggested_savings=0.0,
                remaining_shortfall=float(goal.monthly_target),
                alternative_strategies=["Unable to analyze spending patterns - check data format"]
            )
            
            # Extract key metrics
            current_income = spending_data.get('_total_income', 0)
            current_expenses = spending_data.get('_total_expenses', 0)
            current_savings = spending_data.get('_net_savings', 0)
            
            # Check if goal is achievable
            can_achieve = current_savings >= goal.monthly_target
            shortfall = max(0, goal.monthly_target - current_savings)
            
            # Suggest spending cuts if needed
            suggested_cuts = []
            total_suggested_savings = 0
            remaining_shortfall = shortfall
            
            if shortfall > 0:
                suggested_cuts = self.suggest_spending_cuts(spending_data, shortfall)
                total_suggested_savings = sum(cut.reduction_amount for cut in suggested_cuts)
                remaining_shortfall = max(0, shortfall - total_suggested_savings)
            
            # Generate alternative strategies
            alternative_strategies = self.generate_alternative_strategies(remaining_shortfall, months)
            
            return SavingsAnalysis(
                goal=goal,
                current_monthly_income=float(current_income),
                current_monthly_expenses=float(current_expenses),
                current_monthly_savings=float(current_savings),
                can_achieve_goal=bool(can_achieve),
                shortfall=float(shortfall),
                suggested_cuts=suggested_cuts,
                total_suggested_savings=float(total_suggested_savings),
                remaining_shortfall=float(remaining_shortfall),
                alternative_strategies=alternative_strategies
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing savings goal: {e}")
            return SavingsAnalysis(
                goal=SavingsGoal(target_amount, months, target_amount / months),
                current_monthly_income=0.0,
                current_monthly_expenses=0.0,
                current_monthly_savings=0.0,
                can_achieve_goal=False,
                shortfall=float(target_amount / months),
                suggested_cuts=[],
                total_suggested_savings=0.0,
                remaining_shortfall=float(target_amount / months),
                alternative_strategies=[f"Error analyzing data: {str(e)}"]
            )

def create_savings_analysis_response(analysis: SavingsAnalysis) -> Dict:
    """
    Convert SavingsAnalysis to API response format
    
    Args:
        analysis: SavingsAnalysis object
        
    Returns:
        Dictionary formatted for API response
    """
    return {
        "goal": {
            "target_amount": float(analysis.goal.target_amount),
            "months_to_save": int(analysis.goal.months_to_save),
            "monthly_target": float(analysis.goal.monthly_target)
        },
        "current_financials": {
            "monthly_income": float(analysis.current_monthly_income),
            "monthly_expenses": float(analysis.current_monthly_expenses),
            "monthly_savings": float(analysis.current_monthly_savings)
        },
        "analysis": {
            "can_achieve_goal": bool(analysis.can_achieve_goal),
            "shortfall": float(analysis.shortfall),
            "total_suggested_savings": float(analysis.total_suggested_savings),
            "remaining_shortfall": float(analysis.remaining_shortfall)
        },
        "suggested_cuts": [
            {
                "category": str(cut.category),
                "current_monthly": float(cut.current_monthly),
                "suggested_monthly": float(cut.suggested_monthly),
                "reduction_amount": float(cut.reduction_amount),
                "reduction_percentage": float(cut.reduction_percentage),
                "priority": int(cut.priority)
            }
            for cut in analysis.suggested_cuts
        ],
        "alternative_strategies": [str(strategy) for strategy in analysis.alternative_strategies],
        "summary": {
            "total_categories_analyzed": int(len(analysis.suggested_cuts)),
            "high_priority_cuts": int(len([c for c in analysis.suggested_cuts if c.priority == 1])),
            "total_monthly_reduction": float(sum(cut.reduction_amount for cut in analysis.suggested_cuts)),
            "achievable_with_cuts": bool(analysis.remaining_shortfall <= 0)
        }
    }
