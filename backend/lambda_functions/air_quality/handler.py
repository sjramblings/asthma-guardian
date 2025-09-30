"""
Air Quality API Lambda Function

This Lambda function handles air quality data requests including:
- Current air quality data for a location
- Historical air quality data
- Air quality forecasts
"""

import json
import os
import boto3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
air_quality_table = dynamodb.Table(os.getenv('AIR_QUALITY_TABLE_NAME', 'asthma-guardian-air-quality'))

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for air quality API endpoints.
    
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
        query_params = event.get('queryStringParameters') or {}
        
        logger.info(f"Processing {http_method} request to {path}")
        
        # Route to appropriate handler
        if path.endswith('/current'):
            return handle_current_air_quality(query_params)
        elif path.endswith('/forecast'):
            return handle_air_quality_forecast(query_params)
        elif path.endswith('/history'):
            return handle_air_quality_history(query_params)
        else:
            return create_error_response(404, "Endpoint not found")
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_error_response(500, "Internal server error")

def handle_current_air_quality(query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle GET /api/air-quality/current requests.
    
    Args:
        query_params: Query parameters from the request
        
    Returns:
        API Gateway response with current air quality data
    """
    try:
        # Validate required parameters
        postcode = query_params.get('postcode')
        if not postcode:
            return create_error_response(400, "postcode parameter is required")
        
        # Get current air quality data
        current_data = get_current_air_quality_data(postcode)
        
        if not current_data:
            return create_error_response(404, "No air quality data found for the specified location")
        
        return create_success_response(current_data)
        
    except Exception as e:
        logger.error(f"Error getting current air quality data: {str(e)}")
        return create_error_response(500, "Failed to retrieve air quality data")

def handle_air_quality_forecast(query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle GET /api/air-quality/forecast requests.
    
    Args:
        query_params: Query parameters from the request
        
    Returns:
        API Gateway response with air quality forecast
    """
    try:
        # Validate required parameters
        postcode = query_params.get('postcode')
        if not postcode:
            return create_error_response(400, "postcode parameter is required")
        
        # Get forecast data
        forecast_data = get_air_quality_forecast(postcode)
        
        return create_success_response(forecast_data)
        
    except Exception as e:
        logger.error(f"Error getting air quality forecast: {str(e)}")
        return create_error_response(500, "Failed to retrieve air quality forecast")

def handle_air_quality_history(query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle GET /api/air-quality/history requests.
    
    Args:
        query_params: Query parameters from the request
        
    Returns:
        API Gateway response with air quality history
    """
    try:
        # Validate required parameters
        postcode = query_params.get('postcode')
        if not postcode:
            return create_error_response(400, "postcode parameter is required")
        
        # Get date range
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        
        if not start_date:
            # Default to last 7 days
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Get historical data
        history_data = get_air_quality_history(postcode, start_date, end_date)
        
        return create_success_response(history_data)
        
    except Exception as e:
        logger.error(f"Error getting air quality history: {str(e)}")
        return create_error_response(500, "Failed to retrieve air quality history")

def get_current_air_quality_data(postcode: str) -> Optional[Dict[str, Any]]:
    """
    Get current air quality data for a postcode.
    
    Args:
        postcode: NSW postcode
        
    Returns:
        Current air quality data or None if not found
    """
    try:
        # Query DynamoDB for the most recent air quality data
        response = air_quality_table.query(
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={
                ':pk': f'LOCATION#{postcode}'
            },
            ScanIndexForward=False,  # Get most recent first
            Limit=1
        )
        
        if not response['Items']:
            return None
        
        item = response['Items'][0]
        
        # Format the response according to API contract
        return {
            'location': {
                'postcode': postcode,
                'latitude': item.get('latitude'),
                'longitude': item.get('longitude')
            },
            'current': {
                'timestamp': item.get('timestamp'),
                'aqi': item.get('aqi'),
                'quality_rating': item.get('quality_rating'),
                'pollutants': {
                    'pm25': item.get('pm25'),
                    'pm10': item.get('pm10'),
                    'ozone': item.get('ozone'),
                    'no2': item.get('no2'),
                    'so2': item.get('so2')
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error querying air quality data: {str(e)}")
        return None

def get_air_quality_forecast(postcode: str) -> Dict[str, Any]:
    """
    Get air quality forecast for a postcode.
    
    Args:
        postcode: NSW postcode
        
    Returns:
        Air quality forecast data
    """
    # This would typically integrate with a weather/air quality service
    # For now, return mock data
    return {
        'location': {
            'postcode': postcode
        },
        'forecast': [
            {
                'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'aqi': 45,
                'quality_rating': 'good',
                'confidence': 'high'
            },
            {
                'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                'aqi': 52,
                'quality_rating': 'moderate',
                'confidence': 'medium'
            }
        ]
    }

def get_air_quality_history(postcode: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Get air quality history for a postcode and date range.
    
    Args:
        postcode: NSW postcode
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        Air quality history data
    """
    try:
        # Query DynamoDB for historical data
        response = air_quality_table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :start_sk AND :end_sk',
            ExpressionAttributeValues={
                ':pk': f'LOCATION#{postcode}',
                ':start_sk': f'TIMESTAMP#{start_date}T00:00:00Z',
                ':end_sk': f'TIMESTAMP#{end_date}T23:59:59Z'
            }
        )
        
        # Format the response
        history = []
        for item in response['Items']:
            history.append({
                'timestamp': item.get('timestamp'),
                'aqi': item.get('aqi'),
                'quality_rating': item.get('quality_rating'),
                'pollutants': {
                    'pm25': item.get('pm25'),
                    'pm10': item.get('pm10'),
                    'ozone': item.get('ozone'),
                    'no2': item.get('no2'),
                    'so2': item.get('so2')
                }
            })
        
        return {
            'location': {
                'postcode': postcode
            },
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'history': history
        }
        
    except Exception as e:
        logger.error(f"Error querying air quality history: {str(e)}")
        return {'history': []}

def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a successful API Gateway response.
    
    Args:
        data: Response data
        
    Returns:
        API Gateway response
    """
    return {
        'statusCode': 200,
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
