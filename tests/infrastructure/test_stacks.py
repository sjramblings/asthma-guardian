"""
CDK Infrastructure Unit Tests

This module contains unit tests for the CDK infrastructure components.
"""

import pytest
from aws_cdk import App, Stack
from aws_cdk.assertions import Template
from app import AsthmaGuardianV3Stack


class TestAsthmaGuardianV3Stack:
    """Test cases for the main CDK stack."""
    
    def test_stack_creation(self):
        """Test that the stack can be created successfully."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Verify the stack was created
        assert stack is not None
        assert template is not None
    
    def test_dynamodb_tables_created(self):
        """Test that DynamoDB tables are created with correct configuration."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Check Users table
        template.has_resource_properties("AWS::DynamoDB::Table", {
            "TableName": "asthma-guardian-users",
            "BillingMode": "PAY_PER_REQUEST",
            "PointInTimeRecoverySpecification": {
                "PointInTimeRecoveryEnabled": True
            }
        })
        
        # Check Air Quality table
        template.has_resource_properties("AWS::DynamoDB::Table", {
            "TableName": "asthma-guardian-air-quality",
            "BillingMode": "PAY_PER_REQUEST"
        })
        
        # Check Guidance table
        template.has_resource_properties("AWS::DynamoDB::Table", {
            "TableName": "asthma-guardian-guidance",
            "BillingMode": "PAY_PER_REQUEST"
        })
        
        # Check User Alerts table
        template.has_resource_properties("AWS::DynamoDB::Table", {
            "TableName": "asthma-guardian-user-alerts",
            "BillingMode": "PAY_PER_REQUEST"
        })
    
    def test_lambda_functions_created(self):
        """Test that Lambda functions are created with correct configuration."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Check Air Quality Lambda
        template.has_resource_properties("AWS::Lambda::Function", {
            "Runtime": "python3.12",
            "Handler": "handler.handler"
        })
        
        # Verify all Lambda functions exist
        lambda_functions = [
            "AirQualityLambda",
            "UserProfileLambda", 
            "GuidanceLambda",
            "NotificationsLambda",
            "DataIngestionLambda"
        ]
        
        for function_name in lambda_functions:
            template.has_resource("AWS::Lambda::Function", {
                "Properties": {
                    "FunctionName": {
                        "Fn::Join": ["", [function_name, "-", {"Ref": "AWS::StackName"}]]
                    }
                }
            })
    
    def test_api_gateway_created(self):
        """Test that API Gateway is created with correct configuration."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Check API Gateway
        template.has_resource_properties("AWS::ApiGateway::RestApi", {
            "Name": "asthma-guardian-v3-api"
        })
        
        # Check CORS configuration
        template.has_resource_properties("AWS::ApiGateway::Method", {
            "HttpMethod": "OPTIONS"
        })
    
    def test_cloudfront_distribution_created(self):
        """Test that CloudFront distribution is created."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Check CloudFront distribution
        template.has_resource("AWS::CloudFront::Distribution", {})
        
        # Check S3 bucket for website hosting
        template.has_resource("AWS::S3::Bucket", {})
    
    def test_waf_web_acl_created(self):
        """Test that WAF Web ACL is created for security."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Check WAF Web ACL
        template.has_resource_properties("AWS::WAFv2::WebACL", {
            "Name": "asthma-guardian-v3-waf",
            "Scope": "CLOUDFRONT"
        })
    
    def test_vpc_created(self):
        """Test that VPC is created with proper configuration."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Check VPC
        template.has_resource_properties("AWS::EC2::VPC", {
            "CidrBlock": "10.0.0.0/16",
            "EnableDnsHostnames": True,
            "EnableDnsSupport": True
        })
        
        # Check subnets
        template.resource_count_is("AWS::EC2::Subnet", 9)  # 3 AZs * 3 subnet types
    
    def test_security_groups_created(self):
        """Test that security groups are created."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Check security groups
        template.has_resource("AWS::EC2::SecurityGroup", {})
    
    def test_cloudwatch_alarms_created(self):
        """Test that CloudWatch alarms are created."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Check CloudWatch alarms
        template.has_resource("AWS::CloudWatch::Alarm", {})
        
        # Check SNS topic
        template.has_resource("AWS::SNS::Topic", {})
    
    def test_kms_key_created(self):
        """Test that KMS key is created for encryption."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Check KMS key
        template.has_resource_properties("AWS::KMS::Key", {
            "Description": "KMS key for Asthma Guardian v3",
            "EnableKeyRotation": True
        })
    
    def test_eventbridge_rule_created(self):
        """Test that EventBridge rule is created for scheduled tasks."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Check EventBridge rule
        template.has_resource("AWS::Events::Rule", {})
    
    def test_iam_roles_created(self):
        """Test that IAM roles are created with proper permissions."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Check Lambda execution role
        template.has_resource_properties("AWS::IAM::Role", {
            "AssumeRolePolicyDocument": {
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }]
            }
        })
    
    def test_outputs_created(self):
        """Test that required outputs are created."""
        app = App()
        stack = AsthmaGuardianV3Stack(app, "TestStack")
        template = Template.from_stack(stack)
        
        # Check outputs
        template.has_output("ApiGatewayUrl", {})
        template.has_output("CloudFrontDomainName", {})
        template.has_output("WebsiteBucketName", {})


if __name__ == "__main__":
    pytest.main([__file__])
