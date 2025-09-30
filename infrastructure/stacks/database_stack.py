"""
Database Stack for Asthma Guardian v3

This stack creates the DynamoDB tables for storing user data,
air quality data, alerts, and guidance recommendations.
"""

from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    CfnOutput,
    RemovalPolicy
)
from constructs import Construct


class DatabaseStack(Stack):
    """Stack for DynamoDB tables."""
    
    def __init__(self, scope: Construct, construct_id: str, env_name: str, security_stack=None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.env_name = env_name
        self.security_stack = security_stack
        
        # Users table
        self.users_table = dynamodb.Table(
            self,
            "UsersTable",
            table_name=f"asthma-guardian-users-{env_name}",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Add GSI for email lookup
        self.users_table.add_global_secondary_index(
            index_name="EmailIndex",
            partition_key=dynamodb.Attribute(
                name="GSI1PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="GSI1SK",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # Air Quality Data table
        self.air_quality_table = dynamodb.Table(
            self,
            "AirQualityTable",
            table_name=f"asthma-guardian-air-quality-{env_name}",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            time_to_live_attribute="ttl",
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Add GSI for date-based queries
        self.air_quality_table.add_global_secondary_index(
            index_name="DateIndex",
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
            table_name=f"asthma-guardian-user-alerts-{env_name}",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
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
        
        # Guidance Recommendations table
        self.guidance_table = dynamodb.Table(
            self,
            "GuidanceTable",
            table_name=f"asthma-guardian-guidance-{env_name}",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
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
        
        # Outputs
        CfnOutput(
            self,
            "UsersTableName",
            value=self.users_table.table_name,
            description="Users table name"
        )
        
        CfnOutput(
            self,
            "AirQualityTableName",
            value=self.air_quality_table.table_name,
            description="Air quality table name"
        )
        
        CfnOutput(
            self,
            "UserAlertsTableName",
            value=self.user_alerts_table.table_name,
            description="User alerts table name"
        )
        
        CfnOutput(
            self,
            "GuidanceTableName",
            value=self.guidance_table.table_name,
            description="Guidance table name"
        )
