# Asthma Guardian v3 Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Asthma Guardian v3 application to AWS using CDK.

## Prerequisites

### Required Tools

- **AWS CLI** (v2.0+)
- **AWS CDK** (v2.0+)
- **Python** (3.12+)
- **Node.js** (18+)
- **Docker** (for containerized deployments)

### AWS Account Setup

1. **Create AWS Account**
   - Sign up for AWS account if you don't have one
   - Enable billing and set up payment method

2. **Configure AWS CLI**
   ```bash
   aws configure
   # Enter your Access Key ID, Secret Access Key, Region, and Output format
   ```

3. **Bootstrap CDK**
   ```bash
   cdk bootstrap aws://ACCOUNT-NUMBER/REGION
   ```

### Environment Variables

Create a `.env` file in the project root:

```bash
# AWS Configuration
AWS_ACCOUNT_ID=123456789012
AWS_REGION=ap-southeast-2
ENVIRONMENT=dev

# API Configuration
NSW_AIR_QUALITY_API_URL=https://api.airquality.nsw.gov.au
BOM_API_URL=https://api.bom.gov.au

# Email Configuration
SES_FROM_EMAIL=noreply@asthmaguardian.nsw.gov.au

# Frontend Configuration
REACT_APP_API_BASE_URL=https://api-dev.asthmaguardian.nsw.gov.au/api
```

## Deployment Steps

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/nsw-government/asthma-guardian-v3.git
cd asthma-guardian-v3

# Install Python dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 3. Deploy Infrastructure

```bash
# Synthesize CDK stack
cdk synth

# Deploy the stack
cdk deploy --all

# Or deploy specific stack
cdk deploy AsthmaGuardianV3-dev
```

### 4. Build and Deploy Frontend

```bash
# Build React application
cd frontend
npm run build

# Deploy to S3 (this will be done automatically by CDK)
# The build artifacts will be uploaded to the S3 bucket
```

### 5. Verify Deployment

```bash
# Check stack outputs
cdk list

# Get CloudFront URL
aws cloudformation describe-stacks \
  --stack-name AsthmaGuardianV3-dev \
  --query 'Stacks[0].Outputs'
```

## Environment-Specific Deployments

### Development Environment

```bash
# Deploy to development
ENVIRONMENT=dev cdk deploy AsthmaGuardianV3-dev
```

### Staging Environment

```bash
# Deploy to staging
ENVIRONMENT=staging cdk deploy AsthmaGuardianV3-staging
```

### Production Environment

```bash
# Deploy to production
ENVIRONMENT=prod cdk deploy AsthmaGuardianV3-prod
```

## Infrastructure Components

### Core Services

- **S3 Bucket**: Static website hosting
- **CloudFront**: CDN and SSL termination
- **API Gateway**: REST API endpoints
- **Lambda Functions**: Serverless compute
- **DynamoDB**: NoSQL database
- **VPC**: Network isolation
- **WAF**: Web application firewall

### Security

- **KMS**: Encryption keys
- **IAM**: Access control
- **Security Groups**: Network security
- **VPC**: Private subnets

### Monitoring

- **CloudWatch**: Logs and metrics
- **X-Ray**: Distributed tracing
- **SNS**: Alerting
- **CloudWatch Alarms**: Automated monitoring

## Configuration Management

### CDK Configuration

The CDK configuration is managed in `cdk.json`:

