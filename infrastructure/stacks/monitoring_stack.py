"""
Monitoring Stack for Asthma Guardian v3

This stack creates the monitoring infrastructure including
CloudWatch logs, metrics, alarms, and X-Ray tracing.
"""

from aws_cdk import (
    Stack,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
    aws_sns as sns,
    CfnOutput
)
from constructs import Construct


class MonitoringStack(Stack):
    """Stack for monitoring infrastructure."""
    
    def __init__(self, scope: Construct, construct_id: str, env_name: str, backend_stack=None, web_app_stack=None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.env_name = env_name
        self.backend_stack = backend_stack
        self.web_app_stack = web_app_stack
        
        # Create SNS topic for alerts
        self.alerts_topic = sns.Topic(
            self,
            "AlertsTopic",
            topic_name=f"asthma-guardian-v3-alerts-{env_name}",
            display_name=f"Asthma Guardian v3 Alerts - {env_name}"
        )
        
        # Create CloudWatch log groups
        self.api_log_group = logs.LogGroup(
            self,
            "ApiLogGroup",
            log_group_name=f"/aws/apigateway/asthma-guardian-v3-api-{env_name}",
            retention=logs.RetentionDays.ONE_MONTH
        )
        
        self.lambda_log_group = logs.LogGroup(
            self,
            "LambdaLogGroup",
            log_group_name=f"/aws/lambda/asthma-guardian-v3-{env_name}",
            retention=logs.RetentionDays.ONE_MONTH
        )
        
        # Create CloudWatch dashboard
        self.dashboard = cloudwatch.Dashboard(
            self,
            "MonitoringDashboard",
            dashboard_name=f"asthma-guardian-v3-{env_name}"
        )
        
        # Add widgets to dashboard
        self.dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="API Gateway Metrics",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/ApiGateway",
                        metric_name="Count",
                        dimensions_map={"ApiName": f"asthma-guardian-v3-api-{env_name}"}
                    )
                ],
                width=12,
                height=6
            ),
            cloudwatch.GraphWidget(
                title="Lambda Metrics",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/Lambda",
                        metric_name="Invocations",
                        dimensions_map={"FunctionName": f"asthma-guardian-v3-{env_name}"}
                    )
                ],
                width=12,
                height=6
            )
        )
        
        # Create CloudWatch alarms
        self.error_alarm = cloudwatch.Alarm(
            self,
            "ErrorAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/ApiGateway",
                metric_name="4XXError",
                dimensions_map={"ApiName": f"asthma-guardian-v3-api-{env_name}"}
            ),
            threshold=10,
            evaluation_periods=2,
            alarm_description="High error rate in API Gateway"
        )
        
        self.error_alarm.add_alarm_action(
            cloudwatch_actions.SnsAction(self.alerts_topic)
        )
        
        # Outputs
        CfnOutput(
            self,
            "AlertsTopicArn",
            value=self.alerts_topic.topic_arn,
            description="SNS topic ARN for alerts"
        )
        
        CfnOutput(
            self,
            "DashboardUrl",
            value=f"https://console.aws.amazon.com/cloudwatch/home?region={self.region}#dashboards:name={self.dashboard.dashboard_name}",
            description="CloudWatch dashboard URL"
        )
