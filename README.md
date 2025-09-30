# Asthma Guardian v3

A personalized web application that helps people with asthma in NSW stay safer on poor air quality days by providing real-time air quality data, personalized guidance, and proactive notifications.

## Overview

Asthma Guardian v3 is built using AWS CDK with Python 3.12 and provides:
- Real-time air quality data ingestion from NSW Government feeds
- Personalized user profiles with asthma severity levels
- LLM-powered guidance using AWS Bedrock AgentCore
- Proactive notification system with early warnings
- Responsive web application with accessibility compliance

## Architecture

- **Frontend**: React with TypeScript, hosted on S3 with CloudFront
- **Backend**: Python 3.12 with FastAPI, deployed as Lambda functions
- **Database**: DynamoDB for user data and air quality data
- **API**: API Gateway with JWT authentication
- **AI**: AWS Bedrock AgentCore for personalized guidance
- **Monitoring**: CloudWatch, X-Ray, and comprehensive logging

## Prerequisites

- Python 3.12+
- Node.js 18+
- AWS CLI v2
- AWS CDK CLI
- Git

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd asthma-guardian-v3
   ```

2. **Set up Python environment**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials and configuration
   ```

4. **Bootstrap CDK (first time only)**
   ```bash
   cdk bootstrap
   ```

5. **Deploy infrastructure**
   ```bash
   cdk deploy --all
   ```

## Development

### Project Structure

```
asthma-guardian-v3/
├── infrastructure/          # CDK infrastructure code
│   ├── stacks/             # CDK stacks
│   ├── constructs/         # Reusable CDK constructs
│   └── app.py             # CDK app entry point
├── frontend/              # React application
├── backend/               # Python API services
├── tests/                 # Test suites
└── docs/                  # Documentation
```

### Available Commands

- `cdk synth` - Synthesize CloudFormation templates
- `cdk deploy --all` - Deploy all stacks
- `cdk destroy --all` - Destroy all stacks
- `cdk diff` - Show differences between deployed and current state
- `pytest` - Run tests
- `black .` - Format Python code
- `flake8 .` - Lint Python code

## Environment Variables

See `.env.example` for all required environment variables.

## Security

- All data encrypted at rest and in transit
- VPC with private subnets for backend services
- IAM roles with least privilege principle
- WAF protection for API endpoints
- HIPAA compliance considerations for health data

## Monitoring

- CloudWatch metrics and logs
- X-Ray tracing for distributed systems
- Custom dashboards for key metrics
- Automated alerting for critical issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please open an issue in the GitHub repository.
