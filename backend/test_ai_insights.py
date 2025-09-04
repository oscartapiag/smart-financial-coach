#!/usr/bin/env python3
"""
Test script for AI insights functionality
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

def test_upload_for_insights(csv_type=None):
    """Upload a file for AI insights testing"""
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
    
    print(f"📁 Uploading CSV file for AI insights testing: {csv_path}")
    
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

def test_ai_insights(file_id, period="30d"):
    """Test AI insights generation"""
    if not file_id:
        print("❌ No file ID provided for AI insights test")
        return
        
    url = f"http://localhost:8000/files/{file_id}/insights"
    
    try:
        response = requests.get(url, params={"period": period})
        if response.status_code == 200:
            data = response.json()
            print(f"\n🤖 AI Insights Results:")
            print(f"📊 Period: {data['period']}")
            print(f"📈 Summary:")
            summary = data['summary']
            print(f"  💰 Current Income: ${summary['current_income']:.2f}")
            print(f"  💸 Current Expenses: ${summary['current_expenses']:.2f}")
            print(f"  📊 Current Net: ${summary['current_net']:.2f}")
            print(f"  📈 Prior Net: ${summary['prior_net']:.2f}")
            print(f"  🔄 Net Change: ${summary['net_change']:.2f}")
            
            insights = data.get('insights', {})
            cards = insights.get('cards', [])
            
            if cards:
                print(f"\n💡 AI Insights ({len(cards)} cards):")
                for i, card in enumerate(cards, 1):
                    print(f"\n  {i}. {card.get('title', 'No Title')}")
                    print(f"     Type: {card.get('kind', 'unknown')}")
                    print(f"     Summary: {card.get('summary', 'No summary')}")
                    if card.get('impact') is not None:
                        print(f"     Impact: {card['impact']}")
                    if card.get('period'):
                        print(f"     Period: {card['period']}")
                    if card.get('metrics'):
                        print(f"     Metrics: {json.dumps(card['metrics'], indent=6)}")
                    if card.get('cta'):
                        print(f"     CTA: {json.dumps(card['cta'], indent=6)}")
            else:
                print("ℹ️  No AI insights generated")
                
        else:
            print(f"❌ Failed to get AI insights: {response.status_code}")
            if response.status_code == 500:
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")

def test_different_periods(file_id):
    """Test AI insights with different time periods"""
    if not file_id:
        return
        
    print(f"\n🎯 Testing Different Time Periods:")
    periods = ["14d", "30d", "90d", "1y"]
    
    for period in periods:
        url = f"http://localhost:8000/files/{file_id}/insights"
        try:
            response = requests.get(url, params={"period": period})
            if response.status_code == 200:
                data = response.json()
                cards = data.get('insights', {}).get('cards', [])
                summary = data.get('summary', {})
                print(f"  {period.upper()}: {len(cards)} insights, Net: ${summary.get('current_net', 0):.2f}")
            else:
                print(f"  {period.upper()}: Failed ({response.status_code})")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server")
            break

if __name__ == "__main__":
    print("🤖 Testing AI Insights Functionality...")
    print("=" * 60)
    print("ℹ️  Note: This requires OpenAI API key to be set in environment")
    print("   Set OPENAI_API_KEY environment variable")
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
    
    # Upload a file for AI insights testing
    file_id = test_upload_for_insights()
    
    # Test AI insights
    if file_id:
        test_ai_insights(file_id)
        test_different_periods(file_id)
    
    print(f"\n🔗 AI Insights Endpoints:")
    print(f"🤖 AI insights: http://localhost:8000/files/{file_id}/insights")
    print(f"🤖 AI insights (14d): http://localhost:8000/files/{file_id}/insights?period=14d")
    print(f"🤖 AI insights (90d): http://localhost:8000/files/{file_id}/insights?period=90d")
    print(f"🤖 AI insights (1y): http://localhost:8000/files/{file_id}/insights?period=1y")
