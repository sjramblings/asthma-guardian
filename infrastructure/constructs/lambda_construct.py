"""
Lambda Construct for Asthma Guardian v3

This construct creates reusable Lambda function configurations
with common settings and environment variables.
"""

from aws_cdk import (
    aws_lambda as lambda_,
    aws_iam as iam,
    Duration
)
from constructs import Construct


class LambdaConstruct(Construct):
    """Reusable Lambda construct."""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
    
    def create_function(
        self,
        function_name: str,
        handler: str,
        code: lambda_.Code,
        environment: dict = None,
        timeout: Duration = Duration.seconds(30),
        memory_size: int = 128
    ) -> lambda_.Function:
        """Create a Lambda function with common configuration."""
        
        return lambda_.Function(
            self,
            function_name,
            function_name=function_name,
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler=handler,
            code=code,
            environment=environment or {},
            timeout=timeout,
            memory_size=memory_size
        )
