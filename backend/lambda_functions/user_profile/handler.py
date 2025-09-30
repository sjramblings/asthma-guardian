"""
User Profile API Lambda Function

This Lambda function handles user profile management including:
- User profile creation and updates
- User preferences management
- User authentication and authorization
"""

import json
import os
import boto3
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import uuid

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.getenv('USERS_TABLE_NAME', 'asthma-guardian-users'))

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for user profile API endpoints.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Parse the HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '')
        path_params = event.get('pathParameters') or {}
        query_params = event.get('queryStringParameters') or {}
        body = event.get('body', '{}')
        
        logger.info(f"Processing {http_method} request to {path}")
        
        # Route to appropriate handler
        if http_method == 'GET' and '/users/' in path:
            user_id = path_params.get('user_id')
            if user_id:
                return handle_get_user_profile(user_id)
            else:
                return create_error_response(400, "user_id parameter is required")
        elif http_method == 'PUT' and '/users/' in path:
            user_id = path_params.get('user_id')
            if user_id:
                return handle_update_user_profile(user_id, json.loads(body))
            else:
                return create_error_response(400, "user_id parameter is required")
        elif http_method == 'POST' and path.endswith('/users'):
            return handle_create_user_profile(json.loads(body))
        else:
            return create_error_response(404, "Endpoint not found")
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_error_response(500, "Internal server error")

def handle_get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Handle GET /api/users/{user_id} requests.
    
    Args:
        user_id: User ID
        
    Returns:
        API Gateway response with user profile data
    """
    try:
        # Get user profile from DynamoDB
        user_profile = get_user_profile(user_id)
        
        if not user_profile:
            return create_error_response(404, "User not found")
        
        return create_success_response(user_profile)
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return create_error_response(500, "Failed to retrieve user profile")

def handle_update_user_profile(user_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle PUT /api/users/{user_id} requests.
    
    Args:
        user_id: User ID
        request_data: Request body data
        
    Returns:
        API Gateway response with updated user profile
    """
    try:
        # Validate required fields
        if not request_data:
            return create_error_response(400, "Request body is required")
        
        # Update user profile
        updated_profile = update_user_profile(user_id, request_data)
        
        if not updated_profile:
            return create_error_response(404, "User not found")
        
        return create_success_response(updated_profile)
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        return create_error_response(500, "Failed to update user profile")

def handle_create_user_profile(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle POST /api/users requests.
    
    Args:
        request_data: Request body data
        
    Returns:
        API Gateway response with created user profile
    """
    try:
        # Validate required fields
        if not request_data.get('email'):
            return create_error_response(400, "email is required")
        
        # Create user profile
        user_profile = create_user_profile(request_data)
        
        return create_success_response(user_profile, 201)
        
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}")
        return create_error_response(500, "Failed to create user profile")

def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user profile from DynamoDB.
    
    Args:
        user_id: User ID
        
    Returns:
        User profile data or None if not found
    """
    try:
        response = users_table.get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': 'PROFILE'
            }
        )
        
        if 'Item' not in response:
            return None
        
        item = response['Item']
        
        # Format the response according to API contract
        return {
            'user_id': item.get('user_id'),
            'email': item.get('email'),
            'asthma_severity': item.get('asthma_severity'),
            'location': item.get('location', {}),
            'sensitivity_settings': item.get('sensitivity_settings', {}),
            'notification_preferences': item.get('notification_preferences', {}),
            'created_at': item.get('created_at'),
            'updated_at': item.get('updated_at')
        }
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return None

def update_user_profile(user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update user profile in DynamoDB.
    
    Args:
        user_id: User ID
        update_data: Data to update
        
    Returns:
        Updated user profile or None if not found
    """
    try:
        # Prepare update expression
        update_expression = "SET updated_at = :updated_at"
        expression_attribute_values = {
            ':updated_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Add fields to update
        allowed_fields = [
            'asthma_severity', 'location', 'sensitivity_settings', 
            'notification_preferences'
        ]
        
        for field in allowed_fields:
            if field in update_data:
                update_expression += f", {field} = :{field}"
                expression_attribute_values[f':{field}'] = update_data[field]
        
        # Update the item
        response = users_table.update_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': 'PROFILE'
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )
        
        if 'Attributes' not in response:
            return None
        
        item = response['Attributes']
        
        # Format the response
        return {
            'user_id': item.get('user_id'),
            'email': item.get('email'),
            'asthma_severity': item.get('asthma_severity'),
            'location': item.get('location', {}),
            'sensitivity_settings': item.get('sensitivity_settings', {}),
            'notification_preferences': item.get('notification_preferences', {}),
            'created_at': item.get('created_at'),
            'updated_at': item.get('updated_at')
        }
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        return None

def create_user_profile(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new user profile in DynamoDB.
    
    Args:
        user_data: User data
        
    Returns:
        Created user profile
    """
    try:
        user_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + 'Z'
        
        # Prepare user profile item
        profile_item = {
            'PK': f'USER#{user_id}',
            'SK': 'PROFILE',
            'GSI1PK': f'EMAIL#{user_data["email"]}',
            'GSI1SK': f'USER#{user_id}',
            'user_id': user_id,
            'email': user_data['email'],
            'asthma_severity': user_data.get('asthma_severity', 'mild'),
            'location': user_data.get('location', {}),
            'sensitivity_settings': user_data.get('sensitivity_settings', {
                'pm25_threshold': 25.0,
                'pm10_threshold': 50.0,
                'ozone_threshold': 0.1,
                'no2_threshold': 0.1,
                'so2_threshold': 0.05
            }),
            'notification_preferences': user_data.get('notification_preferences', {
                'email_enabled': True,
                'sms_enabled': False,
                'push_enabled': True,
                'frequency': 'immediate'
            }),
            'created_at': now,
            'updated_at': now
        }
        
        # Put the item in DynamoDB
        users_table.put_item(Item=profile_item)
        
        # Return the created profile
        return {
            'user_id': user_id,
            'email': profile_item['email'],
            'asthma_severity': profile_item['asthma_severity'],
            'location': profile_item['location'],
            'sensitivity_settings': profile_item['sensitivity_settings'],
            'notification_preferences': profile_item['notification_preferences'],
            'created_at': profile_item['created_at'],
            'updated_at': profile_item['updated_at']
        }
        
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}")
        raise

def create_success_response(data: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
    """
    Create a successful API Gateway response.
    
    Args:
        data: Response data
        status_code: HTTP status code
        
    Returns:
        API Gateway response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(data)
    }

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Create an error API Gateway response.
    
    Args:
        status_code: HTTP status code
        message: Error message
        
    Returns:
        API Gateway error response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({
            'error': {
                'code': status_code,
                'message': message
            }
        })
    }
