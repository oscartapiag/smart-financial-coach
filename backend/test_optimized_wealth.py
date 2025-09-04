#!/usr/bin/env python3
"""
Test script for optimized wealth projections functionality
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

def test_upload_for_optimization(csv_type=None):
    """Upload a file for optimization testing"""
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
    
    print(f"📁 Uploading CSV file for optimization testing: {csv_path}")
    
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

def test_optimized_wealth_projections(file_id):
    """Test optimized wealth projections with spending analysis"""
    if not file_id:
        print("❌ No file ID provided for optimization test")
        return
        
    url = "http://localhost:8000/wealth/optimized-projections"
    
    # Sample wealth data
    wealth_data = {
        "file_id": file_id,
        "assets": {
            "realEstate": {"value": 400000, "rate": 3.5},
            "checking": {"value": 8000, "rate": 0},
            "savings": {"value": 15000, "rate": 2.0},
            "retirement": {"value": 75000, "rate": 10.0},
            "cars": {"value": 25000, "rate": -10.0},
            "otherAssets": {"value": 5000, "rate": 0}
        },
        "liabilities": {
            "realEstateLoans": {"value": 250000, "rate": 6.0},
            "creditCardDebt": {"value": 4000, "rate": 22.0},
            "personalLoans": {"value": 0, "rate": 12.0},
            "studentLoans": {"value": 15000, "rate": 7.0},
            "carLoans": {"value": 12000, "rate": 9.0},
            "otherDebt": {"value": 0, "rate": 0}
        },
        "contributions": {
            "contrib_checking": 1500,
            "contrib_hysa": 800,
            "contrib_retirement": 1200,
            "move_checking_to_invest": 300
        },
        "debtPayments": {
            "pay_mortgage": 1800,
            "pay_cc": 400,
            "pay_personal": 0,
            "pay_student": 250,
            "pay_car": 350,
            "pay_other_debt": 0
        }
    }
    
    print(f"\n💰 Testing Optimized Wealth Projections...")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=wealth_data)
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Optimized wealth projections calculated successfully!")
            print(f"📊 Current Net Worth: ${data['current_net_worth']:,.2f}")
            
            # Show spending analysis
            top_categories = data.get('top_spending_categories', [])
            if top_categories:
                print(f"\n🎯 Top 3 Spending Categories (20% Reduction):")
                for i, category in enumerate(top_categories, 1):
                    print(f"  {i}. {category['category']}")
                    print(f"     Current: ${category['current_spending']:,.2f}/month")
                    print(f"     Reduction: ${category['suggested_reduction']:,.2f}/month")
                    print(f"     New Amount: ${category['new_spending']:,.2f}/month")
                    print()
            else:
                print(f"\n⚠️  No spending categories found for optimization")
            
            monthly_savings = data.get('monthly_savings', 0)
            print(f"💡 Total Monthly Savings: ${monthly_savings:,.2f}")
            
            # Show summary
            summary = data.get('summary', {})
            print(f"\n📈 Monthly Contribution Summary:")
            print(f"  Original: ${summary.get('total_contributions_monthly', 0):,.2f}")
            print(f"  Optimized: ${summary.get('optimized_contributions_monthly', 0):,.2f}")
            print(f"  Additional Savings: ${summary.get('additional_monthly_savings', 0):,.2f}")
            
            # Show projections comparison
            print(f"\n🔮 Wealth Projections Comparison:")
            original_projections = data.get('original_projections', {})
            optimized_projections = data.get('optimized_projections', {})
            
            for period in ['1y', '5y', '10y', '20y']:
                if period in original_projections and period in optimized_projections:
                    orig = original_projections[period]
                    opt = optimized_projections[period]
                    
                    if 'error' not in orig and 'error' not in opt:
                        improvement = opt.get('improvement', 0)
                        improvement_pct = opt.get('improvement_pct', 0)
                        
                        print(f"  📅 {period.upper()}:")
                        print(f"    Original: ${orig['net_worth']:,.2f}")
                        print(f"    Optimized: ${opt['net_worth']:,.2f}")
                        print(f"    Improvement: ${improvement:+,.2f} ({improvement_pct:+.1f}%)")
                        print()
            
            return True
        else:
            print(f"❌ Failed to calculate optimized projections: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        return False

def test_optimized_without_file():
    """Test optimized projections without file_id (no spending analysis)"""
    url = "http://localhost:8000/wealth/optimized-projections"
    
    # Sample wealth data without file_id
    wealth_data = {
        "assets": {
            "realEstate": {"value": 300000, "rate": 3.5},
            "checking": {"value": 5000, "rate": 0},
            "savings": {"value": 10000, "rate": 2.0},
            "retirement": {"value": 50000, "rate": 10.0},
            "cars": {"value": 15000, "rate": -10.0},
            "otherAssets": {"value": 0, "rate": 0}
        },
        "liabilities": {
            "realEstateLoans": {"value": 200000, "rate": 6.0},
            "creditCardDebt": {"value": 2000, "rate": 22.0},
            "personalLoans": {"value": 0, "rate": 12.0},
            "studentLoans": {"value": 10000, "rate": 7.0},
            "carLoans": {"value": 8000, "rate": 9.0},
            "otherDebt": {"value": 0, "rate": 0}
        },
        "contributions": {
            "contrib_checking": 1000,
            "contrib_hysa": 500,
            "contrib_retirement": 800,
            "move_checking_to_invest": 200
        },
        "debtPayments": {
            "pay_mortgage": 1200,
            "pay_cc": 200,
            "pay_personal": 0,
            "pay_student": 150,
            "pay_car": 250,
            "pay_other_debt": 0
        }
    }
    
    print(f"\n💰 Testing Optimized Projections (No File Analysis)...")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=wealth_data)
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Optimized projections calculated successfully!")
            print(f"📊 Current Net Worth: ${data['current_net_worth']:,.2f}")
            
            top_categories = data.get('top_spending_categories', [])
            if top_categories:
                print(f"🎯 Found {len(top_categories)} spending categories")
            else:
                print(f"ℹ️  No spending categories (no file_id provided)")
            
            monthly_savings = data.get('monthly_savings', 0)
            print(f"💡 Monthly Savings: ${monthly_savings:,.2f}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        return False

if __name__ == "__main__":
    print("💰 Optimized Wealth Projections Test Suite")
    print("=" * 60)
    print("ℹ️  This tests spending optimization and wealth projections")
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
    
    # Upload a file for optimization testing
    file_id = test_upload_for_optimization()
    
    # Test optimized projections with file analysis
    if file_id:
        success1 = test_optimized_wealth_projections(file_id)
    else:
        success1 = False
    
    # Test optimized projections without file analysis
    success2 = test_optimized_without_file()
    
    if success1 and success2:
        print(f"\n🎉 All optimized wealth projection tests passed!")
    else:
        print(f"\n❌ Some optimized wealth projection tests failed")
    
    print(f"\n🔗 Optimized Wealth Projections Endpoint:")
    print(f"💰 POST /wealth/optimized-projections")
    print(f"   Send wealth data + file_id to get spending-optimized projections")
    print(f"   Returns: top spending categories, original projections, optimized projections")
