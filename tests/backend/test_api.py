"""
Backend API Tests

This module contains tests for the backend API endpoints and Lambda functions.
"""

import pytest
import json
import boto3
from moto import mock_dynamodb, mock_lambda, mock_apigateway
from unittest.mock import patch, MagicMock


class TestAirQualityAPI:
    """Test cases for Air Quality API endpoints."""
    
    @mock_dynamodb
    def test_air_quality_current_endpoint(self):
        """Test GET /api/air-quality/current endpoint."""
        # Mock DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='asthma-guardian-air-quality',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Add test data
        table.put_item(Item={
            'PK': 'LOCATION#2000',
            'SK': 'CURRENT',
            'aqi': 45,
            'quality_rating': 'good',
            'timestamp': '2024-12-19T10:30:00Z'
        })
        
        # Mock Lambda function
        with patch('boto3.resource') as mock_resource:
            mock_resource.return_value = dynamodb
            
            # Import and test the handler
            from backend.lambda_functions.air_quality.handler import handler
            
            event = {
                'httpMethod': 'GET',
                'path': '/api/air-quality/current',
                'queryStringParameters': {'postcode': '2000'}
            }
            
            response = handler(event, {})
            
            assert response['statusCode'] == 200
            assert 'application/json' in response['headers']['Content-Type']
    
    @mock_dynamodb
    def test_air_quality_forecast_endpoint(self):
        """Test GET /api/air-quality/forecast endpoint."""
        # Mock DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='asthma-guardian-air-quality',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch('boto3.resource') as mock_resource:
            mock_resource.return_value = dynamodb
            
            from backend.lambda_functions.air_quality.handler import handler
            
            event = {
                'httpMethod': 'GET',
                'path': '/api/air-quality/forecast',
                'queryStringParameters': {'postcode': '2000'}
            }
            
            response = handler(event, {})
            
            assert response['statusCode'] == 200
    
    @mock_dynamodb
    def test_air_quality_history_endpoint(self):
        """Test GET /api/air-quality/history endpoint."""
        # Mock DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='asthma-guardian-air-quality',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch('boto3.resource') as mock_resource:
            mock_resource.return_value = dynamodb
            
            from backend.lambda_functions.air_quality.handler import handler
            
            event = {
                'httpMethod': 'GET',
                'path': '/api/air-quality/history',
                'queryStringParameters': {
                    'postcode': '2000',
                    'start_date': '2024-12-01',
                    'end_date': '2024-12-19'
                }
            }
            
            response = handler(event, {})
            
            assert response['statusCode'] == 200


class TestUserProfileAPI:
    """Test cases for User Profile API endpoints."""
    
    @mock_dynamodb
    def test_create_user_profile(self):
        """Test POST /api/users endpoint."""
        # Mock DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='asthma-guardian-users',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch('boto3.resource') as mock_resource:
            mock_resource.return_value = dynamodb
            
            from backend.lambda_functions.user_profile.handler import handler
            
            event = {
                'httpMethod': 'POST',
                'path': '/api/users',
                'body': json.dumps({
                    'email': 'test@example.com',
                    'asthma_severity': 'moderate',
                    'location': {
                        'postcode': '2000',
                        'latitude': -33.8688,
                        'longitude': 151.2093
                    }
                })
            }
            
            response = handler(event, {})
            
            assert response['statusCode'] == 200
    
    @mock_dynamodb
    def test_get_user_profile(self):
        """Test GET /api/users/{user_id} endpoint."""
        # Mock DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='asthma-guardian-users',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Add test user
        table.put_item(Item={
            'PK': 'USER#test-user-id',
            'SK': 'PROFILE',
            'email': 'test@example.com',
            'asthma_severity': 'moderate'
        })
        
        with patch('boto3.resource') as mock_resource:
            mock_resource.return_value = dynamodb
            
            from backend.lambda_functions.user_profile.handler import handler
            
            event = {
                'httpMethod': 'GET',
                'path': '/api/users/test-user-id',
                'pathParameters': {'user_id': 'test-user-id'}
            }
            
            response = handler(event, {})
            
            assert response['statusCode'] == 200
    
    @mock_dynamodb
    def test_update_user_profile(self):
        """Test PUT /api/users/{user_id} endpoint."""
        # Mock DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='asthma-guardian-users',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch('boto3.resource') as mock_resource:
            mock_resource.return_value = dynamodb
            
            from backend.lambda_functions.user_profile.handler import handler
            
            event = {
                'httpMethod': 'PUT',
                'path': '/api/users/test-user-id',
                'pathParameters': {'user_id': 'test-user-id'},
                'body': json.dumps({
                    'asthma_severity': 'severe',
                    'location': {
                        'postcode': '2000'
                    }
                })
            }
            
            response = handler(event, {})
            
            assert response['statusCode'] == 200