```json
{
  "app": "python app.py",
  "watch": {
    "include": ["**"],
    "exclude": [
      "README.md",
      "cdk*.json",
      "requirements*.txt",
      "source.bat",
      "**/__pycache__",
      "**/.venv"
    ]
  },
  "context": {
    "@aws-cdk/aws-lambda:recognizeLayerVersion": true,
    "@aws-cdk/core:checkSecretUsage": true,
    "@aws-cdk/core:target-partitions": ["aws", "aws-cn"],
    "@aws-cdk-containers/ecs-service-extensions:enableDefaultLogDriver": true,
    "@aws-cdk/aws-ec2:uniqueImdsv2TemplateName": true,
    "@aws-cdk/aws-ecs:arnFormatIncludesClusterName": true,
    "@aws-cdk/aws-iam:minimizePolicies": true,
    "@aws-cdk/core:validateSnapshotRemovalPolicy": true,
    "@aws-cdk/aws-codepipeline:crossAccountKeyAliasStackSafeResourceName": true,
    "@aws-cdk/aws-s3:createDefaultLoggingPolicy": true,
    "@aws-cdk/aws-sns-subscriptions:restrictSqsDescryption": true,
    "@aws-cdk/aws-apigateway:disableCloudWatchRole": true,
    "@aws-cdk/core:enablePartitionLiterals": true,
    "@aws-cdk/aws-events:eventsTargetQueueSameAccount": true,
    "@aws-cdk/aws-iam:standardizedServicePrincipals": true,
    "@aws-cdk/aws-ecs:disableExplicitDeploymentControllerForCircuitBreaker": true,
    "@aws-cdk/aws-iam:importedRoleStackSafeDefaultPolicyName": true,
    "@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy": true,
    "@aws-cdk/aws-route53-patters:useCertificate": true,
    "@aws-cdk/customresources:installLatestAwsSdkDefault": false,
    "@aws-cdk/aws-rds:databaseProxyUniqueResourceName": true,
    "@aws-cdk/aws-codedeploy:removeAlarmsFromDeploymentGroup": true,
    "@aws-cdk/aws-apigateway:authorizerChangeDeploymentLogicalId": true,
    "@aws-cdk/aws-ec2:launchTemplateDefaultUserData": true,
    "@aws-cdk/aws-secretsmanager:useAttachedSecretResourcePolicyForSecretTargetAttachments": true,
    "@aws-cdk/aws-redshift:columnId": true,
    "@aws-cdk/aws-stepfunctions-tasks:enableLogging": true,
    "@aws-cdk/aws-ec2:restrictDefaultSecurityGroup": true,
    "@aws-cdk/aws-apigateway:requestValidatorUniqueId": true,
    "@aws-cdk/aws-kms:aliasNameRef": true,
    "@aws-cdk/aws-autoscaling:generateLaunchTemplateInsteadOfLaunchConfig": true,
    "@aws-cdk/core:includePrefixInUniqueNameGeneration": true,
    "@aws-cdk/aws-efs:denyAnonymousAccess": true,
    "@aws-cdk/aws-opensearchservice:enableLogging": true,
    "@aws-cdk/aws-lambda:useLatestRuntimeVersion": true,
    "@aws-cdk/aws-ecs:enableExecuteCommandLogging": true,
    "@aws-cdk/aws-ec2:ebsDefaultGp3Volume": true,
    "@aws-cdk/aws-ecs:removeDefaultDeploymentAlarm": false,
    "@aws-cdk/aws-rds:auroraClusterChangeScopeOfInstanceParameterGroupWithEachParameters": true,
    "@aws-cdk/aws-appsync:useArnForSourceApiAssociationIdentifier": true,
    "@aws-cdk/aws-rds:preventRenderingDeprecatedCredentials": true,
    "@aws-cdk/aws-codepipeline-actions:useNewDefaultBranchForSourceAction": true,
    "@aws-cdk/aws-s3:autoDeletePolicy": true,
    "@aws-cdk/aws-lambda:recognizeVersionProps": true,
    "@aws-cdk/aws-cloudfront:defaultSecurityPolicyTLSv1.2_2021": true,
    "@aws-cdk/aws-apigateway:disableCloudWatchRole": true,
    "@aws-cdk/core:stackRelativeExports": true,
    "@aws-cdk/aws-rds:databaseProxyUniqueResourceName": true,
    "@aws-cdk/aws-codedeploy:removeAlarmsFromDeploymentGroup": true,
    "@aws-cdk/aws-apigateway:authorizerChangeDeploymentLogicalId": true,
    "@aws-cdk/aws-ec2:launchTemplateDefaultUserData": true,
    "@aws-cdk/aws-secretsmanager:useAttachedSecretResourcePolicyForSecretTargetAttachments": true,
    "@aws-cdk/aws-redshift:columnId": true,
    "@aws-cdk/aws-stepfunctions-tasks:enableLogging": true,
    "@aws-cdk/aws-ec2:restrictDefaultSecurityGroup": true,
    "@aws-cdk/aws-apigateway:requestValidatorUniqueId": true,
    "@aws-cdk/aws-kms:aliasNameRef": true,
    "@aws-cdk/aws-autoscaling:generateLaunchTemplateInsteadOfLaunchConfig": true,
    "@aws-cdk/core:includePrefixInUniqueNameGeneration": true,
    "@aws-cdk/aws-efs:denyAnonymousAccess": true,
    "@aws-cdk/aws-opensearchservice:enableLogging": true,
    "@aws-cdk/aws-lambda:useLatestRuntimeVersion": true,
    "@aws-cdk/aws-ecs:enableExecuteCommandLogging": true,
    "@aws-cdk/aws-ec2:ebsDefaultGp3Volume": true,
    "@aws-cdk/aws-ecs:removeDefaultDeploymentAlarm": false,
    "@aws-cdk/aws-rds:auroraClusterChangeScopeOfInstanceParameterGroupWithEachParameters": true,
    "@aws-cdk/aws-appsync:useArnForSourceApiAssociationIdentifier": true,
    "@aws-cdk/aws-rds:preventRenderingDeprecatedCredentials": true,
    "@aws-cdk/aws-codepipeline-actions:useNewDefaultBranchForSourceAction": true,
    "@aws-cdk/aws-s3:autoDeletePolicy": true,
    "@aws-cdk/aws-lambda:recognizeVersionProps": true,
    "@aws-cdk/aws-cloudfront:defaultSecurityPolicyTLSv1.2_2021": true,
    "@aws-cdk/aws-apigateway:disableCloudWatchRole": true,
    "@aws-cdk/core:stackRelativeExports": true
  }
}
```

