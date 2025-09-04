#!/usr/bin/env python3
"""
Test script for subscription detection functionality
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

def test_subscription_model_status():
    """Test the subscription model status"""
    url = "http://localhost:8000/subscriptions/status"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🔍 Subscription Model Status:")
            print(f"✅ Model Loaded: {data['model_loaded']}")
            print(f"📁 Model Path: {data['model_path']}")
            print(f"📄 Model Exists: {data['model_exists']}")
            if data.get('feature_columns'):
                print(f"🔧 Feature Columns: {len(data['feature_columns'])} features")
            return data['model_loaded']
        else:
            print(f"❌ Subscription model status check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        return False

def test_ml_status():
    """Test the overall ML models status"""
    url = "http://localhost:8000/ml/status"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🤖 ML Models Status:")
            
            # Category model status
            cat_model = data['category_model']
            print(f"📊 Category Model:")
            print(f"  ✅ Loaded: {cat_model['loaded']}")
            print(f"  📁 Path: {cat_model['path']}")
            print(f"  📄 Exists: {cat_model['exists']}")
            
            # Subscription model status
            sub_model = data['subscription_model']
            print(f"🔍 Subscription Model:")
            print(f"  ✅ Loaded: {sub_model['loaded']}")
            print(f"  📁 Path: {sub_model['path']}")
            print(f"  📄 Exists: {sub_model['exists']}")
            
            return cat_model['loaded'] and sub_model['loaded']
        else:
            print(f"❌ ML status check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        return False

def test_upload_for_subscriptions(csv_type=None):
    """Upload a file for subscription testing"""
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
    
    print(f"📁 Uploading CSV file for subscription testing: {csv_path}")
    
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

def test_subscription_detection(file_id, threshold=0.5):
    """Test subscription detection for a file"""
    if not file_id:
        print("❌ No file ID provided for subscription detection test")
        return
        
    url = f"http://localhost:8000/files/{file_id}/subscriptions"
    
    try:
        response = requests.get(url, params={"threshold": threshold})
        if response.status_code == 200:
            data = response.json()
            print(f"\n🔍 Subscription Detection Results:")
            print(f"📊 Threshold: {data['threshold']}")
            print(f"💸 Expense Transactions Analyzed: {data.get('expense_transactions_analyzed', 'N/A')}")
            print(f"📈 Total Subscriptions Found: {data['total_subscriptions']}")
            print(f"💰 Total Monthly Cost: ${data.get('total_monthly_cost', 0):.2f}")
            
            if data['subscriptions']:
                print(f"\n📋 Detected Subscriptions:")
                for i, sub in enumerate(data['subscriptions'], 1):
                    print(f"  {i}. {sub['merchant']}")
                    print(f"     Score: {sub['subscription_score']:.3f}")
                    print(f"     Occurrences: {sub['occurrences']}")
                    print(f"     Coverage: {sub['coverage_months']} months")
                    print(f"     Avg Amount: ${sub['average_amount']:.2f}")
                    print(f"     Monthly Cost: ${sub.get('average_monthly_cost', 0):.2f}")
                    print(f"     Day Consistency: {sub['day_consistency']:.2f}")
                    print(f"     Median Gap: {sub['median_gap_days']:.1f} days")
                    if sub.get('website'):
                        print(f"     Website: {sub['website']}")
                    else:
                        print(f"     Website: Not found")
                    print()
            else:
                print("ℹ️  No subscriptions detected above the threshold")
                
        elif response.status_code == 503:
            print("❌ Subscription model not loaded")
        else:
            print(f"❌ Failed to detect subscriptions: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")

def test_different_thresholds(file_id):
    """Test subscription detection with different thresholds"""
    if not file_id:
        return
        
    print(f"\n🎯 Testing Different Thresholds:")
    thresholds = [0.3, 0.5, 0.7, 0.9]
    
    for threshold in thresholds:
        url = f"http://localhost:8000/files/{file_id}/subscriptions"
        try:
            response = requests.get(url, params={"threshold": threshold})
            if response.status_code == 200:
                data = response.json()
                total_cost = data.get('total_monthly_cost', 0)
                print(f"  Threshold {threshold}: {data['total_subscriptions']} subscriptions (${total_cost:.2f}/month)")
            else:
                print(f"  Threshold {threshold}: Failed ({response.status_code})")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server")
            break

if __name__ == "__main__":
    print("🔍 Testing Subscription Detection Functionality...")
    print("=" * 60)
    print("ℹ️  Note: Subscription detection only analyzes EXPENSE transactions (amount ≤ 0)")
    print("   Income transactions are automatically filtered out")
    
    # Show available CSV files
    print(f"📁 Available CSV files:")
    for name, path in CSV_FILES.items():
        status = "✅" if os.path.exists(path) else "❌"
        default_marker = " (DEFAULT)" if name == DEFAULT_CSV else ""
        print(f"  {status} {name}: {path}{default_marker}")
    
    print(f"\n🎯 Using CSV file: {DEFAULT_CSV} ({CSV_FILES[DEFAULT_CSV]})")
    print("💡 To change the CSV file, modify the DEFAULT_CSV variable at the top of this file")
    print("=" * 60)
    
    # Test subscription model status
    subscription_model_loaded = test_subscription_model_status()
    
    # Test overall ML status
    all_models_loaded = test_ml_status()
    
    if not subscription_model_loaded:
        print("⚠️  Subscription model not loaded, some tests may fail")
    
    # Upload a file for subscription testing
    file_id = test_upload_for_subscriptions()
    
    # Test subscription detection
    if file_id:
        test_subscription_detection(file_id)
        test_different_thresholds(file_id)
    
    print(f"\n🔗 Subscription Endpoints:")
    print(f"🔍 Subscription status: http://localhost:8000/subscriptions/status")
    print(f"🤖 ML models status: http://localhost:8000/ml/status")
    if file_id:
        print(f"📊 File subscriptions: http://localhost:8000/files/{file_id}/subscriptions")
        print(f"📊 File subscriptions (threshold=0.3): http://localhost:8000/files/{file_id}/subscriptions?threshold=0.3")
        print(f"📊 File subscriptions (threshold=0.7): http://localhost:8000/files/{file_id}/subscriptions?threshold=0.7")
