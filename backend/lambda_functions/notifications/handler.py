"""
Notification API Lambda Function

This Lambda function handles notification services including:
- User notification preferences management
- Sending notifications via email, SMS, and push
- Notification history and tracking
- Integration with SNS for multi-channel delivery
"""

import json
import os
import boto3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
ses = boto3.client('ses', region_name='us-east-1')  # SES is available in us-east-1

users_table = dynamodb.Table(os.getenv('USERS_TABLE_NAME', 'asthma-guardian-users'))
user_alerts_table = dynamodb.Table(os.getenv('USER_ALERTS_TABLE_NAME', 'asthma-guardian-user-alerts'))

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for notification API endpoints.
    
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
        if http_method == 'GET' and '/notifications/' in path:
            user_id = path_params.get('user_id')
            if user_id:
                return handle_get_notifications(user_id, query_params)
            else:
                return create_error_response(400, "user_id parameter is required")
        elif http_method == 'POST' and path.endswith('/notifications'):
            return handle_send_notification(json.loads(body))
        elif http_method == 'PUT' and '/notifications/preferences/' in path:
            user_id = path_params.get('user_id')
            if user_id:
                return handle_update_notification_preferences(user_id, json.loads(body))
            else:
                return create_error_response(400, "user_id parameter is required")
        else:
            return create_error_response(404, "Endpoint not found")
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_error_response(500, "Internal server error")

def handle_get_notifications(user_id: str, query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle GET /api/notifications/{user_id} requests.
    
    Args:
        user_id: User ID
        query_params: Query parameters
        
    Returns:
        API Gateway response with notification history
    """
    try:
        # Get notification history for user
        notifications = get_user_notifications(user_id, query_params)
        
        return create_success_response(notifications)
        
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        return create_error_response(500, "Failed to retrieve notifications")

def handle_send_notification(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle POST /api/notifications requests.
    
    Args:
        request_data: Request body data
        
    Returns:
        API Gateway response with notification status
    """
    try:
        # Validate required fields
        if not request_data.get('user_id'):
            return create_error_response(400, "user_id is required")
        
        if not request_data.get('message'):
            return create_error_response(400, "message is required")
        
        user_id = request_data['user_id']
        
        # Get user profile and preferences
        user_profile = get_user_profile(user_id)
        if not user_profile:
            return create_error_response(404, "User not found")
        
        # Send notification
        notification_result = send_notification(user_id, user_profile, request_data)
        
        return create_success_response(notification_result, 201)
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return create_error_response(500, "Failed to send notification")

def handle_update_notification_preferences(user_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle PUT /api/notifications/preferences/{user_id} requests.
    
    Args:
        user_id: User ID
        request_data: Request body data
        
    Returns:
        API Gateway response with updated preferences
    """
    try:
        # Update notification preferences
        updated_preferences = update_notification_preferences(user_id, request_data)
        
        if not updated_preferences:
            return create_error_response(404, "User not found")
        
        return create_success_response(updated_preferences)
        
    except Exception as e:
        logger.error(f"Error updating notification preferences: {str(e)}")
        return create_error_response(500, "Failed to update notification preferences")

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
        
        return response['Item']
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return None

def get_user_notifications(user_id: str, query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Get notification history for a user.
    
    Args:
        user_id: User ID
        query_params: Query parameters
        
    Returns:
        Notification history data
    """
    try:
        # Get date range
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        
        if not start_date:
            # Default to last 30 days
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Query notification history
        response = user_alerts_table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :start_sk AND :end_sk',
            ExpressionAttributeValues={
                ':pk': f'USER#{user_id}',
                ':start_sk': f'NOTIFICATION#{start_date}T00:00:00Z',
                ':end_sk': f'NOTIFICATION#{end_date}T23:59:59Z'
            }
        )
        
        # Format notifications
        notifications = []
        for item in response['Items']:
            notifications.append({
                'notification_id': item.get('notification_id'),
                'type': item.get('type'),
                'channel': item.get('channel'),
                'message': item.get('message'),
                'status': item.get('status'),
                'sent_at': item.get('sent_at'),
                'read_at': item.get('read_at')
            })
        
        return {
            'user_id': user_id,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'notifications': notifications,
            'total_count': len(notifications)
        }
        
    except Exception as e:
        logger.error(f"Error getting user notifications: {str(e)}")
        return {'notifications': [], 'total_count': 0}

def send_notification(user_id: str, user_profile: Dict[str, Any], notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send notification to user via preferred channels.
    
    Args:
        user_id: User ID
        user_profile: User profile data
        notification_data: Notification data
        
    Returns:
        Notification sending result
    """
    try:
        notification_id = f"notif_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}"
        now = datetime.utcnow().isoformat() + 'Z'
        
        # Get user notification preferences
        preferences = user_profile.get('notification_preferences', {})
        
        # Prepare notification channels
        channels = []
        if preferences.get('email_enabled', True):
            channels.append('email')
        if preferences.get('sms_enabled', False):
            channels.append('sms')
        if preferences.get('push_enabled', True):
            channels.append('push')
        
        # Send notifications via each channel
        results = []
        for channel in channels:
            try:
                if channel == 'email':
                    result = send_email_notification(user_id, user_profile, notification_data)
                elif channel == 'sms':
                    result = send_sms_notification(user_id, user_profile, notification_data)
                elif channel == 'push':
                    result = send_push_notification(user_id, user_profile, notification_data)
                
                results.append({
                    'channel': channel,
                    'status': 'sent',
                    'message_id': result.get('message_id', 'unknown')
                })
                
                # Store notification record
                store_notification_record(user_id, notification_id, channel, notification_data, 'sent', now)
                
            except Exception as e:
                logger.error(f"Error sending {channel} notification: {str(e)}")
                results.append({
                    'channel': channel,
                    'status': 'failed',
                    'error': str(e)
                })
                
                # Store failed notification record
                store_notification_record(user_id, notification_id, channel, notification_data, 'failed', now)
        
        return {
            'notification_id': notification_id,
            'user_id': user_id,
            'channels': results,
            'sent_at': now
        }
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        raise

def send_email_notification(user_id: str, user_profile: Dict[str, Any], notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send email notification via SES.
    
    Args:
        user_id: User ID
        user_profile: User profile data
        notification_data: Notification data
        
    Returns:
        Email sending result
    """
    try:
        email = user_profile.get('email')
        if not email:
            raise ValueError("User email not found")
        
        # Prepare email content
        subject = notification_data.get('subject', 'Asthma Guardian Alert')
        message = notification_data.get('message', '')
        
        # Send email via SES
        response = ses.send_email(
            Source=os.getenv('SES_FROM_EMAIL', 'noreply@asthmaguardian.nsw.gov.au'),
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': message},
                    'Html': {'Data': f'<html><body><p>{message}</p></body></html>'}
                }
            }
        )
        
        return {
            'message_id': response['MessageId'],
            'status': 'sent'
        }
        
    except Exception as e:
        logger.error(f"Error sending email notification: {str(e)}")
        raise

