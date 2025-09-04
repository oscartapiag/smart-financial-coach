"""
Financial Priority Tool - Guides users through structured financial priorities
Uses the discretionary income API to provide specific spending recommendations
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class FinancialPriority:
    """Represents a financial priority with current status and recommendations"""
    priority: int
    name: str
    description: str
    current_amount: float
    target_amount: float
    monthly_allocation: float
    months_to_complete: float
    status: str  # "not_started", "in_progress", "completed"
    recommendations: List[str]

@dataclass
class FinancialPlan:
    """Complete financial plan with all priorities and allocations"""
    discretionary_income: float
    six_month_expenses: float
    monthly_expenses: float
    priorities: List[FinancialPriority]
    total_allocated: float
    remaining_discretionary: float
    plan_summary: Dict

class FinancialPriorityTool:
    """Tool for creating and managing financial priority plans"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
    
    def get_discretionary_income(self, file_id: str) -> Dict:
        """Get discretionary income data from the API"""
        try:
            url = f"{self.base_url}/files/{file_id}/discretionary-income"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to get discretionary income: {response.status_code}")
                return {}
        except Exception as e:
            self.logger.error(f"Error getting discretionary income: {e}")
            return {}
    
    def ask_credit_card_debt_questions(self) -> Dict:
        """Ask questions about credit card debt"""
        print("\n💳 CREDIT CARD DEBT ANALYSIS")
        print("=" * 50)
        print("Priority 1: Pay off credit card debt as fast as possible")
        print("Credit card debt typically has 15-25% APR, making it the highest priority.")
        
        questions = {
            "total_debt": "What is your total credit card debt? ($)",
            "highest_apr": "What is your highest credit card APR? (%)",
            "minimum_payments": "What are your total minimum monthly payments? ($)",
            "debt_accounts": "How many credit card accounts do you have?"
        }
        
        answers = {}
        for key, question in questions.items():
            while True:
                try:
                    if key == "highest_apr":
                        value = float(input(f"\n{question}: ").replace('%', ''))
                    else:
                        value = float(input(f"\n{question}: ").replace('$', '').replace(',', ''))
                    answers[key] = value
                    break
                except ValueError:
                    print("Please enter a valid number.")
        
        return answers
    
    def ask_emergency_fund_questions(self, six_month_expenses: float) -> Dict:
        """Ask questions about emergency fund"""
        print(f"\n💰 EMERGENCY FUND ANALYSIS")
        print("=" * 50)
        print("Priority 2: Build emergency fund to cover 6 months of expenses")
        print(f"Based on your spending, you need: ${six_month_expenses:,.2f}")
        
        questions = {
            "current_emergency_fund": "How much do you currently have in your emergency fund? ($)",
            "target_emergency_fund": f"Target emergency fund (6 months expenses): ${six_month_expenses:,.2f}"
        }
        
        answers = {}
        answers["target_emergency_fund"] = six_month_expenses
        
        while True:
            try:
                value = float(input(f"\n{questions['current_emergency_fund']}: ").replace('$', '').replace(',', ''))
                answers["current_emergency_fund"] = value
                break
            except ValueError:
                print("Please enter a valid number.")
        
        return answers
    
    def ask_retirement_match_questions(self) -> Dict:
        """Ask questions about retirement matching"""
        print(f"\n🏦 RETIREMENT MATCH ANALYSIS")
        print("=" * 50)
        print("Priority 3: Always invest enough to capture employer match")
        print("This is free money - never miss it!")
        
        questions = {
            "employer_match_percentage": "What percentage does your employer match? (%)",
            "match_limit": "What's the maximum percentage they'll match? (%)",
            "current_contribution": "What percentage are you currently contributing? (%)",
            "salary": "What is your annual salary? ($)"
        }
        
        answers = {}
        for key, question in questions.items():
            while True:
                try:
                    if key == "salary":
                        value = float(input(f"\n{question}: ").replace('$', '').replace(',', ''))
                    else:
                        value = float(input(f"\n{question}: ").replace('%', ''))
                    answers[key] = value
                    break
                except ValueError:
                    print("Please enter a valid number.")
        
        return answers
    
    def ask_investing_allocation_questions(self) -> Dict:
        """Ask questions about investing allocation"""
        print(f"\n📈 INVESTING ALLOCATION ANALYSIS")
        print("=" * 50)
        print("Priority 4: 80% retirement/SPY, 20% HYSA or high-risk securities")
        print("This is for any remaining discretionary income after priorities 1-3")
        
        questions = {
            "risk_tolerance": "What's your risk tolerance? (1=Very Conservative, 5=Very Aggressive)",
            "investment_experience": "How experienced are you with investing? (1=Beginner, 5=Expert)",
            "preferred_retirement_account": "Do you prefer 401k, IRA, or both? (401k/IRA/both)",
            "hysa_rate": "What's your current HYSA interest rate? (%)"
        }
        
        answers = {}
        for key, question in questions.items():
            if key == "preferred_retirement_account":
                while True:
                    value = input(f"\n{question}: ").lower().strip()
                    if value in ['401k', 'ira', 'both']:
                        answers[key] = value
                        break
                    print("Please enter '401k', 'IRA', or 'both'")
            else:
                while True:
                    try:
                        if key == "hysa_rate":
                            value = float(input(f"\n{question}: ").replace('%', ''))
                        else:
                            value = float(input(f"\n{question}: "))
                        answers[key] = value
                        break
                    except ValueError:
                        print("Please enter a valid number.")
        
        return answers
    
    def calculate_credit_card_plan(self, debt_info: Dict, discretionary_income: float) -> FinancialPriority:
        """Calculate credit card debt payoff plan"""
        total_debt = debt_info["total_debt"]
        highest_apr = debt_info["highest_apr"]
        minimum_payments = debt_info["minimum_payments"]
        
        # Calculate aggressive payoff (use most of discretionary income)
        aggressive_payment = min(discretionary_income * 0.8, total_debt)
        monthly_payment = minimum_payments + aggressive_payment
        
        # Calculate payoff time (simplified calculation)
        if monthly_payment > total_debt:
            months_to_payoff = 1
        else:
            # Rough calculation: debt / monthly_payment
            months_to_payoff = total_debt / monthly_payment
        
        recommendations = [
            f"Pay ${monthly_payment:,.2f} monthly (${minimum_payments:,.2f} minimum + ${aggressive_payment:,.2f} extra)",
            f"Focus on highest APR card first ({highest_apr}%)",
            f"Consider balance transfer to lower APR if possible",
            f"Cut up cards and use cash/debit only during payoff"
        ]
        
        if months_to_payoff > 12:
            recommendations.append("Consider debt consolidation loan if APR is lower")
        
        return FinancialPriority(
            priority=1,
            name="Credit Card Debt Payoff",
            description=f"Pay off ${total_debt:,.2f} in credit card debt",
            current_amount=total_debt,
            target_amount=0,
            monthly_allocation=monthly_payment,
            months_to_complete=months_to_payoff,
            status="in_progress" if total_debt > 0 else "completed",
            recommendations=recommendations
        )
    
    def calculate_emergency_fund_plan(self, fund_info: Dict, discretionary_income: float) -> FinancialPriority:
        """Calculate emergency fund building plan"""
        current_fund = fund_info["current_emergency_fund"]
        target_fund = fund_info["target_emergency_fund"]
        needed = max(0, target_fund - current_fund)
        
        if needed <= 0:
            return FinancialPriority(
                priority=2,
                name="Emergency Fund",
                description="Emergency fund fully funded",
                current_amount=current_fund,
                target_amount=target_fund,
                monthly_allocation=0,
                months_to_complete=0,
                status="completed",
                recommendations=["Emergency fund is fully funded! Great job!"]
            )
        
        # Allocate remaining discretionary income after credit card payments
        monthly_allocation = min(discretionary_income * 0.6, needed / 12)  # Aim for 12 months
        months_to_complete = needed / monthly_allocation if monthly_allocation > 0 else float('inf')
        
        recommendations = [
            f"Save ${monthly_allocation:,.2f} monthly to emergency fund",
            f"Keep in high-yield savings account (HYSA) for easy access",
            f"Only use for true emergencies (job loss, medical, major repairs)",
            f"Consider 3-month target first, then build to 6 months"
        ]
        
        return FinancialPriority(
            priority=2,
            name="Emergency Fund",
            description=f"Build emergency fund to ${target_fund:,.2f}",
            current_amount=current_fund,
            target_amount=target_fund,
            monthly_allocation=monthly_allocation,
            months_to_complete=months_to_complete,
            status="in_progress",
            recommendations=recommendations
        )
    
    def calculate_retirement_match_plan(self, retirement_info: Dict, discretionary_income: float) -> FinancialPriority:
        """Calculate retirement matching plan"""
        match_percentage = retirement_info["employer_match_percentage"]
        match_limit = retirement_info["match_limit"]
        current_contribution = retirement_info["current_contribution"]
        salary = retirement_info["salary"]
        
        # Calculate required contribution to get full match
        required_contribution = min(match_limit, match_percentage)
        monthly_required = (salary / 12) * (required_contribution / 100)
        
        # Calculate if they're already getting full match
        if current_contribution >= required_contribution:
            return FinancialPriority(
                priority=3,
                name="Retirement Match",
                description="Already getting full employer match",
                current_amount=current_contribution,
                target_amount=required_contribution,
                monthly_allocation=0,
                months_to_complete=0,
                status="completed",
                recommendations=["You're already getting the full employer match! Great job!"]
            )
        
        # Calculate additional contribution needed
        additional_contribution = required_contribution - current_contribution
        monthly_additional = (salary / 12) * (additional_contribution / 100)
        
        recommendations = [
            f"Increase contribution by {additional_contribution:.1f}% to get full match",
            f"This requires ${monthly_additional:,.2f} additional monthly contribution",
            f"Employer will match ${monthly_required:,.2f} monthly (free money!)",
            f"Total monthly retirement contribution: ${monthly_required:,.2f}"
        ]
        
        return FinancialPriority(
            priority=3,
            name="Retirement Match",
            description=f"Get full employer match ({required_contribution}%)",
            current_amount=current_contribution,
            target_amount=required_contribution,
            monthly_allocation=monthly_additional,
            months_to_complete=1,  # Can start immediately
            status="in_progress",
            recommendations=recommendations
        )
    
    def calculate_investing_allocation_plan(self, investing_info: Dict, remaining_discretionary: float) -> FinancialPriority:
        """Calculate investing allocation plan"""
        risk_tolerance = investing_info["risk_tolerance"]
        investment_experience = investing_info["investment_experience"]
        preferred_account = investing_info["preferred_retirement_account"]
        hysa_rate = investing_info["hysa_rate"]
        
        # Calculate 80/20 split
        retirement_allocation = remaining_discretionary * 0.8
        hysa_allocation = remaining_discretionary * 0.2
        
        recommendations = [
            f"Invest ${retirement_allocation:,.2f} monthly in retirement accounts",
            f"Save ${hysa_allocation:,.2f} monthly in HYSA (current rate: {hysa_rate}%)",
            f"Retirement split: 70% SPY/Total Market, 30% Bonds (age-appropriate)",
            f"HYSA for short-term goals or emergency fund overflow"
        ]
        
        if risk_tolerance >= 4 and investment_experience >= 3:
            recommendations.append("Consider 10% allocation to high-risk securities (crypto, individual stocks)")
        
        if preferred_account == "401k":
            recommendations.append("Maximize 401k contributions first, then IRA")
        elif preferred_account == "ira":
            recommendations.append("Focus on IRA contributions, consider Roth vs Traditional")
        else:
            recommendations.append("Balance between 401k and IRA based on tax situation")
        
        return FinancialPriority(
            priority=4,
            name="Investing Allocation",
            description="80% retirement/SPY, 20% HYSA",
            current_amount=0,
            target_amount=remaining_discretionary,
            monthly_allocation=remaining_discretionary,
            months_to_complete=float('inf'),  # Ongoing
            status="in_progress",
            recommendations=recommendations
        )
    
    def create_financial_plan(self, file_id: str) -> FinancialPlan:
        """Create a complete financial plan based on user input and discretionary income"""
        print("🎯 FINANCIAL PRIORITY PLANNER")
        print("=" * 60)
        print("Let's create a personalized financial plan based on your spending patterns!")
        
        # Get discretionary income data
        print("\n📊 Analyzing your spending patterns...")
        discretionary_data = self.get_discretionary_income(file_id)
        
        if not discretionary_data:
            print("❌ Could not analyze your spending patterns. Please check your file ID.")
            return None
        
        monthly_discretionary = discretionary_data.get("monthly_discretionary_income", 0)
        six_month_expenses = discretionary_data.get("six_month_expenses", 0)
        monthly_expenses = discretionary_data.get("monthly_expenses", 0)
        
        print(f"✅ Analysis complete!")
        print(f"   Monthly Discretionary Income: ${monthly_discretionary:,.2f}")
        print(f"   6-Month Expenses: ${six_month_expenses:,.2f}")
        print(f"   Monthly Expenses: ${monthly_expenses:,.2f}")
        
        # Ask questions for each priority
        debt_info = self.ask_credit_card_debt_questions()
        emergency_info = self.ask_emergency_fund_questions(six_month_expenses)
        retirement_info = self.ask_retirement_match_questions()
        investing_info = self.ask_investing_allocation_questions()
        
        # Calculate plans for each priority
        print("\n🔄 Calculating your personalized financial plan...")
        
        debt_plan = self.calculate_credit_card_plan(debt_info, monthly_discretionary)
        emergency_plan = self.calculate_emergency_fund_plan(emergency_info, monthly_discretionary)
        retirement_plan = self.calculate_retirement_match_plan(retirement_info, monthly_discretionary)
        
        # Calculate remaining discretionary income after priorities 1-3
        remaining_after_debt = monthly_discretionary - debt_plan.monthly_allocation
        remaining_after_emergency = remaining_after_debt - emergency_plan.monthly_allocation
        remaining_after_retirement = remaining_after_emergency - retirement_plan.monthly_allocation
        
        investing_plan = self.calculate_investing_allocation_plan(investing_info, remaining_after_retirement)
        
        # Create priorities list
        priorities = [debt_plan, emergency_plan, retirement_plan, investing_plan]
        
        # Calculate totals
        total_allocated = sum(p.monthly_allocation for p in priorities)
        remaining_discretionary = monthly_discretionary - total_allocated
        
        # Create plan summary
        plan_summary = {
            "total_discretionary_income": monthly_discretionary,
            "total_allocated": total_allocated,
            "remaining_after_plan": remaining_discretionary,
            "debt_payoff_months": debt_plan.months_to_complete,
            "emergency_fund_months": emergency_plan.months_to_complete,
            "retirement_match_immediate": retirement_plan.months_to_complete == 1
        }
        
        return FinancialPlan(
            discretionary_income=monthly_discretionary,
            six_month_expenses=six_month_expenses,
            monthly_expenses=monthly_expenses,
            priorities=priorities,
            total_allocated=total_allocated,
            remaining_discretionary=remaining_discretionary,
            plan_summary=plan_summary
        )
    
    def display_financial_plan(self, plan: FinancialPlan):
        """Display the complete financial plan"""
        print("\n🎯 YOUR PERSONALIZED FINANCIAL PLAN")
        print("=" * 60)
        
        print(f"\n📊 FINANCIAL OVERVIEW:")
        print(f"   Monthly Discretionary Income: ${plan.discretionary_income:,.2f}")
        print(f"   Total Allocated: ${plan.total_allocated:,.2f}")
        print(f"   Remaining After Plan: ${plan.remaining_discretionary:,.2f}")
        
        for priority in plan.priorities:
            print(f"\n{priority.priority}. {priority.name.upper()}")
            print("-" * 40)
            print(f"   Description: {priority.description}")
            print(f"   Monthly Allocation: ${priority.monthly_allocation:,.2f}")
            print(f"   Status: {priority.status.replace('_', ' ').title()}")
            
            if priority.months_to_complete != float('inf') and priority.months_to_complete > 0:
                print(f"   Time to Complete: {priority.months_to_complete:.1f} months")
            
            print(f"\n   Recommendations:")
            for i, rec in enumerate(priority.recommendations, 1):
                print(f"   {i}. {rec}")
        
        print(f"\n💡 NEXT STEPS:")
        print("1. Start with Priority 1 (Credit Card Debt) immediately")
        print("2. Set up automatic transfers for each priority")
        print("3. Review and adjust monthly as your situation changes")
        print("4. Celebrate small wins along the way!")
        
        if plan.remaining_discretionary > 0:
            print(f"\n🎉 BONUS: You have ${plan.remaining_discretionary:,.2f} left over!")
            print("   Consider: Additional emergency fund, vacation fund, or extra debt payments")
        elif plan.remaining_discretionary < 0:
            print(f"\n⚠️  WARNING: Plan exceeds discretionary income by ${abs(plan.remaining_discretionary):,.2f}")
            print("   Consider: Reducing allocations or increasing income")

def create_financial_priority_response(plan: FinancialPlan) -> Dict:
    """Convert FinancialPlan to API response format"""
    return {
        "financial_overview": {
            "monthly_discretionary_income": plan.discretionary_income,
            "six_month_expenses": plan.six_month_expenses,
            "monthly_expenses": plan.monthly_expenses,
            "total_allocated": plan.total_allocated,
            "remaining_after_plan": plan.remaining_discretionary
        },
        "priorities": [
            {
                "priority": p.priority,
                "name": p.name,
                "description": p.description,
                "current_amount": p.current_amount,
                "target_amount": p.target_amount,
                "monthly_allocation": p.monthly_allocation,
                "months_to_complete": p.months_to_complete,
                "status": p.status,
                "recommendations": p.recommendations
            }
            for p in plan.priorities
        ],
        "plan_summary": plan.plan_summary,
        "next_steps": [
            "Start with Priority 1 (Credit Card Debt) immediately",
            "Set up automatic transfers for each priority",
            "Review and adjust monthly as your situation changes",
            "Celebrate small wins along the way!"
        ]
    }
