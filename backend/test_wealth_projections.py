#!/usr/bin/env python3
"""
Test script for wealth projections functionality
"""

import requests
import json

def test_wealth_projections():
    """Test wealth projections calculation"""
    url = "http://localhost:8000/wealth/projections"
    
    # Sample wealth data matching the frontend structure
    wealth_data = {
        "assets": {
            "realEstate": {"value": 500000, "rate": 3.5},
            "checking": {"value": 5000, "rate": 0},
            "savings": {"value": 25000, "rate": 2.0},
            "retirement": {"value": 100000, "rate": 10.0},
            "cars": {"value": 30000, "rate": -10.0},
            "otherAssets": {"value": 10000, "rate": 0}
        },
        "liabilities": {
            "realEstateLoans": {"value": 300000, "rate": 6.0},
            "creditCardDebt": {"value": 5000, "rate": 22.0},
            "personalLoans": {"value": 0, "rate": 12.0},
            "studentLoans": {"value": 20000, "rate": 7.0},
            "carLoans": {"value": 15000, "rate": 9.0},
            "otherDebt": {"value": 0, "rate": 0}
        },
        "contributions": {
            "contrib_checking": 2000,
            "contrib_hysa": 1000,
            "contrib_retirement": 1500,
            "move_checking_to_invest": 500
        },
        "debtPayments": {
            "pay_mortgage": 2000,
            "pay_cc": 500,
            "pay_personal": 0,
            "pay_student": 300,
            "pay_car": 400,
            "pay_other_debt": 0
        }
    }
    
    print("💰 Testing Wealth Projections API...")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=wealth_data)
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Wealth projections calculated successfully!")
            print(f"\n📊 Current Net Worth: ${data['current_net_worth']:,.2f}")
            
            print(f"\n📈 Monthly Cash Flow Summary:")
            summary = data['summary']
            print(f"  💰 Total Contributions: ${summary['total_contributions_monthly']:,.2f}")
            print(f"  💸 Total Debt Payments: ${summary['total_debt_payments_monthly']:,.2f}")
            print(f"  📊 Net Cash Flow: ${summary['net_monthly_cash_flow']:,.2f}")
            
            print(f"\n🔮 Future Wealth Projections:")
            projections = data['projections']
            
            for period, projection in projections.items():
                if 'error' in projection:
                    print(f"  ❌ {period.upper()}: {projection['error']}")
                else:
                    net_worth = projection['net_worth']
                    change = projection['net_worth_change']
                    change_pct = projection['net_worth_change_pct']
                    
                    print(f"  📅 {period.upper()}: ${net_worth:,.2f} (${change:+,.2f}, {change_pct:+.1f}%)")
                    
                    # Show time series data for shorter periods
                    if period in ['3m', '1y', '2y'] and 'time_series' in projection:
                        time_series = projection['time_series']
                        print(f"    📊 Time Series Data ({len(time_series)} months):")
                        # Show first few and last few months
                        for i, month_data in enumerate(time_series):
                            if i < 3 or i >= len(time_series) - 3:
                                print(f"      {month_data['month']}: Net Worth ${month_data['net_worth']:,.2f}")
                            elif i == 3:
                                print(f"      ... ({len(time_series) - 6} months) ...")
                    
                    # Show breakdown for longer periods
                    if period in ['5y', '10y', '20y', '50y']:
                        breakdown = projection['breakdown']
                        print(f"    🏠 Real Estate: ${breakdown['real_estate']:,.2f}")
                        print(f"    💳 Retirement: ${breakdown['retirement_invest']:,.2f}")
                        print(f"    🏦 Savings: ${breakdown['savings_hysa']:,.2f}")
                        print(f"    🚗 Cars: ${breakdown['cars_value']:,.2f}")
                        print(f"    🏠 Mortgage: ${breakdown['real_estate_loans']:,.2f}")
                        print(f"    💳 Credit Cards: ${breakdown['credit_card_debt']:,.2f}")
                        print(f"    🎓 Student Loans: ${breakdown['student_loans']:,.2f}")
                        print(f"    🚗 Car Loans: ${breakdown['car_loans']:,.2f}")
                        print()
            
            return True
        else:
            print(f"❌ Failed to calculate wealth projections: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        return False

def test_time_series_data():
    """Test time series data structure"""
    url = "http://localhost:8000/wealth/projections"
    
    # Simple wealth data for time series testing
    wealth_data = {
        "assets": {
            "realEstate": {"value": 300000, "rate": 3.5},
            "checking": {"value": 10000, "rate": 0},
            "savings": {"value": 20000, "rate": 2.0},
            "retirement": {"value": 50000, "rate": 10.0},
            "cars": {"value": 20000, "rate": -10.0},
            "otherAssets": {"value": 0, "rate": 0}
        },
        "liabilities": {
            "realEstateLoans": {"value": 200000, "rate": 6.0},
            "creditCardDebt": {"value": 3000, "rate": 22.0},
            "personalLoans": {"value": 0, "rate": 12.0},
            "studentLoans": {"value": 10000, "rate": 7.0},
            "carLoans": {"value": 10000, "rate": 9.0},
            "otherDebt": {"value": 0, "rate": 0}
        },
        "contributions": {
            "contrib_checking": 1000,
            "contrib_hysa": 500,
            "contrib_retirement": 800,
            "move_checking_to_invest": 200
        },
        "debtPayments": {
            "pay_mortgage": 1500,
            "pay_cc": 300,
            "pay_personal": 0,
            "pay_student": 200,
            "pay_car": 300,
            "pay_other_debt": 0
        }
    }
    
    print("\n📊 Testing Time Series Data Structure...")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=wealth_data)
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Time series data retrieved successfully!")
            
            # Test 1-year projection time series
            if '1y' in data['projections'] and 'time_series' in data['projections']['1y']:
                time_series = data['projections']['1y']['time_series']
                print(f"\n📈 1-Year Time Series ({len(time_series)} data points):")
                
                # Show sample data points
                for i, month_data in enumerate(time_series[::3]):  # Every 3rd month
                    print(f"  {month_data['month']}: Net Worth ${month_data['net_worth']:,.2f}")
                
                # Show data structure
                if time_series:
                    sample = time_series[0]
                    print(f"\n📋 Sample Data Structure:")
                    print(f"  Month: {sample['month']}")
                    print(f"  Net Worth: ${sample['net_worth']:,.2f}")
                    print(f"  Assets Total: ${sample['assets_total']:,.2f}")
                    print(f"  Liabilities Total: ${sample['liabilities_total']:,.2f}")
                    print(f"  Breakdown Keys: {list(sample['breakdown'].keys())}")
            
            return True
        else:
            print(f"❌ Failed to get time series data: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        return False

def test_wealth_projections_minimal():
    """Test wealth projections with minimal data"""
    url = "http://localhost:8000/wealth/projections"
    
    # Minimal wealth data
    wealth_data = {
        "assets": {
            "realEstate": {"value": 0, "rate": 3.5},
            "checking": {"value": 10000, "rate": 0},
            "savings": {"value": 5000, "rate": 2.0},
            "retirement": {"value": 0, "rate": 10.0},
            "cars": {"value": 0, "rate": -10.0},
            "otherAssets": {"value": 0, "rate": 0}
        },
        "liabilities": {
            "realEstateLoans": {"value": 0, "rate": 6.0},
            "creditCardDebt": {"value": 2000, "rate": 22.0},
            "personalLoans": {"value": 0, "rate": 12.0},
            "studentLoans": {"value": 0, "rate": 7.0},
            "carLoans": {"value": 0, "rate": 9.0},
            "otherDebt": {"value": 0, "rate": 0}
        },
        "contributions": {
            "contrib_checking": 1000,
            "contrib_hysa": 500,
            "contrib_retirement": 0,
            "move_checking_to_invest": 0
        },
        "debtPayments": {
            "pay_mortgage": 0,
            "pay_cc": 200,
            "pay_personal": 0,
            "pay_student": 0,
            "pay_car": 0,
            "pay_other_debt": 0
        }
    }
    
    print("\n💰 Testing Wealth Projections (Minimal Data)...")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=wealth_data)
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Minimal wealth projections calculated successfully!")
            print(f"📊 Current Net Worth: ${data['current_net_worth']:,.2f}")
            
            projections = data['projections']
            print(f"\n🔮 Key Projections:")
            for period in ['1y', '5y', '10y']:
                if period in projections and 'error' not in projections[period]:
                    projection = projections[period]
                    net_worth = projection['net_worth']
                    change = projection['net_worth_change']
                    print(f"  📅 {period.upper()}: ${net_worth:,.2f} (${change:+,.2f})")
            
            return True
        else:
            print(f"❌ Failed to calculate minimal wealth projections: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        return False

if __name__ == "__main__":
    print("💰 Wealth Projections API Test Suite")
    print("=" * 60)
    print("ℹ️  This tests the wealth projection calculations")
    print("   Make sure the server is running on localhost:8000")
    print("=" * 60)
    
    # Test with comprehensive data
    success1 = test_wealth_projections()
    
    # Test time series data structure
    success2 = test_time_series_data()
    
    # Test with minimal data
    success3 = test_wealth_projections_minimal()
    
    if success1 and success2 and success3:
        print(f"\n🎉 All wealth projection tests passed!")
    else:
        print(f"\n❌ Some wealth projection tests failed")
    
    print(f"\n🔗 Wealth Projections Endpoint:")
    print(f"💰 POST /wealth/projections")
    print(f"   Send wealth data to get future projections for 3m, 1y, 2y, 5y, 10y, 20y, 50y")
