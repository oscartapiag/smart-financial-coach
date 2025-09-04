#!/usr/bin/env python3
"""
Test script for financial priority tool functionality
"""

import requests
import json
import os

# Configuration: Change this to switch between different CSV files
CSV_FILES = {
    "balanced": "./trans_data_internal/sample_transactions_balanced.csv",
    "original": "./trans_data_internal/sample_transactions.csv"
}

# Set the default CSV file to use
DEFAULT_CSV = "balanced"  # Change this to "original" to use the other file

def test_upload_for_financial_priorities(csv_type=None):
    """Upload a file for financial priorities testing"""
    if csv_type is None:
        csv_type = DEFAULT_CSV
    
    if csv_type not in CSV_FILES:
        print(f"❌ Unknown CSV type: {csv_type}. Available: {list(CSV_FILES.keys())}")
        return None
    
    csv_path = CSV_FILES[csv_type]
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return None
    
    url = "http://localhost:8000/upload-transactions"
    
    print(f"📁 Uploading CSV file for financial priorities: {csv_path}")
    
    with open(csv_path, "rb") as f:
        files = {"file": (csv_path, f, "text/csv")}
        
        try:
            response = requests.post(url, files=files)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Upload successful! File ID: {data['file_id']}")
                return data['file_id']
            else:
                print(f"❌ Upload failed: {response.status_code}")
                return None
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server")
            return None