def send_sms_notification(user_id: str, user_profile: Dict[str, Any], notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send SMS notification via SNS.
    
    Args:
        user_id: User ID
        user_profile: User profile data
        notification_data: Notification data
        
    Returns:
        SMS sending result
    """
    try:
        phone_number = user_profile.get('phone_number')
        if not phone_number:
            raise ValueError("User phone number not found")
        
        message = notification_data.get('message', '')
        
        # Send SMS via SNS
        response = sns.publish(
            PhoneNumber=phone_number,
            Message=message
        )
        
        return {
            'message_id': response['MessageId'],
            'status': 'sent'
        }
        
    except Exception as e:
        logger.error(f"Error sending SMS notification: {str(e)}")
        raise

def send_push_notification(user_id: str, user_profile: Dict[str, Any], notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send push notification via SNS.
    
    Args:
        user_id: User ID
        user_profile: User profile data
        notification_data: Notification data
        
    Returns:
        Push notification sending result
    """
    try:
        # Get user's device tokens (this would be stored in user profile)
        device_tokens = user_profile.get('device_tokens', [])
        if not device_tokens:
            raise ValueError("User device tokens not found")
        
        message = notification_data.get('message', '')
        
        # Send push notification to each device
        results = []
        for device_token in device_tokens:
            response = sns.publish(
                TargetArn=device_token,
                Message=json.dumps({
                    'default': message,
                    'APNS': json.dumps({
                        'aps': {
                            'alert': message,
                            'sound': 'default'
                        }
                    })
                }),
                MessageStructure='json'
            )
            results.append(response['MessageId'])
        
        return {
            'message_id': results[0] if results else 'unknown',
            'status': 'sent',
            'device_count': len(device_tokens)
        }
        
    except Exception as e:
        logger.error(f"Error sending push notification: {str(e)}")
        raise

def store_notification_record(user_id: str, notification_id: str, channel: str, notification_data: Dict[str, Any], status: str, sent_at: str) -> None:
    """
    Store notification record in DynamoDB.
    
    Args:
        user_id: User ID
        notification_id: Notification ID
        channel: Notification channel
        notification_data: Notification data
        status: Notification status
        sent_at: Sent timestamp
    """
    try:
        item = {
            'PK': f'USER#{user_id}',
            'SK': f'NOTIFICATION#{sent_at}',
            'GSI1PK': f'STATUS#{status}',
            'GSI1SK': f'NOTIFICATION#{sent_at}',
            'notification_id': notification_id,
            'user_id': user_id,
            'type': notification_data.get('type', 'alert'),
            'channel': channel,
            'message': notification_data.get('message', ''),
            'subject': notification_data.get('subject', ''),
            'status': status,
            'sent_at': sent_at,
            'ttl': int((datetime.utcnow() + timedelta(days=90)).timestamp())
        }
        
        user_alerts_table.put_item(Item=item)
        
    except Exception as e:
        logger.error(f"Error storing notification record: {str(e)}")

def update_notification_preferences(user_id: str, preferences_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update user notification preferences.
    
    Args:
        user_id: User ID
        preferences_data: New preferences data
        
    Returns:
        Updated preferences or None if user not found
    """
    try:
        # Update notification preferences in user profile
        update_expression = "SET notification_preferences = :prefs, updated_at = :updated_at"
        expression_attribute_values = {
            ':prefs': preferences_data,
            ':updated_at': datetime.utcnow().isoformat() + 'Z'
        }
        
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
        
        return {
            'user_id': user_id,
            'notification_preferences': preferences_data,
            'updated_at': response['Attributes']['updated_at']
        }
        
    except Exception as e:
        logger.error(f"Error updating notification preferences: {str(e)}")
        return None

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
