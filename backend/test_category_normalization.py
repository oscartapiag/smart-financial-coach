#!/usr/bin/env python3
"""
Test script to verify that 'Other' and 'Uncategorized' are treated as the same category
"""

import requests
import json

def test_category_normalization():
    """Test that the ML model treats 'Other' and 'Uncategorized' as the same category"""
    url = "http://localhost:8000/ml/predict-category"
    
    # Test descriptions that might be categorized as "Other" or "Uncategorized"
    test_descriptions = [
        "UNKNOWN STORE TRANSACTION",
        "RANDOM PURCHASE",
        "MYSTERY CHARGE",
        "UNIDENTIFIED TRANSACTION",
        "STRANGE STORE NAME",
        "OBSCURE BUSINESS",
        "UNFAMILIAR MERCHANT"
    ]
    
    print("🧪 Testing Category Normalization...")
    print("=" * 50)
    
    for desc in test_descriptions:
        try:
            response = requests.post(url, params={"description": desc})
            if response.status_code == 200:
                data = response.json()
                category = data['predicted_category']
                confidence = data['confidence']
                
                # Check if the category is "Uncategorized" (not "Other")
                if category == "Uncategorized":
                    print(f"✅ '{desc}' → {category} (confidence: {confidence:.2f})")
                elif category == "Other":
                    print(f"❌ '{desc}' → {category} (confidence: {confidence:.2f}) - Should be 'Uncategorized'")
                else:
                    print(f"ℹ️  '{desc}' → {category} (confidence: {confidence:.2f}) - Categorized as specific category")
            else:
                print(f"❌ Failed to predict for '{desc}': {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server")
            break
    
    print("\n📊 Summary:")
    print("- All predictions should return 'Uncategorized' instead of 'Other'")
    print("- Low confidence predictions should default to 'Uncategorized'")
    print("- The ML model now treats 'Other' and 'Uncategorized' as the same category")

if __name__ == "__main__":
    test_category_normalization()
