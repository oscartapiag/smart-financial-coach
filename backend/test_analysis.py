#!/usr/bin/env python3
"""
Test script for financial analysis and time series functionality
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

def test_upload_for_analysis(csv_type=None):
    """Upload a file for analysis testing"""
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
    
    print(f"📁 Uploading CSV file: {csv_path}")
    
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

def test_financial_analysis(file_id):
    """Test the financial analysis endpoint"""
    if not file_id:
        print("❌ No file ID provided for analysis test")
        return
        
    url = f"http://localhost:8000/files/{file_id}/analysis"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Financial Analysis:")
            print(f"💰 Total amount: ${data['transaction_summary']['total_amount']:.2f}")
            print(f"💸 Total expenses: ${data['spending_analysis']['total_expenses']:.2f}")
            print(f"💵 Total income: ${data['spending_analysis']['total_income']:.2f}")
            print(f"📈 Net amount: ${data['spending_analysis']['net_amount']:.2f}")
            
            # Show ML category analysis if available
            if 'category_analysis' in data and 'income_vs_spending' in data['category_analysis']:
                cat_analysis = data['category_analysis']
                income_spending = cat_analysis['income_vs_spending']
                
                print(f"\n🤖 Smart Category Analysis:")
                print(f"💰 Income Transactions: {income_spending['income_transactions']} ({income_spending['income_percentage']:.1f}%)")
                print(f"💸 Spending Transactions: {income_spending['spending_transactions']} ({income_spending['spending_percentage']:.1f}%)")
                
                if 'top_spending_categories' in cat_analysis:
                    print(f"📊 Top Spending Categories: {list(cat_analysis['top_spending_categories'].keys())[:5]}")
                
                if 'spending_confidence_stats' in cat_analysis:
                    conf_stats = cat_analysis['spending_confidence_stats']
                    print(f"🎯 ML Confidence (Spending): {conf_stats['mean_confidence']:.2f}")
                    print(f"❓ Uncategorized Spending: {cat_analysis['uncategorized_percentage']:.1f}%")
                
                # Show category spending breakdown if available
                if 'category_breakdown' in data['spending_analysis']:
                    print(f"\n💰 Spending by Category:")
                    breakdown = data['spending_analysis']['category_breakdown']
                    for category, info in list(breakdown.items())[:5]:  # Show top 5
                        print(f"  {category}: ${info['total_amount']:.2f} ({info['transaction_count']} transactions)")
                
                # Show time series trends if available
                if 'trends' in data:
                    trends = data['trends']
                    print(f"\n📈 Financial Trends:")
                    print(f"  💰 Income Trend: {trends['income_trend_direction']} (slope: {trends['income_trend']:.2f})")
                    print(f"  💸 Spending Trend: {trends['spending_trend_direction']} (slope: {trends['spending_trend']:.2f})")
                
                # Show time series data if available
                if 'time_series' in data:
                    time_series = data['time_series']
                    print(f"\n📊 Time Series Data Available:")
                    for period in time_series.keys():
                        period_data = time_series[period]
                        income_points = len(period_data.get('income', {}))
                        spending_points = len(period_data.get('spending', {}))
                        print(f"  {period.capitalize()}: {income_points} income points, {spending_points} spending points")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")

def test_time_series(file_id):
    """Test cumulative time series endpoint"""
    if not file_id:
        print("❌ No file ID provided for time series test")
        return
        
    url = f"http://localhost:8000/files/{file_id}/time-series"
    
    print(f"\n📊 Testing Cumulative Time Series Data:")
    for period in ["14d", "30d", "90d", "1y"]:
        try:
            response = requests.get(url, params={"period": period})
            if response.status_code == 200:
                data = response.json()
                income_points = len(data['income'])
                spending_points = len(data['spending'])
                date_range = data['date_range']
                summary = data['summary']
                
                print(f"  {period.upper()}: {date_range['days_covered']} days")
                print(f"    Date Range: {date_range['start_date']} to {date_range['end_date']}")
                print(f"    Data Points: {income_points} income, {spending_points} spending")
                print(f"    Total Income: ${summary['total_income']:.2f}")
                print(f"    Total Spending: ${summary['total_spending']:.2f}")
                print(f"    Net Amount: ${summary['net_amount']:.2f}")
                
                # Show cumulative progression
                if income_points > 0:
                    first_income = data['income'][0]
                    last_income = data['income'][-1]
                    print(f"    Income: ${first_income['cumulative_amount']:.2f} → ${last_income['cumulative_amount']:.2f}")
                
                if spending_points > 0:
                    first_spending = data['spending'][0]
                    last_spending = data['spending'][-1]
                    print(f"    Spending: ${first_spending['cumulative_amount']:.2f} → ${last_spending['cumulative_amount']:.2f}")
                
                print()  # Add spacing
            else:
                print(f"  ❌ Failed to get {period} data: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server")
            break

def test_categories_by_time(file_id):
    """Test categories by time period endpoint"""
    if not file_id:
        print("❌ No file ID provided for categories by time test")
        return
        
    url = f"http://localhost:8000/files/{file_id}/categories-by-time"
    
    print(f"\n📊 Testing Categories by Time Period:")
    for period in ["14d", "30d", "90d", "1y"]:
        try:
            response = requests.get(url, params={"period": period})
            if response.status_code == 200:
                data = response.json()
                date_range = data['date_range']
                summary = data['summary']
                top_categories = data['top_categories']
                
                print(f"  {period.upper()}: {date_range['days_covered']} days")
                print(f"    Date Range: {date_range['start_date']} to {date_range['end_date']}")
                print(f"    Total Spending: ${summary['total_spending']:.2f}")
                print(f"    Unique Categories: {summary['unique_categories']}")
                print(f"    Spending Transactions: {summary['spending_transactions']}")
                
                # Show top 3 categories
                if top_categories:
                    print(f"    Top Categories:")
                    for i, (category, info) in enumerate(list(top_categories.items())[:3], 1):
                        print(f"      {i}. {category}: ${info['total_amount']:.2f} ({info['percentage_of_spending']:.1f}%)")
                        print(f"         {info['transaction_count']} transactions, avg: ${info['average_amount']:.2f}")
                
                print()  # Add spacing
            else:
                print(f"  ❌ Failed to get {period} categories: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server")
            break

def test_file_details(file_id):
    """Test file details endpoint"""
    if not file_id:
        return
        
    url = f"http://localhost:8000/files/{file_id}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"\n📁 File Details:")
            print(f"  File ID: {data['file_id']}")
            print(f"  Filename: {data['filename']}")
            print(f"  Upload Time: {data['upload_time']}")
            print(f"  File Size: {data['file_size']} bytes")
        else:
            print(f"❌ Failed to get file details: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")

if __name__ == "__main__":
    print("📊 Testing Financial Analysis & Time Series...")
    print("=" * 50)
    
    # Show available CSV files
    print(f"📁 Available CSV files:")
    for name, path in CSV_FILES.items():
        status = "✅" if os.path.exists(path) else "❌"
        default_marker = " (DEFAULT)" if name == DEFAULT_CSV else ""
        print(f"  {status} {name}: {path}{default_marker}")
    
    print(f"\n🎯 Using CSV file: {DEFAULT_CSV} ({CSV_FILES[DEFAULT_CSV]})")
    print("💡 To change the CSV file, modify the DEFAULT_CSV variable at the top of this file")
    print("=" * 50)
    
    # Upload a file for analysis testing
    file_id = test_upload_for_analysis()
    
    if file_id:
        # Test file details
        test_file_details(file_id)
        
        # Test financial analysis
        test_financial_analysis(file_id)
        
        # Test time series data
        test_time_series(file_id)
        
        # Test categories by time
        test_categories_by_time(file_id)
        
        print(f"\n🔗 Analysis Endpoints:")
        print(f"📁 File details: http://localhost:8000/files/{file_id}")
        print(f"📊 File analysis: http://localhost:8000/files/{file_id}/analysis")
        print(f"📈 Time series data: http://localhost:8000/files/{file_id}/time-series")
        print(f"📊 Categories by time: http://localhost:8000/files/{file_id}/categories-by-time")
        print(f"🤖 Categorized transactions: http://localhost:8000/files/{file_id}/categorized")
    else:
        print("❌ Could not upload file for analysis testing")
