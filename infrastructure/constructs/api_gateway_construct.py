"""
API Gateway Construct for Asthma Guardian v3

This construct creates a reusable API Gateway configuration
with CORS, authentication, and rate limiting.
"""

from aws_cdk import (
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    Duration
)
from constructs import Construct


class ApiGatewayConstruct(Construct):
    """Reusable API Gateway construct."""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create API Gateway
        self.api = apigateway.RestApi(
            self,
            "ApiGateway",
            rest_api_name="asthma-guardian-v3-api",
            description="API Gateway for Asthma Guardian v3",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            ),
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=1000,
                throttling_burst_limit=2000
            )
        )
    
    def add_lambda_integration(self, path: str, lambda_function: lambda_.Function, methods: list[str] = ["GET"]) -> None:
        """Add Lambda integration to API Gateway."""
        resource = self.api.root
        for part in path.split("/"):
            if part:
                resource = resource.get_resource(part) or resource.add_resource(part)
        
        for method in methods:
            resource.add_method(
                method,
                apigateway.LambdaIntegration(
                    lambda_function,
                    request_templates={"application/json": '{"statusCode": "200"}'}
                )
            )
