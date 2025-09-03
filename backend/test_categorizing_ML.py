#!/usr/bin/env python3
"""
Test script for ML categorization functionality
"""

import requests
import json

def test_ml_status():
    """Test the ML model status"""
    url = "http://localhost:8000/ml/status"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🤖 ML Model Status:")
            print(f"✅ Model Loaded: {data['model_loaded']}")
            print(f"📁 Model Path: {data['model_path']}")
            print(f"📄 Model Exists: {data['model_exists']}")
            return data['model_loaded']
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

def test_upload_for_ml():
    """Upload a file for ML testing"""
    url = "http://localhost:8000/upload-transactions"
    
    with open("./trans_data_internal/sample_transactions.csv", "rb") as f:
        files = {"file": ("./trans_data_internal/sample_transactions.csv", f, "text/csv")}
        
        try:
            response = requests.post(url, files=files)
            if response.status_code == 200:
                data = response.json()
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
    
    # Test ML status first
    model_loaded = test_ml_status()
    
    if not model_loaded:
        print("⚠️  ML model not loaded, some tests may fail")
    
    # Test single predictions
    test_single_prediction()
    
    # Upload a file for ML testing
    file_id = test_upload_for_ml()
    
    # Test categorized transactions
    if file_id:
        test_categorized_transactions(file_id)
    
    print(f"\n🔗 ML Endpoints:")
    print(f"🤖 ML status: http://localhost:8000/ml/status")
    print(f"🔮 Single prediction: http://localhost:8000/ml/predict-category")
    if file_id:
        print(f"📊 Categorized transactions: http://localhost:8000/files/{file_id}/categorized")