class TestGuidanceAPI:
    """Test cases for Guidance API endpoints."""
    
    @mock_dynamodb
    @patch('boto3.client')
    def test_get_guidance(self, mock_boto_client):
        """Test GET /api/guidance/{user_id} endpoint."""
        # Mock Bedrock client
        mock_bedrock = MagicMock()
        mock_bedrock.invoke_model.return_value = {
            'body': MagicMock()
        }
        mock_bedrock.invoke_model.return_value['body'].read.return_value = json.dumps({
            'content': [{'text': 'Test guidance response'}]
        }).encode()
        mock_boto_client.return_value = mock_bedrock
        
        # Mock DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        users_table = dynamodb.create_table(
            TableName='asthma-guardian-users',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        air_quality_table = dynamodb.create_table(
            TableName='asthma-guardian-air-quality',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        guidance_table = dynamodb.create_table(
            TableName='asthma-guardian-guidance',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch('boto3.resource') as mock_resource:
            mock_resource.return_value = dynamodb
            
            from backend.lambda_functions.guidance.handler import handler
            
            event = {
                'httpMethod': 'GET',
                'path': '/api/guidance/test-user-id',
                'pathParameters': {'user_id': 'test-user-id'}
            }
            
            response = handler(event, {})
            
            assert response['statusCode'] == 200


class TestNotificationsAPI:
    """Test cases for Notifications API endpoints."""
    
    @mock_dynamodb
    @patch('boto3.client')
    def test_send_notification(self, mock_boto_client):
        """Test POST /api/notifications endpoint."""
        # Mock SNS client
        mock_sns = MagicMock()
        mock_sns.publish.return_value = {'MessageId': 'test-message-id'}
        mock_boto_client.return_value = mock_sns
        
        # Mock DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        users_table = dynamodb.create_table(
            TableName='asthma-guardian-users',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        alerts_table = dynamodb.create_table(
            TableName='asthma-guardian-user-alerts',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch('boto3.resource') as mock_resource:
            mock_resource.return_value = dynamodb
            
            from backend.lambda_functions.notifications.handler import handler
            
            event = {
                'httpMethod': 'POST',
                'path': '/api/notifications',
                'body': json.dumps({
                    'user_id': 'test-user-id',
                    'message': 'Test notification',
                    'subject': 'Test Subject',
                    'type': 'alert'
                })
            }
            
            response = handler(event, {})
            
            assert response['statusCode'] == 200
    
    @mock_dynamodb
    def test_get_notifications(self):
        """Test GET /api/notifications/{user_id} endpoint."""
        # Mock DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        alerts_table = dynamodb.create_table(
            TableName='asthma-guardian-user-alerts',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch('boto3.resource') as mock_resource:
            mock_resource.return_value = dynamodb
            
            from backend.lambda_functions.notifications.handler import handler
            
            event = {
                'httpMethod': 'GET',
                'path': '/api/notifications/test-user-id',
                'pathParameters': {'user_id': 'test-user-id'}
            }
            
            response = handler(event, {})
            
            assert response['statusCode'] == 200


class TestDataIngestionAPI:
    """Test cases for Data Ingestion service."""
    
    @mock_dynamodb
    @patch('requests.get')
    def test_data_ingestion_lambda(self, mock_requests_get):
        """Test data ingestion Lambda function."""
        # Mock external API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': [{
                'location': 'Sydney',
                'aqi': 45,
                'quality_rating': 'good',
                'timestamp': '2024-12-19T10:30:00Z'
            }]
        }
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response
        
        # Mock DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='asthma-guardian-air-quality',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        with patch('boto3.resource') as mock_resource:
            mock_resource.return_value = dynamodb
            
            from backend.lambda_functions.data_ingestion.handler import handler
            
            event = {
                'source': 'aws.events',
                'detail-type': 'Scheduled Event'
            }
            
            response = handler(event, {})
            
            assert response['statusCode'] == 200


if __name__ == "__main__":
    pytest.main([__file__])
