"""
Web App Stack for Asthma Guardian v3

This stack creates the infrastructure for hosting the React frontend application
including S3 bucket, CloudFront distribution, and related resources.
"""

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_route53 as route53,
    aws_certificatemanager as acm,
    CfnOutput,
    RemovalPolicy
)
from constructs import Construct


class WebAppStack(Stack):
    """Stack for hosting the React frontend application."""
    
    def __init__(self, scope: Construct, construct_id: str, env_name: str, backend_stack=None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.env_name = env_name
        self.backend_stack = backend_stack
        
        # Create S3 bucket for static website hosting
        self.website_bucket = s3.Bucket(
            self,
            "WebsiteBucket",
            bucket_name=f"asthma-guardian-v3-website-{env_name}",
            website_index_document="index.html",
            website_error_document="error.html",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        # Create CloudFront distribution
        self.distribution = cloudfront.Distribution(
            self,
            "WebsiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(self.website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                compress=True
            ),
            additional_behaviors={
                "/api/*": cloudfront.BehaviorOptions(
                    origin=origins.HttpOrigin(
                        f"api-{env_name}.asthmaguardian.nsw.gov.au",
                        protocol=cloudfront.OriginProtocol.HTTPS
                    ),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED
                )
            },
            domain_names=[f"{env_name}.asthmaguardian.nsw.gov.au"],
            certificate=None,  # Will be added when domain is configured
            price_class=cloudfront.PriceClass.PRICE_CLASS_100
        )
        
        # Outputs
        CfnOutput(
            self,
            "WebsiteBucketName",
            value=self.website_bucket.bucket_name,
            description="Name of the S3 bucket for website hosting"
        )
        
        CfnOutput(
            self,
            "CloudFrontDistributionId",
            value=self.distribution.distribution_id,
            description="CloudFront distribution ID"
        )
        
        CfnOutput(
            self,
            "CloudFrontDomainName",
            value=self.distribution.domain_name,
            description="CloudFront distribution domain name"
        )
