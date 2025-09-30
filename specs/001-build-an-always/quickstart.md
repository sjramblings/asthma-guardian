# Quickstart Guide: Asthma Guardian v3 CDK Infrastructure

## Prerequisites

### Required Software
- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **AWS CLI v2** - [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **AWS CDK CLI** - Install with `npm install -g aws-cdk`
- **Git** - [Download](https://git-scm.com/downloads)

### AWS Account Setup
1. Create an AWS account if you don't have one
2. Configure AWS CLI with your credentials:
   ```bash
   aws configure
   ```
3. Bootstrap CDK in your AWS account:
   ```bash
   cdk bootstrap
   ```

## Project Setup

### 1. Clone and Initialize
```bash
# Clone the repository
git clone <repository-url>
cd asthma-guardian-v3

# Create Python virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**
```bash
# AWS Configuration
AWS_REGION=ap-southeast-2
AWS_ACCOUNT_ID=123456789012

# Application Configuration
APP_NAME=asthma-guardian-v3
ENVIRONMENT=dev

# Database Configuration
DYNAMODB_TABLE_PREFIX=asthma-guardian

# API Configuration
API_DOMAIN=api-dev.asthmaguardian.nsw.gov.au
FRONTEND_DOMAIN=dev.asthmaguardian.nsw.gov.au

# Monitoring
LOG_LEVEL=INFO
ENABLE_XRAY=true
```

### 3. Install CDK Dependencies
```bash
# Install Python CDK dependencies
pip install aws-cdk-lib constructs

# Install Node.js dependencies for CDK
npm install
```

## CDK Project Structure

```
asthma-guardian-v3/
├── infrastructure/
│   ├── stacks/
│   │   ├── __init__.py
│   │   ├── web_app_stack.py      # Frontend hosting
│   │   ├── backend_stack.py      # API and services
│   │   ├── database_stack.py     # DynamoDB tables
│   │   ├── monitoring_stack.py   # CloudWatch and X-Ray
│   │   └── security_stack.py     # IAM and security
│   ├── constructs/
│   │   ├── __init__.py
│   │   ├── api_gateway_construct.py
│   │   ├── lambda_construct.py
│   │   └── dynamodb_construct.py
│   ├── app.py                    # CDK app entry point
│   └── config.py                 # Configuration management
├── frontend/                     # React application
├── backend/                      # Python API services
├── tests/                        # CDK and application tests
├── cdk.json                      # CDK configuration
├── requirements.txt              # Python dependencies
└── package.json                  # Node.js dependencies
```

## Deployment

### 1. Synthesize CDK Templates
```bash
# Check CDK configuration
cdk doctor

# Synthesize CloudFormation templates
cdk synth

# List all stacks
cdk list
```

### 2. Deploy Infrastructure
```bash
# Deploy all stacks
cdk deploy --all

# Deploy specific stack
cdk deploy AsthmaGuardianV3-DatabaseStack

# Deploy with specific parameters
cdk deploy --all --parameters Environment=prod
```

### 3. Verify Deployment
```bash
# Check stack status
aws cloudformation describe-stacks --stack-name AsthmaGuardianV3-WebAppStack

# List deployed resources
aws cloudformation list-stack-resources --stack-name AsthmaGuardianV3-WebAppStack
```

## Development Workflow

### 1. Local Development
```bash
# Start local development server
cd frontend
npm start

# Start backend API locally
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 2. Testing
```bash
# Run CDK tests
pytest tests/infrastructure/

# Run application tests
pytest tests/backend/
npm test  # Frontend tests
```

### 3. Code Quality
```bash
# Format Python code
black infrastructure/ backend/

# Lint Python code
flake8 infrastructure/ backend/

# Format TypeScript code
cd frontend
npm run format

# Lint TypeScript code
npm run lint
```

## Monitoring and Debugging

### 1. CloudWatch Logs
```bash
# View Lambda function logs
aws logs tail /aws/lambda/asthma-guardian-api --follow

# View API Gateway logs
aws logs tail /aws/apigateway/asthma-guardian-api --follow
```

### 2. X-Ray Tracing
- Enable X-Ray tracing in the CDK configuration
- View traces in the AWS X-Ray console
- Use X-Ray SDK for custom instrumentation

### 3. CloudWatch Metrics
- Monitor API Gateway metrics
- Track Lambda function performance
- Set up alarms for critical metrics

## Common Commands

### CDK Commands
```bash
# Deploy all stacks
cdk deploy --all

# Deploy specific stack
cdk deploy AsthmaGuardianV3-WebAppStack

# Destroy all stacks
cdk destroy --all

# Diff changes
cdk diff

# List all stacks
cdk list

# Show stack outputs
cdk outputs
```

### AWS CLI Commands
```bash
# List all stacks
aws cloudformation list-stacks

# Get stack outputs
aws cloudformation describe-stacks --stack-name AsthmaGuardianV3-WebAppStack --query 'Stacks[0].Outputs'

# Update stack
aws cloudformation update-stack --stack-name AsthmaGuardianV3-WebAppStack --template-body file://cdk.out/AsthmaGuardianV3-WebAppStack.template.json
```

## Troubleshooting

### Common Issues

#### 1. CDK Bootstrap Issues
```bash
# Re-bootstrap CDK
cdk bootstrap --force

# Check bootstrap status
aws cloudformation describe-stacks --stack-name CDKToolkit
```

#### 2. Permission Issues
```bash
# Check AWS credentials
aws sts get-caller-identity

# Update AWS credentials
aws configure
```

#### 3. Dependency Issues
```bash
# Update CDK dependencies
pip install --upgrade aws-cdk-lib constructs

# Clear CDK cache
rm -rf cdk.out/
```

#### 4. Stack Update Failures
```bash
# Check stack events
aws cloudformation describe-stack-events --stack-name AsthmaGuardianV3-WebAppStack

# Rollback stack
aws cloudformation cancel-update-stack --stack-name AsthmaGuardianV3-WebAppStack
```

## Next Steps

1. **Customize Configuration:** Update environment variables and CDK parameters
2. **Add Features:** Implement additional AWS services and constructs
3. **Set Up CI/CD:** Configure GitHub Actions or AWS CodePipeline
4. **Monitor Production:** Set up comprehensive monitoring and alerting
5. **Scale Infrastructure:** Implement auto-scaling and performance optimization

## Support

- **Documentation:** [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- **Issues:** Create GitHub issues for bugs and feature requests
- **Discussions:** Use GitHub Discussions for questions and community support
