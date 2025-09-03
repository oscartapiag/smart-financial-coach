#!/usr/bin/env python3
"""
Test script to demonstrate the financial CSV upload functionality
"""

import requests
import json

def test_upload():
    """Test the CSV upload endpoint"""
    url = "http://localhost:8000/upload-transactions"
    
    # Test with sample file
    with open("sample_transactions.csv", "rb") as f:
        files = {"file": ("sample_transactions.csv", f, "text/csv")}
        
        try:
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('is_duplicate'):
                    print("🔄 Duplicate detected!")
                    print(f"📁 Existing File ID: {data['file_id']}")
                    print(f"📅 Original upload: {data['original_upload_time']}")
                else:
                    print("✅ Upload successful!")
                    print(f"📁 File ID: {data['file_id']}")
                    print(f"📊 Total rows: {data['rows']}")
                    print(f"📋 Total columns: {data['columns']}")
                return data['file_id']
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(response.text)
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure it's running on http://localhost:8000")
            return None

def test_upload_2():
    """Test the CSV upload endpoint"""
    url = "http://localhost:8000/upload-transactions"
    
    # Test with sample file
    with open("sample_transaction_2.csv", "rb") as f:
        files = {"file": ("sample_transaction_2.csv", f, "text/csv")}
        
        try:
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Upload successful!")
                print(f"📁 File ID: {data['file_id']}")
                print(f"📊 Total rows: {data['rows']}")
                print(f"📋 Total columns: {data['columns']}")
                return data['file_id']
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(response.text)
                return None
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure it's running on http://localhost:8000")
            return None

def test_duplicate_upload():
    """Test uploading the same file twice to verify duplicate detection"""
    print("\n🔄 Testing duplicate detection...")
    url = "http://localhost:8000/upload-transactions"
    
    # Upload the same file twice
    with open("sample_transactions.csv", "rb") as f:
        files = {"file": ("sample_transactions.csv", f, "text/csv")}
        
        try:
            response = requests.post(url, files=files)
            if response.status_code == 200:
                data = response.json()
                if data.get('is_duplicate'):
                    print("✅ Duplicate detection working correctly!")
                    print(f"📁 Returned existing file ID: {data['file_id']}")
                else:
                    print("⚠️  First upload - this is expected")
            else:
                print(f"❌ Upload failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server")

def test_analysis(file_id):
    """Test the analysis endpoint"""
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
        else:
            print(f"❌ Analysis failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")

def test_file_list():
    """Test the file listing endpoint"""
    url = "http://localhost:8000/files"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 Found {data['total_files']} uploaded files:")
            for file_info in data['files']:
                print(f"  - {file_info['filename']} (ID: {file_info['file_id'][:8]}...)")
        else:
            print(f"❌ Failed to list files: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")

if __name__ == "__main__":
    print("🧪 Testing Financial Coach API...")
    print("=" * 50)
    
    # Test upload
    file_id = test_upload()
    file_id_2 = test_upload_2()
    
    # Test duplicate detection
    test_duplicate_upload()
    
    # Test analysis if upload was successful
    if file_id:
        test_analysis(file_id)
    
    # Test file listing
    test_file_list()
    
    if file_id:
        print(f"\n🔗 You can view the API docs at: http://localhost:8000/docs")
        print(f"📁 File details: http://localhost:8000/files/{file_id}")
        print(f"📊 File analysis: http://localhost:8000/files/{file_id}/analysis")
        print(f"⬇️  Download file: http://localhost:8000/files/{file_id}/download")
        print(f"🔍 Hash registry: http://localhost:8000/files/registry")
