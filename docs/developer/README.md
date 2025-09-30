# Asthma Guardian v3 Developer Guide

## Overview

This guide provides comprehensive information for developers working on the Asthma Guardian v3 project, including architecture, development setup, coding standards, and contribution guidelines.

## Table of Contents

- [Architecture](#architecture)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [API Development](#api-development)
- [Frontend Development](#frontend-development)
- [Infrastructure Development](#infrastructure-development)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

## Architecture

### System Overview

Asthma Guardian v3 is a serverless web application built on AWS that helps people with asthma in NSW stay safer on poor air quality days.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Lambda        │
│   (React SPA)   │◄──►│   (REST API)    │◄──►│   Functions     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │   DynamoDB      │
         │                       │              │   (Database)    │
         │                       │              └─────────────────┘
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │   External      │
         │                       │              │   APIs          │
         │                       │              │   (NSW Gov)     │
         │                       │              └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   CloudFront    │    │   CloudWatch    │
│   (CDN)         │    │   (Monitoring)  │
└─────────────────┘    └─────────────────┘
```

### Technology Stack

- **Frontend**: React 18, TypeScript, Material-UI, Axios
- **Backend**: AWS Lambda (Python 3.12), API Gateway, DynamoDB
- **Infrastructure**: AWS CDK (Python), CloudFormation
- **Monitoring**: CloudWatch, X-Ray, SNS
- **Security**: WAF, VPC, IAM, KMS
- **CI/CD**: GitHub Actions

### Data Flow

1. **User Interaction**: User interacts with React frontend
2. **API Request**: Frontend makes API calls to API Gateway
3. **Lambda Processing**: API Gateway routes requests to Lambda functions
4. **Data Access**: Lambda functions query DynamoDB and external APIs
5. **Response**: Data flows back through the same path
6. **Monitoring**: All interactions are logged and monitored

## Development Setup

### Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **AWS CLI 2.0+**
- **AWS CDK 2.0+**
- **Docker** (optional)
- **Git**

### Local Development

1. **Clone Repository**
   ```bash
   git clone https://github.com/nsw-government/asthma-guardian-v3.git
   cd asthma-guardian-v3
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r tests/requirements.txt
   
   # Install CDK globally
   npm install -g aws-cdk
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit environment variables
   nano .env
   ```

### IDE Setup

#### VS Code

Install recommended extensions:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylint",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-azuretools.vscode-docker"
  ]
}
```

#### PyCharm

1. Open project in PyCharm
2. Configure Python interpreter to use virtual environment
3. Install plugins: AWS Toolkit, Docker

## Project Structure

```
asthma-guardian-v3/
├── app.py                          # CDK application entry point
├── requirements.txt                # Python dependencies
├── pytest.ini                     # Test configuration
├── run_tests.py                   # Test runner script
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── cdk.json                       # CDK configuration
├── frontend/                      # React frontend
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── api/                   # API client
│   │   ├── App.tsx               # Main app component
│   │   └── index.tsx             # Entry point
│   ├── public/                    # Static assets
│   ├── package.json              # Node dependencies
│   └── tsconfig.json             # TypeScript config
├── backend/                       # Lambda functions
│   └── lambda_functions/
│       ├── air_quality/          # Air quality API
│       ├── user_profile/         # User management
│       ├── guidance/             # AI guidance
│       ├── notifications/        # Notifications
│       └── data_ingestion/       # Data ingestion
├── tests/                         # Test suite
│   ├── infrastructure/           # CDK tests
│   ├── backend/                  # API tests
│   ├── frontend/                 # Component tests
│   └── integration/              # E2E tests
├── docs/                         # Documentation
│   ├── api/                      # API documentation
│   ├── deployment/               # Deployment guides
│   ├── developer/                # Developer guides
│   ├── user/                     # User guides
│   └── troubleshooting/          # Troubleshooting
└── specs/                        # Project specifications
    └── 001-build-an-always/
        ├── spec.md               # Feature specification
        ├── plan.md               # Implementation plan
        ├── tasks.md              # Task breakdown
        ├── data-model.md         # Data model
        └── contracts/            # API contracts
```

## Coding Standards

### Python

#### Code Style

- **Formatter**: Black
- **Linter**: Pylint
- **Type Hints**: Required for all functions
- **Docstrings**: Google style

```python
def process_air_quality_data(
    data: Dict[str, Any], 
    location: str
) -> AirQualityResponse:
    """
    Process raw air quality data and return formatted response.
    
    Args:
        data: Raw air quality data from external API
        location: Location identifier
        
    Returns:
        Formatted air quality response
        
    Raises:
        ValueError: If data is invalid
        APIError: If external API fails
    """
    # Implementation here
    pass
```

#### File Structure

```python
# Standard imports
import os
import json
from typing import Dict, Any, Optional

# Third-party imports
import boto3
from botocore.exceptions import ClientError

# Local imports
from .models import AirQualityData
from .exceptions import APIError

# Constants
DEFAULT_TIMEOUT = 30

# Classes and functions
class AirQualityProcessor:
    """Process air quality data."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dynamodb = boto3.resource('dynamodb')
```

### TypeScript/React

#### Code Style

- **Formatter**: Prettier
- **Linter**: ESLint
- **Type Safety**: Strict TypeScript
- **Components**: Functional components with hooks

```typescript
interface AirQualityProps {
  location: string;
  onDataUpdate: (data: AirQualityData) => void;
}

const AirQuality: React.FC<AirQualityProps> = ({ 
  location, 
  onDataUpdate 
}) => {
  const [data, setData] = useState<AirQualityData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.airQuality.getCurrent({ location });
        setData(response.data);
        onDataUpdate(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [location, onDataUpdate]);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!data) return <Alert severity="info">No data available</Alert>;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Air Quality: {data.quality_rating}</Typography>
        <Typography variant="body1">AQI: {data.aqi}</Typography>
      </CardContent>
    </Card>
  );
};

export default AirQuality;
```

#### File Structure

```typescript
// types/api.ts
export interface AirQualityData {
  aqi: number;
  quality_rating: string;
  location: string;
  timestamp: string;
}

// components/AirQuality.tsx
import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import { api } from '../api/client';
import { AirQualityData } from '../types/api';

// Component implementation
```

### CDK/Infrastructure

#### Code Style

- **Naming**: PascalCase for constructs, camelCase for properties
- **Comments**: Explain complex infrastructure decisions
- **Organization**: Group related resources

```python
class AsthmaGuardianV3Stack(Stack):
    """Main stack for Asthma Guardian v3 infrastructure."""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
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
                # ... other subnets
            ]
        )
```

## Testing

### Test Structure

```
tests/
├── infrastructure/           # CDK infrastructure tests
│   └── test_stacks.py
├── backend/                 # API and Lambda tests
│   └── test_api.py
├── frontend/                # React component tests
│   └── test_components.tsx
├── integration/             # End-to-end tests
│   └── test_endpoints.py
└── requirements.txt         # Test dependencies
```

### Running Tests

```bash
# Run all tests
python run_tests.py --type all

# Run specific test types
python run_tests.py --type unit
python run_tests.py --type frontend
python run_tests.py --type integration

# Run with coverage
python run_tests.py --type coverage
```

### Test Guidelines

1. **Unit Tests**: Test individual functions and components
2. **Integration Tests**: Test API endpoints and external integrations
3. **E2E Tests**: Test complete user workflows
4. **Coverage**: Maintain >90% test coverage
5. **Mocking**: Mock external dependencies

## API Development

### Lambda Function Structure

```python
# backend/lambda_functions/air_quality/handler.py
import json
import os
import boto3
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
air_quality_table = dynamodb.Table(os.environ['AIR_QUALITY_TABLE_NAME'])

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for air quality API endpoints.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Parse request
        path = event.get('path', '')
        method = event.get('httpMethod', '')
        query_params = event.get('queryStringParameters', {})
        
        # Route to appropriate handler
        if method == 'GET' and '/current' in path:
            return handle_current_air_quality(query_params)
        elif method == 'GET' and '/forecast' in path:
            return handle_forecast(query_params)
        elif method == 'GET' and '/history' in path:
            return handle_history(query_params)
        else:
            return create_error_response(404, 'Not Found')
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return create_error_response(500, 'Internal Server Error')

def handle_current_air_quality(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle current air quality request."""
    # Implementation here
    pass

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': {'message': message}})
    }
```

### API Gateway Integration

```python
# In CDK stack
api = apigateway.RestApi(
    self,
    "ApiGateway",
    rest_api_name="asthma-guardian-v3-api",
    description="API Gateway for Asthma Guardian v3",
    default_cors_preflight_options=apigateway.CorsOptions(
        allow_origins=apigateway.Cors.ALL_ORIGINS,
        allow_methods=apigateway.Cors.ALL_METHODS,
        allow_headers=["Content-Type", "Authorization"]
    )
)

# Add Lambda integration
air_quality_integration = apigateway.LambdaIntegration(
    air_quality_lambda,
    request_templates={"application/json": '{"statusCode": "200"}'}
)

# Add routes
air_quality = api_resource.add_resource("air-quality")
air_quality.add_method("GET", air_quality_integration)
```

## Frontend Development

### Component Development

```typescript
// components/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, CircularProgress } from '@mui/material';
import { api } from '../api/client';
import { AirQualityData } from '../types/api';

interface DashboardProps {
  userId?: string;
}

const Dashboard: React.FC<DashboardProps> = ({ userId }) => {
  const [airQualityData, setAirQualityData] = useState<AirQualityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAirQualityData();
  }, []);

  const loadAirQualityData = async () => {
    try {
      setLoading(true);
      const response = await api.airQuality.getCurrent({ postcode: '2000' });
      setAirQualityData(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;
  if (!airQualityData) return <Typography>No data available</Typography>;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Current Air Quality</Typography>
        <Typography variant="body1">
          AQI: {airQualityData.aqi} - {airQualityData.quality_rating}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default Dashboard;
```

### State Management

```typescript
// hooks/useAirQuality.ts
import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { AirQualityData } from '../types/api';

export const useAirQuality = (location: string) => {
  const [data, setData] = useState<AirQualityData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.airQuality.getCurrent({ location });
      setData(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (location) {
      fetchData();
    }
  }, [location]);

  return { data, loading, error, refetch: fetchData };
};
```

## Infrastructure Development

### CDK Constructs

```python
# infrastructure/constructs/air_quality_construct.py
from aws_cdk import Stack, aws_lambda as lambda_, aws_dynamodb as dynamodb
from constructs import Construct

class AirQualityConstruct(Construct):
    """Construct for air quality related resources."""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create DynamoDB table
        self.table = dynamodb.Table(
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
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        
        # Create Lambda function
        self.function = lambda_.Function(
            self,
            "AirQualityFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=lambda_.Code.from_asset("backend/lambda_functions/air_quality"),
            environment={
                "AIR_QUALITY_TABLE_NAME": self.table.table_name
            }
        )
        
        # Grant permissions
        self.table.grant_read_write_data(self.function)
```

### Environment Configuration

```python
# infrastructure/config/environment.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class EnvironmentConfig:
    """Environment configuration."""
    name: str
    region: str
    account_id: str
    domain_name: str
    api_base_url: str
    
    @classmethod
    def from_env(cls, env_name: str) -> 'EnvironmentConfig':
        """Create configuration from environment variables."""
        return cls(
            name=env_name,
            region=os.getenv('AWS_REGION', 'ap-southeast-2'),
            account_id=os.getenv('AWS_ACCOUNT_ID'),
            domain_name=f"asthmaguardian-{env_name}.nsw.gov.au",
            api_base_url=f"https://api-{env_name}.asthmaguardian.nsw.gov.au/api"
        )
```

## Contributing

### Development Workflow

1. **Fork Repository**
   ```bash
   git clone https://github.com/your-username/asthma-guardian-v3.git
   cd asthma-guardian-v3
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow coding standards
   - Write tests
   - Update documentation

4. **Test Changes**
   ```bash
   python run_tests.py --type all
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Pull Request Guidelines

- **Title**: Use conventional commits format
- **Description**: Explain what and why
- **Tests**: Include test coverage
- **Documentation**: Update relevant docs
- **Review**: Request appropriate reviewers

### Code Review Process

1. **Automated Checks**: CI/CD pipeline runs tests
2. **Peer Review**: At least one reviewer required
3. **Security Review**: For security-related changes
4. **Approval**: All checks must pass

## Troubleshooting

### Common Issues

#### CDK Issues

```bash
# Bootstrap CDK
cdk bootstrap aws://ACCOUNT-NUMBER/REGION

# Check CDK version
cdk --version

# Synthesize without deploying
cdk synth
```

#### Lambda Issues

```bash
# Check Lambda logs
aws logs tail /aws/lambda/function-name --follow

# Test Lambda locally
python -m pytest tests/backend/test_api.py -v
```

#### Frontend Issues

```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check TypeScript errors
npm run type-check
```

#### Database Issues

```bash
# Check DynamoDB table
aws dynamodb describe-table --table-name asthma-guardian-users

# Query table
aws dynamodb scan --table-name asthma-guardian-users --limit 10
```

### Debugging

#### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### CloudWatch Insights

```sql
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
```

#### X-Ray Tracing

```python
from aws_xray_sdk.core import xray_recorder

@xray_recorder.capture('process_data')
def process_data(data):
    # Implementation
    pass
```

## Support

- **Email**: dev@asthmaguardian.nsw.gov.au
- **Slack**: #asthma-guardian-dev
- **Documentation**: https://docs.asthmaguardian.nsw.gov.au
- **Issues**: GitHub Issues