def test_financial_priorities(file_id):
    """Test financial priorities creation for a specific file"""
    if not file_id:
        print("❌ No file ID provided for financial priorities")
        return False
        
    url = f"http://localhost:8000/files/{file_id}/financial-priorities"
    
    # Sample financial data for testing
    financial_data = {
        "credit_card_debt": {
            "total_debt": 5000,
            "highest_apr": 22.99,
            "minimum_payments": 150,
            "debt_accounts": 3
        },
        "emergency_fund": {
            "current_emergency_fund": 1000
        },
        "retirement_match": {
            "employer_match_percentage": 4,
            "match_limit": 6,
            "current_contribution": 2,
            "salary": 60000
        },
        "investing_allocation": {
            "risk_tolerance": 3,
            "investment_experience": 2,
            "preferred_retirement_account": "401k",
            "hysa_rate": 4.5
        }
    }
    
    print(f"\n🎯 Testing Financial Priorities...")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=financial_data)
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Financial priorities created successfully!")
            
            # Display financial overview
            overview = data.get('financial_overview', {})
            print(f"\n📊 Financial Overview:")
            print(f"  Monthly Discretionary Income: ${overview.get('monthly_discretionary_income', 0):,.2f}")
            print(f"  Six Month Expenses: ${overview.get('six_month_expenses', 0):,.2f}")
            print(f"  Monthly Expenses: ${overview.get('monthly_expenses', 0):,.2f}")
            print(f"  Total Allocated: ${overview.get('total_allocated', 0):,.2f}")
            print(f"  Remaining After Plan: ${overview.get('remaining_after_plan', 0):,.2f}")
            
            # Display each priority
            priorities = data.get('priorities', [])
            for priority in priorities:
                print(f"\n{priority.get('priority', 0)}. {priority.get('name', 'Unknown').upper()}")
                print("-" * 40)
                print(f"  Description: {priority.get('description', 'N/A')}")
                print(f"  Monthly Allocation: ${priority.get('monthly_allocation', 0):,.2f}")
                print(f"  Status: {priority.get('status', 'Unknown').replace('_', ' ').title()}")
                
                months = priority.get('months_to_complete', 0)
                if months != float('inf') and months > 0:
                    print(f"  Time to Complete: {months:.1f} months")
                
                recommendations = priority.get('recommendations', [])
                if recommendations:
                    print(f"  Recommendations:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"    {i}. {rec}")
            
            # Display plan summary
            summary = data.get('plan_summary', {})
            print(f"\n📋 Plan Summary:")
            print(f"  Debt Payoff Time: {summary.get('debt_payoff_months', 0):.1f} months")
            print(f"  Emergency Fund Time: {summary.get('emergency_fund_months', 0):.1f} months")
            print(f"  Retirement Match Immediate: {'Yes' if summary.get('retirement_match_immediate', False) else 'No'}")
            
            # Display next steps
            next_steps = data.get('next_steps', [])
            if next_steps:
                print(f"\n💡 Next Steps:")
                for i, step in enumerate(next_steps, 1):
                    print(f"  {i}. {step}")
            
            return True
        else:
            print(f"❌ Failed to create financial priorities: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        return False

def test_financial_priorities_validation():
    """Test API validation and error handling"""
    print(f"\n🧪 Testing API Validation...")
    print("=" * 60)
    
    # Test cases for validation
    test_cases = [
        {"file_id": "nonexistent", "expected_status": 404, "description": "Non-existent file"},
    ]
    
    results = []
    for test_case in test_cases:
        url = f"http://localhost:8000/files/{test_case['file_id']}/financial-priorities"
        financial_data = {
            "credit_card_debt": {"total_debt": 1000, "highest_apr": 20, "minimum_payments": 50, "debt_accounts": 1},
            "emergency_fund": {"current_emergency_fund": 500},
            "retirement_match": {"employer_match_percentage": 3, "match_limit": 6, "current_contribution": 3, "salary": 50000},
            "investing_allocation": {"risk_tolerance": 3, "investment_experience": 2, "preferred_retirement_account": "401k", "hysa_rate": 4.0}
        }
        
        try:
            response = requests.post(url, json=financial_data)
            if response.status_code == test_case["expected_status"]:
                print(f"✅ {test_case['description']}: Correct status {response.status_code}")
                results.append(True)
            else:
                print(f"❌ {test_case['description']}: Expected {test_case['expected_status']}, got {response.status_code}")
                results.append(False)
        except requests.exceptions.ConnectionError:
            print(f"❌ {test_case['description']}: Could not connect to server")
            results.append(False)
    
    return all(results)

def test_different_scenarios(file_id):
    """Test different financial scenarios"""
    if not file_id:
        return False
    
    print(f"\n🎭 Testing Different Financial Scenarios...")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "High Debt Scenario",
            "data": {
                "credit_card_debt": {"total_debt": 15000, "highest_apr": 25, "minimum_payments": 300, "debt_accounts": 5},
                "emergency_fund": {"current_emergency_fund": 0},
                "retirement_match": {"employer_match_percentage": 3, "match_limit": 6, "current_contribution": 0, "salary": 50000},
                "investing_allocation": {"risk_tolerance": 2, "investment_experience": 1, "preferred_retirement_account": "401k", "hysa_rate": 4.0}
            }
        },
        {
            "name": "No Debt Scenario",
            "data": {
                "credit_card_debt": {"total_debt": 0, "highest_apr": 0, "minimum_payments": 0, "debt_accounts": 0},
                "emergency_fund": {"current_emergency_fund": 2000},
                "retirement_match": {"employer_match_percentage": 4, "match_limit": 6, "current_contribution": 4, "salary": 75000},
                "investing_allocation": {"risk_tolerance": 4, "investment_experience": 3, "preferred_retirement_account": "both", "hysa_rate": 4.5}
            }
        }
    ]
    
    results = []
    for scenario in scenarios:
        print(f"\n📊 {scenario['name']}:")
        url = f"http://localhost:8000/files/{file_id}/financial-priorities"
        
        try:
            response = requests.post(url, json=scenario['data'])
            if response.status_code == 200:
                data = response.json()
                overview = data.get('financial_overview', {})
                print(f"  ✅ Success - Remaining: ${overview.get('remaining_after_plan', 0):,.2f}")
                results.append(True)
            else:
                print(f"  ❌ Failed: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append(False)
    
    return all(results)

if __name__ == "__main__":
    print("🎯 Financial Priority Tool Test Suite")
    print("=" * 60)
    print("ℹ️  This tests the financial priority planning tool")
    print("   Make sure the server is running on localhost:8000")
    print("=" * 60)
    
    # Show available CSV files
    print(f"📁 Available CSV files:")
    for name, path in CSV_FILES.items():
        status = "✅" if os.path.exists(path) else "❌"
        default_marker = " (DEFAULT)" if name == DEFAULT_CSV else ""
        print(f"  {status} {name}: {path}{default_marker}")
    
    print(f"\n🎯 Using CSV file: {DEFAULT_CSV} ({CSV_FILES[DEFAULT_CSV]})")
    print("💡 To change the CSV file, modify the DEFAULT_CSV variable at the top of this file")
    print("=" * 60)
    
    # Upload a file for analysis
    file_id = test_upload_for_financial_priorities()
    
    # Test validation first
    validation_success = test_financial_priorities_validation()
    
    # Test financial priorities
    if file_id:
        priorities_success = test_financial_priorities(file_id)
        scenarios_success = test_different_scenarios(file_id)
    else:
        priorities_success = False
        scenarios_success = False
    
    if validation_success and priorities_success and scenarios_success:
        print(f"\n🎉 All financial priority tests passed!")
    else:
        print(f"\n❌ Some financial priority tests failed")
    
    print(f"\n🔗 Financial Priority Endpoint:")
    print(f"🎯 POST /files/{{file_id}}/financial-priorities")
    print(f"   Send financial data to get personalized priority plan")
    print(f"   Returns: Complete financial plan with 4 priorities and recommendations")
