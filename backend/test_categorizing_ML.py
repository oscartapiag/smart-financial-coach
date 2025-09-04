#!/usr/bin/env python3
"""
Test script for ML categorization functionality
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

def test_ml_status():
    """Test the ML models status"""
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

def test_single_prediction():
    """Test single category prediction"""
    url = "http://localhost:8000/ml/predict-category"
    
    test_descriptions = [
        "STARBUCKS COFFEE #1234",
        "AMAZON.COM PURCHASE",
        "SHELL GAS STATION",
        "NETFLIX MONTHLY SUBSCRIPTION",
        "SALARY DEPOSIT",
        "RENT PAYMENT",
        "GROCERY STORE PURCHASE"
    ]
    
    print(f"\n🔮 Testing Single Predictions:")
    for desc in test_descriptions:
        try:
            response = requests.post(url, params={"description": desc})
            if response.status_code == 200:
                data = response.json()
                print(f"  '{desc}' → {data['predicted_category']} (confidence: {data['confidence']:.2f})")
            else:
                print(f"  ❌ Failed to predict for '{desc}': {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server")
            break

def test_categorized_transactions(file_id):
    """Test getting categorized transactions"""
    if not file_id:
        print("❌ No file ID provided for categorized transactions test")
        return
        
    url = f"http://localhost:8000/files/{file_id}/categorized"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🤖 Categorized Transactions:")
            print(f"📊 Total transactions: {data['total_transactions']}")
            
            # Show sample of categorized transactions
            transactions = data['transactions'][:5]  # First 5 transactions
            for i, transaction in enumerate(transactions, 1):
                if 'ml_category' in transaction and 'ml_confidence' in transaction:
                    print(f"  {i}. {transaction.get('description', 'N/A')[:30]}...")
                    print(f"     Category: {transaction['ml_category']} (confidence: {transaction['ml_confidence']:.2f})")
                    print(f"     Amount: ${transaction.get('amount', 'N/A')}")
        else:
            print(f"❌ Failed to get categorized transactions: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")

def test_upload_for_ml(csv_type=None):
    """Upload a file for ML testing"""
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
    
    print(f"📁 Uploading CSV file for ML testing: {csv_path}")
    
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

if __name__ == "__main__":
    print("🤖 Testing ML Categorization Functionality...")
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
    
    # Test ML status first
    models_loaded = test_ml_status()
    
    if not models_loaded:
        print("⚠️  Some ML models not loaded, some tests may fail")
    
    # Test single predictions
    test_single_prediction()
    
    # Upload a file for ML testing
    file_id = test_upload_for_ml()
    
    # Test categorized transactions
    if file_id:
        test_categorized_transactions(file_id)
    
    print(f"\n🔗 ML Endpoints:")
    print(f"🤖 ML models status: http://localhost:8000/ml/status")
    print(f"🔮 Single category prediction: http://localhost:8000/ml/predict-category")
    print(f"🔍 Subscription model status: http://localhost:8000/subscriptions/status")
    if file_id:
        print(f"📊 Categorized transactions: http://localhost:8000/files/{file_id}/categorized")
        print(f"📊 File subscriptions: http://localhost:8000/files/{file_id}/subscriptions")
