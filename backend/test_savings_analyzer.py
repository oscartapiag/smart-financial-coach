#!/usr/bin/env python3
"""
Test script for savings analyzer functionality
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

def test_upload_for_savings(csv_type=None):
    """Upload a file for savings analysis testing"""
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
    
    print(f"📁 Uploading CSV file for savings analysis: {csv_path}")
    
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

def test_savings_analysis(file_id, target_amount, months):
    """Test savings analysis for a specific goal"""
    if not file_id:
        print("❌ No file ID provided for savings analysis")
        return False
        
    url = "http://localhost:8000/savings/analyze"
    
    savings_request = {
        "file_id": file_id,
        "target_amount": target_amount,
        "months": months
    }
    
    print(f"\n💰 Testing Savings Analysis...")
    print(f"🎯 Goal: ${target_amount:,.2f} in {months} months")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=savings_request)
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Savings analysis completed successfully!")
            
            # Display goal information
            goal = data.get('goal', {})
            print(f"\n🎯 Savings Goal:")
            print(f"  Target Amount: ${goal.get('target_amount', 0):,.2f}")
            print(f"  Timeframe: {goal.get('months_to_save', 0)} months")
            print(f"  Monthly Target: ${goal.get('monthly_target', 0):,.2f}")
            
            # Display current financials
            financials = data.get('current_financials', {})
            print(f"\n📊 Current Financials (Last 3 Months):")
            print(f"  Monthly Income: ${financials.get('monthly_income', 0):,.2f}")
            print(f"  Monthly Expenses: ${financials.get('monthly_expenses', 0):,.2f}")
            print(f"  Monthly Savings: ${financials.get('monthly_savings', 0):,.2f}")
            
            # Display analysis results
            analysis = data.get('analysis', {})
            print(f"\n📈 Analysis Results:")
            print(f"  Can Achieve Goal: {'✅ Yes' if analysis.get('can_achieve_goal', False) else '❌ No'}")
            print(f"  Shortfall: ${analysis.get('shortfall', 0):,.2f}")
            print(f"  Suggested Savings: ${analysis.get('total_suggested_savings', 0):,.2f}")
            print(f"  Remaining Shortfall: ${analysis.get('remaining_shortfall', 0):,.2f}")
            
            # Display suggested cuts
            suggested_cuts = data.get('suggested_cuts', [])
            if suggested_cuts:
                print(f"\n✂️  Suggested Spending Cuts:")
                for i, cut in enumerate(suggested_cuts, 1):
                    priority_text = {1: "High", 2: "Medium", 3: "Low", 4: "Very Low"}.get(cut.get('priority', 4), "Unknown")
                    print(f"  {i}. {cut.get('category', 'Unknown')} ({priority_text} Priority)")
                    print(f"     Current: ${cut.get('current_monthly', 0):,.2f}/month")
                    print(f"     Suggested: ${cut.get('suggested_monthly', 0):,.2f}/month")
                    print(f"     Reduction: ${cut.get('reduction_amount', 0):,.2f}/month ({cut.get('reduction_percentage', 0):.1f}%)")
                    print()
            else:
                print(f"\nℹ️  No spending cuts suggested")
            
            # Display alternative strategies
            strategies = data.get('alternative_strategies', [])
            if strategies:
                print(f"\n💡 Alternative Strategies:")
                for i, strategy in enumerate(strategies, 1):
                    print(f"  {i}. {strategy}")
                print()
            
            # Display summary
            summary = data.get('summary', {})
            print(f"\n📋 Summary:")
            print(f"  Categories Analyzed: {summary.get('total_categories_analyzed', 0)}")
            print(f"  High Priority Cuts: {summary.get('high_priority_cuts', 0)}")
            print(f"  Total Monthly Reduction: ${summary.get('total_monthly_reduction', 0):,.2f}")
            print(f"  Achievable with Cuts: {'✅ Yes' if summary.get('achievable_with_cuts', False) else '❌ No'}")
            
            return True
        else:
            print(f"❌ Failed to analyze savings goal: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        return False

def test_multiple_goals(file_id):
    """Test savings analysis with multiple different goals"""
    if not file_id:
        return False
    
    goals = [
        {"amount": 1000, "months": 6, "description": "Emergency Fund - $1,000 in 6 months"},
        {"amount": 5000, "months": 12, "description": "Vacation Fund - $5,000 in 1 year"},
        {"amount": 10000, "months": 24, "description": "Car Down Payment - $10,000 in 2 years"},
        {"amount": 25000, "months": 60, "description": "House Down Payment - $25,000 in 5 years"}
    ]
    
    print(f"\n🎯 Testing Multiple Savings Goals...")
    print("=" * 60)
    
    results = []
    for goal in goals:
        print(f"\n📊 {goal['description']}")
        success = test_savings_analysis(file_id, goal['amount'], goal['months'])
        results.append(success)
        
        if not success:
            print(f"❌ Failed to analyze goal: {goal['description']}")
    
    return all(results)

def test_savings_analyzer_validation():
    """Test API validation and error handling"""
    url = "http://localhost:8000/savings/analyze"
    
    print(f"\n🧪 Testing API Validation...")
    print("=" * 60)
    
    # Test cases for validation
    test_cases = [
        {"data": {}, "expected_status": 400, "description": "Missing file_id"},
        {"data": {"file_id": "nonexistent", "target_amount": 1000, "months": 12}, "expected_status": 404, "description": "Non-existent file"},
        {"data": {"file_id": "test", "target_amount": -1000, "months": 12}, "expected_status": 400, "description": "Negative target amount"},
        {"data": {"file_id": "test", "target_amount": 1000, "months": -6}, "expected_status": 400, "description": "Negative months"},
        {"data": {"file_id": "test", "target_amount": 0, "months": 12}, "expected_status": 400, "description": "Zero target amount"},
    ]
    
    results = []
    for test_case in test_cases:
        try:
            response = requests.post(url, json=test_case["data"])
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

if __name__ == "__main__":
    print("💰 Savings Analyzer Test Suite")
    print("=" * 60)
    print("ℹ️  This tests spending analysis and savings goal recommendations")
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
    
    # Upload a file for savings analysis
    file_id = test_upload_for_savings()
    
    # Test validation first
    validation_success = test_savings_analyzer_validation()
    
    # Test savings analysis with different goals
    if file_id:
        # Test single goal
        single_goal_success = test_savings_analysis(file_id, 5000, 12)
        
        # Test multiple goals
        multiple_goals_success = test_multiple_goals(file_id)
    else:
        single_goal_success = False
        multiple_goals_success = False
    
    if validation_success and single_goal_success and multiple_goals_success:
        print(f"\n🎉 All savings analyzer tests passed!")
    else:
        print(f"\n❌ Some savings analyzer tests failed")
    
    print(f"\n🔗 Savings Analyzer Endpoint:")
    print(f"💰 POST /savings/analyze")
    print(f"   Send file_id, target_amount, and months to get savings analysis")
    print(f"   Returns: spending analysis, suggested cuts, and alternative strategies")
