"""
Security Construct for Asthma Guardian v3

This construct creates reusable security configurations
including IAM roles, policies, and KMS keys.
"""

from aws_cdk import (
    aws_iam as iam,
    aws_kms as kms,
    RemovalPolicy
)
from constructs import Construct


class SecurityConstruct(Construct):
    """Reusable security construct."""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
    
    def create_kms_key(self, key_name: str, description: str) -> kms.Key:
        """Create a KMS key with common configuration."""
        
        return kms.Key(
            self,
            key_name,
            description=description,
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY
        )
    
    def create_lambda_role(self, role_name: str, policies: list = None) -> iam.Role:
        """Create a Lambda execution role with common policies."""
        
        role = iam.Role(
            self,
            role_name,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Add custom policies if provided
        if policies:
            for policy in policies:
                role.add_managed_policy(policy)
        
        return role
