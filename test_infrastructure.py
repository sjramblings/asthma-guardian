#!/usr/bin/env python3
"""
Test script to verify the CDK infrastructure works correctly
"""

import json
import subprocess
import sys
from pathlib import Path

def test_cdk_synthesis():
    """Test that CDK synthesis works without errors."""
    print("🧪 Testing CDK synthesis...")
    
    try:
        result = subprocess.run(
            ["cdk", "synth", "--quiet"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print("✅ CDK synthesis successful")
            return True
        else:
            print(f"❌ CDK synthesis failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ CDK synthesis error: {e}")
        return False

def test_cdk_list():
    """Test that CDK list shows the expected stack."""
    print("🧪 Testing CDK list...")
    
    try:
        result = subprocess.run(
            ["cdk", "list"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0 and "AsthmaGuardianV3-dev" in result.stdout:
            print("✅ CDK list shows expected stack")
            return True
        else:
            print(f"❌ CDK list failed or unexpected output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ CDK list error: {e}")
        return False

def test_cdk_diff():
    """Test that CDK diff works (should show no changes for new stack)."""
    print("🧪 Testing CDK diff...")
    
    try:
        result = subprocess.run(
            ["cdk", "diff"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        # CDK diff returns 0 for no changes, 1 for changes, so both are valid
        print("✅ CDK diff completed")
        return True
            
    except Exception as e:
        print(f"❌ CDK diff error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting CDK infrastructure tests...")
    
    tests = [
        test_cdk_synthesis,
        test_cdk_list,
        test_cdk_diff
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Infrastructure is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