### Environment-Specific Settings

Different environments can be configured by modifying the environment variables:

```bash
# Development
ENVIRONMENT=dev
AWS_REGION=ap-southeast-2
REACT_APP_API_BASE_URL=https://api-dev.asthmaguardian.nsw.gov.au/api

# Staging
ENVIRONMENT=staging
AWS_REGION=ap-southeast-2
REACT_APP_API_BASE_URL=https://api-staging.asthmaguardian.nsw.gov.au/api

# Production
ENVIRONMENT=prod
AWS_REGION=ap-southeast-2
REACT_APP_API_BASE_URL=https://api.asthmaguardian.nsw.gov.au/api
```

## CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Asthma Guardian v3

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py --type all

  deploy-dev:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-southeast-2
      - name: Deploy to development
        run: |
          ENVIRONMENT=dev cdk deploy --all --require-approval never

  deploy-prod:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-southeast-2
      - name: Deploy to production
        run: |
          ENVIRONMENT=prod cdk deploy --all --require-approval never
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check API health
curl https://api-dev.asthmaguardian.nsw.gov.au/api/health

# Check CloudFront distribution
aws cloudfront get-distribution --id DISTRIBUTION_ID

# Check Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `asthma-guardian`)]'
```

### Logs

```bash
# View API Gateway logs
aws logs tail /aws/apigateway/asthma-guardian-v3-api --follow

# View Lambda logs
aws logs tail /aws/lambda/asthma-guardian-v3-air-quality --follow

# View CloudFront logs
aws logs tail /aws/cloudfront/distribution/DISTRIBUTION_ID --follow
```

### Metrics

```bash
# Get CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=asthma-guardian-v3-api \
  --start-time 2024-12-19T00:00:00Z \
  --end-time 2024-12-19T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

## Troubleshooting

### Common Issues

1. **CDK Bootstrap Required**
   ```bash
   cdk bootstrap aws://ACCOUNT-NUMBER/REGION
   ```

2. **Permission Denied**
   - Check IAM permissions
   - Verify AWS credentials

3. **Stack Update Failed**
   ```bash
   cdk diff
   cdk deploy --force
   ```

4. **Frontend Build Fails**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

### Rollback

```bash
# Rollback to previous version
cdk rollback AsthmaGuardianV3-dev

# Or delete and redeploy
cdk destroy AsthmaGuardianV3-dev
cdk deploy AsthmaGuardianV3-dev
```

## Security Considerations

### Secrets Management

- Use AWS Secrets Manager for sensitive data
- Never commit secrets to version control
- Rotate API keys regularly

### Network Security

- VPC with private subnets
- Security groups with minimal access
- WAF protection enabled

### Data Protection

- Encryption at rest and in transit
- KMS key management
- Regular security audits

## Support

For deployment issues:
- **Email**: devops@asthmaguardian.nsw.gov.au
- **Documentation**: https://docs.asthmaguardian.nsw.gov.au
- **Status Page**: https://status.asthmaguardian.nsw.gov.au
