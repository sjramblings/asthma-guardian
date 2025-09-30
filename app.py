#!/usr/bin/env python3
"""
Asthma Guardian v3 CDK Application - Simplified Version
"""

import os
from aws_cdk import (
    App, Environment, Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_kms as kms,
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
    aws_sns as sns,
    aws_events as events,
    aws_events_targets as targets,
    aws_wafv2 as wafv2,
    aws_cloudfront_origins as cf_origins,
    CfnOutput,
    RemovalPolicy,
    Duration
)
from constructs import Construct


class AsthmaGuardianV3Stack(Stack):
    """Main stack for Asthma Guardian v3 infrastructure."""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create KMS key for encryption
        self.kms_key = kms.Key(
            self,
            "EncryptionKey",
            description="KMS key for Asthma Guardian v3",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Create VPC with enhanced security
        self.vpc = ec2.Vpc(
            self,
            "VPC",
            vpc_name="asthma-guardian-v3-vpc",
            max_azs=3,  # Use 3 AZs for better availability
            nat_gateways=2,  # Use 2 NAT gateways for high availability
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                    map_public_ip_on_launch=False  # Don't auto-assign public IPs
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Database",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True
        )
        
        # Create security groups
        self.lambda_security_group = ec2.SecurityGroup(
            self,
            "LambdaSecurityGroup",
            vpc=self.vpc,
            description="Security group for Lambda functions",
            allow_all_outbound=True
        )
        
        self.api_security_group = ec2.SecurityGroup(
            self,
            "ApiSecurityGroup",
            vpc=self.vpc,
            description="Security group for API Gateway",
            allow_all_outbound=True
        )
        
        # Allow HTTPS traffic to API Gateway
        self.api_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="HTTPS traffic to API Gateway"
        )
        
        # Allow Lambda to access DynamoDB and other AWS services
        self.lambda_security_group.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="HTTPS outbound for AWS services"
        )
        
        # Create DynamoDB tables
        self.users_table = dynamodb.Table(
            self,
            "UsersTable",
            table_name="asthma-guardian-users",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True
            ),
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        self.air_quality_table = dynamodb.Table(
            self,
            "AirQualityTable",
            table_name="asthma-guardian-air-quality",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True
            ),
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            time_to_live_attribute="ttl",
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Guidance Recommendations table
        self.guidance_table = dynamodb.Table(
            self,
            "GuidanceTable",
            table_name="asthma-guardian-guidance",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True
            ),
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            time_to_live_attribute="ttl",
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Add GSI for location-based queries
        self.guidance_table.add_global_secondary_index(
            index_name="LocationIndex",
            partition_key=dynamodb.Attribute(
                name="GSI1PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="GSI1SK",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # User Alerts table
        self.user_alerts_table = dynamodb.Table(
            self,
            "UserAlertsTable",
            table_name="asthma-guardian-user-alerts",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True
            ),
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            time_to_live_attribute="ttl",
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Add GSI for status-based queries
        self.user_alerts_table.add_global_secondary_index(
            index_name="StatusIndex",
            partition_key=dynamodb.Attribute(
                name="GSI1PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="GSI1SK",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # Create Lambda execution role with enhanced security
        self.lambda_execution_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole")
            ],
            role_name="asthma-guardian-v3-lambda-execution-role",
            inline_policies={
                "DynamoDBAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "dynamodb:GetItem",
                                "dynamodb:PutItem",
                                "dynamodb:UpdateItem",
                                "dynamodb:DeleteItem",
                                "dynamodb:Query",
                                "dynamodb:Scan"
                            ],
                            resources=[
                                self.users_table.table_arn,
                                self.air_quality_table.table_arn,
                                self.guidance_table.table_arn,
                                self.user_alerts_table.table_arn
                            ]
                        )
                    ]
                ),
                "BedrockAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "bedrock:InvokeModel",
                                "bedrock:InvokeModelWithResponseStream"
                            ],
                            resources=["*"]
                        )
                    ]
                ),
                "NotificationAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "sns:Publish",
                                "sns:GetTopicAttributes"
                            ],
                            resources=["*"]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ses:SendEmail",
                                "ses:SendRawEmail"
                            ],
                            resources=["*"]
                        )
                    ]
                ),
                "KMSAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["kms:Decrypt", "kms:GenerateDataKey"],
                            resources=[self.kms_key.key_arn]
                        )
                    ]
                ),
                "CloudWatchLogsAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                                "logs:DescribeLogGroups",
                                "logs:DescribeLogStreams"
                            ],
                            resources=["arn:aws:logs:*:*:*"]
                        )
                    ]
                )
            }
        )
        
        # Create Lambda functions
        self.air_quality_lambda = lambda_.Function(
            self,
            "AirQualityLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=lambda_.Code.from_asset("backend/lambda_functions/air_quality"),
            environment={
                "ENVIRONMENT": "dev",
                "DYNAMODB_TABLE_PREFIX": "asthma-guardian",
                "AIR_QUALITY_TABLE_NAME": self.air_quality_table.table_name
            },
            timeout=Duration.seconds(30),
            role=self.lambda_execution_role,
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self.lambda_security_group],
            dead_letter_queue_enabled=True,
            tracing=lambda_.Tracing.ACTIVE
        )
        
        self.user_profile_lambda = lambda_.Function(
            self,
            "UserProfileLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=lambda_.Code.from_asset("backend/lambda_functions/user_profile"),
            environment={
                "ENVIRONMENT": "dev",
                "DYNAMODB_TABLE_PREFIX": "asthma-guardian",
                "USERS_TABLE_NAME": self.users_table.table_name
            },
            timeout=Duration.seconds(30),
            role=self.lambda_execution_role,
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self.lambda_security_group],
            dead_letter_queue_enabled=True,
            tracing=lambda_.Tracing.ACTIVE
        )
        
        self.guidance_lambda = lambda_.Function(
            self,
            "GuidanceLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=lambda_.Code.from_asset("backend/lambda_functions/guidance"),
            environment={
                "ENVIRONMENT": "dev",
                "DYNAMODB_TABLE_PREFIX": "asthma-guardian",
                "USERS_TABLE_NAME": self.users_table.table_name,
                "AIR_QUALITY_TABLE_NAME": self.air_quality_table.table_name,
                "GUIDANCE_TABLE_NAME": self.guidance_table.table_name
            },
            timeout=Duration.seconds(60),  # Longer timeout for Bedrock calls
            role=self.lambda_execution_role,
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self.lambda_security_group],
            dead_letter_queue_enabled=True,
            tracing=lambda_.Tracing.ACTIVE
        )
        
        self.notifications_lambda = lambda_.Function(
            self,
            "NotificationsLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=lambda_.Code.from_asset("backend/lambda_functions/notifications"),
            environment={
                "ENVIRONMENT": "dev",
                "DYNAMODB_TABLE_PREFIX": "asthma-guardian",
                "USERS_TABLE_NAME": self.users_table.table_name,
                "USER_ALERTS_TABLE_NAME": self.user_alerts_table.table_name,
                "SES_FROM_EMAIL": "noreply@asthmaguardian.nsw.gov.au"
            },
            timeout=Duration.seconds(30),
            role=self.lambda_execution_role,
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self.lambda_security_group],
            dead_letter_queue_enabled=True,
            tracing=lambda_.Tracing.ACTIVE
        )
        
        self.data_ingestion_lambda = lambda_.Function(
            self,
            "DataIngestionLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=lambda_.Code.from_asset("backend/lambda_functions/data_ingestion"),
            environment={
                "ENVIRONMENT": "dev",
                "DYNAMODB_TABLE_PREFIX": "asthma-guardian",
                "AIR_QUALITY_TABLE_NAME": self.air_quality_table.table_name,
                "NSW_AIR_QUALITY_API_URL": "https://api.airquality.nsw.gov.au",
                "BOM_API_URL": "https://api.bom.gov.au"
            },
            timeout=Duration.seconds(300),  # 5 minutes for data ingestion
            role=self.lambda_execution_role,
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self.lambda_security_group],
            dead_letter_queue_enabled=True,
            tracing=lambda_.Tracing.ACTIVE
        )
        
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
        
        # Add API routes
        air_quality_integration = apigateway.LambdaIntegration(
            self.air_quality_lambda,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )
        
        user_profile_integration = apigateway.LambdaIntegration(
            self.user_profile_lambda,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )
        
        guidance_integration = apigateway.LambdaIntegration(
            self.guidance_lambda,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )
        
        notifications_integration = apigateway.LambdaIntegration(
            self.notifications_lambda,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )
        
        # Create API resource once
        api_resource = self.api.root.add_resource("api")
        
        # Air Quality API endpoints
        air_quality = api_resource.add_resource("air-quality")
        air_quality.add_method("GET", air_quality_integration)  # /api/air-quality/current
        
        # Add forecast and history endpoints
        forecast = air_quality.add_resource("forecast")
        forecast.add_method("GET", air_quality_integration)
        
        history = air_quality.add_resource("history")
        history.add_method("GET", air_quality_integration)
        
        # User Profile API endpoints
        users = api_resource.add_resource("users")
        users.add_method("POST", user_profile_integration)  # /api/users
        
        user = users.add_resource("{user_id}")
        user.add_method("GET", user_profile_integration)    # /api/users/{user_id}
        user.add_method("PUT", user_profile_integration)    # /api/users/{user_id}
        
        # Guidance API endpoints
        guidance = api_resource.add_resource("guidance")
        guidance.add_method("POST", guidance_integration)   # /api/guidance
        
        user_guidance = guidance.add_resource("{user_id}")
        user_guidance.add_method("GET", guidance_integration)  # /api/guidance/{user_id}
        
        # Notification API endpoints
        notifications = api_resource.add_resource("notifications")
        notifications.add_method("POST", notifications_integration)  # /api/notifications
        
        user_notifications = notifications.add_resource("{user_id}")
        user_notifications.add_method("GET", notifications_integration)  # /api/notifications/{user_id}
        
        notification_preferences = notifications.add_resource("preferences").add_resource("{user_id}")
        notification_preferences.add_method("PUT", notifications_integration)  # /api/notifications/preferences/{user_id}
        
        # Create S3 bucket for website hosting
        self.website_bucket = s3.Bucket(
            self,
            "WebsiteBucket",
            bucket_name="asthma-guardian-v3-website",
            website_index_document="index.html",
            website_error_document="error.html",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        # Create WAF Web ACL for CloudFront
        self.waf_web_acl = wafv2.CfnWebACL(
            self,
            "WAFWebACL",
            name="asthma-guardian-v3-waf",
            description="WAF Web ACL for Asthma Guardian v3",
            scope="CLOUDFRONT",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(
                allow=wafv2.CfnWebACL.AllowActionProperty()
            ),
            rules=[
                # Rate limiting rule
                wafv2.CfnWebACL.RuleProperty(
                    name="RateLimitRule",
                    priority=1,
                    statement=wafv2.CfnWebACL.StatementProperty(
                        rate_based_statement=wafv2.CfnWebACL.RateBasedStatementProperty(
                            limit=2000,
                            aggregate_key_type="IP"
                        )
                    ),
                    action=wafv2.CfnWebACL.RuleActionProperty(
                        block=wafv2.CfnWebACL.BlockActionProperty()
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name="RateLimitRule"
                    )
                ),
                # AWS Managed Rules for Core Rule Set
                wafv2.CfnWebACL.RuleProperty(
                    name="AWSManagedRulesCommonRuleSet",
                    priority=2,
                    override_action=wafv2.CfnWebACL.OverrideActionProperty(
                        none={}
                    ),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            vendor_name="AWS",
                            name="AWSManagedRulesCommonRuleSet"
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name="AWSManagedRulesCommonRuleSet"
                    )
                ),
                # AWS Managed Rules for Known Bad Inputs
                wafv2.CfnWebACL.RuleProperty(
                    name="AWSManagedRulesKnownBadInputsRuleSet",
                    priority=3,
                    override_action=wafv2.CfnWebACL.OverrideActionProperty(
                        none={}
                    ),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                            vendor_name="AWS",
                            name="AWSManagedRulesKnownBadInputsRuleSet"
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name="AWSManagedRulesKnownBadInputsRuleSet"
                    )
                )
            ],
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                sampled_requests_enabled=True,
                cloud_watch_metrics_enabled=True,
                metric_name="AsthmaGuardianV3WAF"
            )
        )

        # Create CloudFront distribution with WAF
        self.distribution = cloudfront.Distribution(
            self,
            "WebsiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin(self.website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                compress=True,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS
            ),
            additional_behaviors={
                "/api/*": cloudfront.BehaviorOptions(
                    origin=origins.HttpOrigin(
                        f"{self.api.rest_api_id}.execute-api.{self.region}.amazonaws.com"
                    ),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD
                )
            },
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html"
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html"
                )
            ]
        )
        
        # Associate WAF with CloudFront distribution
        wafv2.CfnWebACLAssociation(
            self,
            "WAFWebACLAssociation",
            resource_arn=f"arn:aws:cloudfront::{self.account}:distribution/{self.distribution.distribution_id}",
            web_acl_arn=self.waf_web_acl.attr_arn
        )
        
        # Create CloudWatch log groups with enhanced monitoring
        self.api_log_group = logs.LogGroup(
            self,
            "ApiLogGroup",
            log_group_name="/aws/apigateway/asthma-guardian-v3-api",
            retention=logs.RetentionDays.THREE_MONTHS,
            encryption_key=self.kms_key
        )
        
        # Create specific log groups for each Lambda function
        self.air_quality_log_group = logs.LogGroup(
            self,
            "AirQualityLogGroup",
            log_group_name="/aws/lambda/asthma-guardian-v3-air-quality",
            retention=logs.RetentionDays.ONE_MONTH,
            encryption_key=self.kms_key
        )
        
        self.user_profile_log_group = logs.LogGroup(
            self,
            "UserProfileLogGroup",
            log_group_name="/aws/lambda/asthma-guardian-v3-user-profile",
            retention=logs.RetentionDays.ONE_MONTH,
            encryption_key=self.kms_key
        )
        
        self.guidance_log_group = logs.LogGroup(
            self,
            "GuidanceLogGroup",
            log_group_name="/aws/lambda/asthma-guardian-v3-guidance",
            retention=logs.RetentionDays.ONE_MONTH,
            encryption_key=self.kms_key
        )
        
        self.notifications_log_group = logs.LogGroup(
            self,
            "NotificationsLogGroup",
            log_group_name="/aws/lambda/asthma-guardian-v3-notifications",
            retention=logs.RetentionDays.ONE_MONTH,
            encryption_key=self.kms_key
        )
        
        self.data_ingestion_log_group = logs.LogGroup(
            self,
            "DataIngestionLogGroup",
            log_group_name="/aws/lambda/asthma-guardian-v3-data-ingestion",
            retention=logs.RetentionDays.ONE_MONTH,
            encryption_key=self.kms_key
        )
        
        # Create SNS topic for alerts
        self.alerts_topic = sns.Topic(
            self,
            "AlertsTopic",
            topic_name="asthma-guardian-v3-alerts",
            display_name="Asthma Guardian v3 Alerts"
        )
        
        # Create CloudWatch alarms
        self.create_cloudwatch_alarms()
        
        # Create CloudWatch dashboard
        self.dashboard = cloudwatch.Dashboard(
            self,
            "MonitoringDashboard",
            dashboard_name="asthma-guardian-v3"
        )
        
        # Add widgets to dashboard
        self.dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="API Gateway Metrics",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/ApiGateway",
                        metric_name="Count",
                        dimensions_map={"ApiName": "asthma-guardian-v3-api"}
                    )
                ],
                width=12,
                height=6
            )
        )
        
        # Create EventBridge rule for scheduled data ingestion
        self.data_ingestion_rule = events.Rule(
            self,
            "DataIngestionRule",
            description="Trigger data ingestion every hour",
            schedule=events.Schedule.rate(Duration.hours(1))
        )
        
        # Add Lambda function as target
        self.data_ingestion_rule.add_target(
            targets.LambdaFunction(self.data_ingestion_lambda)
        )
        
        # Outputs
        CfnOutput(
            self,
            "ApiGatewayUrl",
            value=self.api.url,
            description="API Gateway URL"
        )
        
        CfnOutput(
            self,
            "CloudFrontDomainName",
            value=self.distribution.domain_name,
            description="CloudFront distribution domain name"
        )
        
        CfnOutput(
            self,
            "WebsiteBucketName",
            value=self.website_bucket.bucket_name,
            description="Name of the S3 bucket for website hosting"
        )
    
    def create_cloudwatch_alarms(self):
        """Create CloudWatch alarms for monitoring and alerting."""
        
        # Lambda error rate alarm
        self.lambda_error_alarm = cloudwatch.Alarm(
            self,
            "LambdaErrorAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/Lambda",
                metric_name="Errors",
                dimensions_map={
                    "FunctionName": self.air_quality_lambda.function_name
                }
            ),
            threshold=5,
            evaluation_periods=2,
            alarm_description="Lambda function error rate is high"
        )
        self.lambda_error_alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alerts_topic))
        
        # Lambda duration alarm
        self.lambda_duration_alarm = cloudwatch.Alarm(
            self,
            "LambdaDurationAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/Lambda",
                metric_name="Duration",
                dimensions_map={
                    "FunctionName": self.air_quality_lambda.function_name
                }
            ),
            threshold=30000,  # 30 seconds
            evaluation_periods=2,
            alarm_description="Lambda function duration is high"
        )
        self.lambda_duration_alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alerts_topic))
        
        # API Gateway 4XX error alarm
        self.api_4xx_alarm = cloudwatch.Alarm(
            self,
            "Api4XXAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ApiGateway",
                metric_name="4XXError",
                dimensions_map={
                    "ApiName": self.api.rest_api_name
                }
            ),
            threshold=10,
            evaluation_periods=2,
            alarm_description="API Gateway 4XX error rate is high"
        )
        self.api_4xx_alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alerts_topic))
        
        # API Gateway 5XX error alarm
        self.api_5xx_alarm = cloudwatch.Alarm(
            self,
            "Api5XXAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ApiGateway",
                metric_name="5XXError",
                dimensions_map={
                    "ApiName": self.api.rest_api_name
                }
            ),
            threshold=5,
            evaluation_periods=1,
            alarm_description="API Gateway 5XX error rate is high"
        )
        self.api_5xx_alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alerts_topic))
        
        # DynamoDB throttled requests alarm
        self.dynamodb_throttle_alarm = cloudwatch.Alarm(
            self,
            "DynamoDBThrottleAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/DynamoDB",
                metric_name="ThrottledRequests",
                dimensions_map={
                    "TableName": self.users_table.table_name
                }
            ),
            threshold=1,
            evaluation_periods=1,
            alarm_description="DynamoDB throttled requests detected"
        )
        self.dynamodb_throttle_alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alerts_topic))
        
        # CloudFront error rate alarm
        self.cloudfront_error_alarm = cloudwatch.Alarm(
            self,
            "CloudFrontErrorAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/CloudFront",
                metric_name="4xxErrorRate",
                dimensions_map={
                    "DistributionId": self.distribution.distribution_id
                }
            ),
            threshold=5,
            evaluation_periods=2,
            alarm_description="CloudFront error rate is high"
        )
        self.cloudfront_error_alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alerts_topic))


def main():
    """Main CDK application entry point."""
    app = App()
    
    # Get environment variables
    env_name = os.getenv('ENVIRONMENT', 'dev')
    aws_account = os.getenv('AWS_ACCOUNT_ID')
    aws_region = os.getenv('AWS_REGION', 'ap-southeast-2')
    
    # Create environment object
    env = Environment(account=aws_account, region=aws_region)
    
    # Create main stack
    AsthmaGuardianV3Stack(
        app,
        f"AsthmaGuardianV3-{env_name}",
        env=env
    )
    
    # Add tags to all resources
    app.node.add_metadata("cdk:tags", {
        "Project": "AsthmaGuardianV3",
        "Environment": env_name,
        "ManagedBy": "CDK"
    })
    
    app.synth()


if __name__ == "__main__":
    main()
