#!/usr/bin/env python3
"""
Simple CDK test to verify the setup works
"""

try:
    from aws_cdk import App, Stack
    from constructs import Construct
    print("✅ CDK imports successful")
    
    app = App()
    stack = Stack(app, "TestStack")
    print("✅ CDK app and stack creation successful")
    
    app.synth()
    print("✅ CDK synthesis successful")
    
except Exception as e:
    print(f"❌ CDK test failed: {e}")
    import traceback
    traceback.print_exc()
