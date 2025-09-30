"""
Monitoring Construct for Asthma Guardian v3

This construct creates reusable monitoring configurations
including CloudWatch logs, metrics, and alarms.
"""

from aws_cdk import (
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_sns as sns
)
from constructs import Construct


class MonitoringConstruct(Construct):
    """Reusable monitoring construct."""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
    
    def create_log_group(self, log_group_name: str, retention_days: int = 30) -> logs.LogGroup:
        """Create a CloudWatch log group with common configuration."""
        
        return logs.LogGroup(
            self,
            log_group_name,
            log_group_name=log_group_name,
            retention=logs.RetentionDays(retention_days)
        )
    
    def create_sns_topic(self, topic_name: str, display_name: str = None) -> sns.Topic:
        """Create an SNS topic for notifications."""
        
        return sns.Topic(
            self,
            topic_name,
            topic_name=topic_name,
            display_name=display_name or topic_name
        )
