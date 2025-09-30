"""
Backend Stack for Asthma Guardian v3

This stack creates the infrastructure for the backend API services
including API Gateway, Lambda functions, and related resources.
"""

from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_iam as iam,
    CfnOutput,
    Duration
)
from constructs import Construct


class BackendStack(Stack):
    """Stack for backend API services."""
    
    def __init__(self, scope: Construct, construct_id: str, env_name: str, database_stack=None, security_stack=None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.env_name = env_name
        self.database_stack = database_stack
        self.security_stack = security_stack
        
        # Create API Gateway
        self.api = apigateway.RestApi(
            self,
            "ApiGateway",
            rest_api_name=f"asthma-guardian-v3-api-{env_name}",
            description="API Gateway for Asthma Guardian v3",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            ),
            deploy_options=apigateway.StageOptions(
                stage_name=env_name,
                throttling_rate_limit=1000,
                throttling_burst_limit=2000
            )
        )
        
        # Create Lambda function for air quality API
        self.air_quality_lambda = lambda_.Function(
            self,
            "AirQualityLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="air_quality.handler",
            code=lambda_.Code.from_inline("""
def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"message": "Air quality API endpoint"}'
    }
            """),
            environment={
                "ENVIRONMENT": env_name,
                "DYNAMODB_TABLE_PREFIX": "asthma-guardian"
            },
            timeout=Duration.seconds(30)
        )
        
        # Create Lambda function for user profile API
        self.user_profile_lambda = lambda_.Function(
            self,
            "UserProfileLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="user_profile.handler",
            code=lambda_.Code.from_inline("""
def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"message": "User profile API endpoint"}'
    }
            """),
            environment={
                "ENVIRONMENT": env_name,
                "DYNAMODB_TABLE_PREFIX": "asthma-guardian"
            },
            timeout=Duration.seconds(30)
        )
        
        # Create API Gateway integrations
        air_quality_integration = apigateway.LambdaIntegration(
            self.air_quality_lambda,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )
        
        user_profile_integration = apigateway.LambdaIntegration(
            self.user_profile_lambda,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )
        
        # Add API routes
        air_quality = self.api.root.add_resource("api").add_resource("air-quality")
        air_quality.add_method("GET", air_quality_integration)
        
        users = self.api.root.add_resource("api").add_resource("users")
        users.add_method("GET", user_profile_integration)
        users.add_method("PUT", user_profile_integration)
        
        # Outputs
        CfnOutput(
            self,
            "ApiGatewayUrl",
            value=self.api.url,
            description="API Gateway URL"
        )
        
        CfnOutput(
            self,
            "ApiGatewayId",
            value=self.api.rest_api_id,
            description="API Gateway ID"
        )
