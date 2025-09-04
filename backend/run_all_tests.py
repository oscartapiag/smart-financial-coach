#!/usr/bin/env python3
"""
Master test runner for all financial coach API tests
"""

import subprocess
import sys
import os

def run_test(test_file):
    """Run a test file and return success status"""
    print(f"\n{'='*60}")
    print(f"Running {test_file}...")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=False, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Run all test files in sequence"""
    test_files = [
        "test_upload.py",
        "test_categorizing_ML.py", 
        "test_analysis.py",
        "test_subscriptions.py",
        "test_ai_insights.py"
    ]
    
    print("🧪 Financial Coach API - Complete Test Suite")
    print("=" * 60)
    print("This will run all test files in sequence:")
    for i, test_file in enumerate(test_files, 1):
        print(f"  {i}. {test_file}")
    
    print(f"\n⚠️  Make sure the FastAPI server is running on http://localhost:8000")
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    results = {}
    
    for test_file in test_files:
        if os.path.exists(test_file):
            success = run_test(test_file)
            results[test_file] = success
        else:
            print(f"❌ Test file {test_file} not found")
            results[test_file] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_file, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_file}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
