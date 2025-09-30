"""
DynamoDB Construct for Asthma Guardian v3

This construct creates reusable DynamoDB table configurations
with common settings and GSI patterns.
"""

from aws_cdk import (
    aws_dynamodb as dynamodb,
    RemovalPolicy
)
from constructs import Construct


class DynamoDBConstruct(Construct):
    """Reusable DynamoDB construct."""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
    
    def create_table(
        self,
        table_name: str,
        partition_key: dynamodb.Attribute,
        sort_key: dynamodb.Attribute = None,
        gsi_configs: list = None
    ) -> dynamodb.Table:
        """Create a DynamoDB table with common configuration."""
        
        table = dynamodb.Table(
            self,
            table_name,
            table_name=table_name,
            partition_key=partition_key,
            sort_key=sort_key,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Add GSIs if provided
        if gsi_configs:
            for gsi_config in gsi_configs:
                table.add_global_secondary_index(
                    index_name=gsi_config["index_name"],
                    partition_key=gsi_config["partition_key"],
                    sort_key=gsi_config.get("sort_key")
                )
        
        return table
