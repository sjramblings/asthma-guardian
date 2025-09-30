#!/usr/bin/env python3
"""
Asthma Guardian v3 CDK Application

This is the main entry point for the CDK application that defines all the stacks
for the Asthma Guardian v3 infrastructure.
"""

import os
from aws_cdk import App, Environment, Stack
from constructs import Construct


def main():
    """Main CDK application entry point."""
    app = App()
    
    # Get environment variables
    env_name = os.getenv('ENVIRONMENT', 'dev')
    aws_account = os.getenv('AWS_ACCOUNT_ID')
    aws_region = os.getenv('AWS_REGION', 'ap-southeast-2')
    
    # Create environment object
    env = Environment(account=aws_account, region=aws_region)
    
    # Create a simple test stack for now
    class TestStack(Stack):
        def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
            super().__init__(scope, construct_id, **kwargs)
    
    # Create test stack
    test_stack = TestStack(
        app,
        f"AsthmaGuardianV3-TestStack-{env_name}",
        env=env
    )
    
    # Add tags to all resources
    app.node.apply_metadata("cdk:tags", {
        "Project": "AsthmaGuardianV3",
        "Environment": env_name,
        "ManagedBy": "CDK"
    })
    
    app.synth()


if __name__ == "__main__":
    main()
