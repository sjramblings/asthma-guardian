"""
Guidance API Lambda Function

This Lambda function handles personalized guidance recommendations using AWS Bedrock AgentCore
including:
- Personalized asthma guidance based on air quality and user profile
- Risk assessment and recommendations
- Action suggestions for poor air quality days
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
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')  # Bedrock is available in us-east-1

users_table = dynamodb.Table(os.getenv('USERS_TABLE_NAME', 'asthma-guardian-users'))
air_quality_table = dynamodb.Table(os.getenv('AIR_QUALITY_TABLE_NAME', 'asthma-guardian-air-quality'))
guidance_table = dynamodb.Table(os.getenv('GUIDANCE_TABLE_NAME', 'asthma-guardian-guidance'))

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for guidance API endpoints.
    
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
        if http_method == 'GET' and '/guidance/' in path:
            user_id = path_params.get('user_id')
            if user_id:
                return handle_get_guidance(user_id, query_params)
            else:
                return create_error_response(400, "user_id parameter is required")
        elif http_method == 'POST' and path.endswith('/guidance'):
            return handle_create_guidance(json.loads(body))
        else:
            return create_error_response(404, "Endpoint not found")
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_error_response(500, "Internal server error")

def handle_get_guidance(user_id: str, query_params: Dict[str, str]) -> Dict[str, Any]:
    """
    Handle GET /api/guidance/{user_id} requests.
    
    Args:
        user_id: User ID
        query_params: Query parameters
        
    Returns:
        API Gateway response with personalized guidance
    """
    try:
        # Get user profile
        user_profile = get_user_profile(user_id)
        if not user_profile:
            return create_error_response(404, "User not found")
        
        # Get current air quality for user's location
        postcode = user_profile.get('location', {}).get('postcode')
        if not postcode:
            return create_error_response(400, "User location not set")
        
        air_quality = get_current_air_quality_data(postcode)
        if not air_quality:
            return create_error_response(404, "No air quality data available for user location")
        
        # Generate personalized guidance using Bedrock
        guidance = generate_personalized_guidance(user_profile, air_quality)
        
        # Store guidance in database
        store_guidance_recommendation(user_id, guidance)
        
        return create_success_response(guidance)
        
    except Exception as e:
        logger.error(f"Error getting guidance: {str(e)}")
        return create_error_response(500, "Failed to generate guidance")

def handle_create_guidance(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle POST /api/guidance requests.
    
    Args:
        request_data: Request body data
        
    Returns:
        API Gateway response with created guidance
    """
    try:
        # Validate required fields
        if not request_data.get('user_id'):
            return create_error_response(400, "user_id is required")
        
        user_id = request_data['user_id']
        
        # Get user profile
        user_profile = get_user_profile(user_id)
        if not user_profile:
            return create_error_response(404, "User not found")
        
        # Get air quality data
        postcode = user_profile.get('location', {}).get('postcode')
        if not postcode:
            return create_error_response(400, "User location not set")
        
        air_quality = get_current_air_quality_data(postcode)
        if not air_quality:
            return create_error_response(404, "No air quality data available")
        
        # Generate guidance
        guidance = generate_personalized_guidance(user_profile, air_quality)
        
        # Store guidance
        store_guidance_recommendation(user_id, guidance)
        
        return create_success_response(guidance, 201)
        
    except Exception as e:
        logger.error(f"Error creating guidance: {str(e)}")
        return create_error_response(500, "Failed to create guidance")

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

def get_current_air_quality_data(postcode: str) -> Optional[Dict[str, Any]]:
    """
    Get current air quality data for a postcode.
    
    Args:
        postcode: NSW postcode
        
    Returns:
        Current air quality data or None if not found
    """
    try:
        response = air_quality_table.query(
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={
                ':pk': f'LOCATION#{postcode}'
            },
            ScanIndexForward=False,
            Limit=1
        )
        
        if not response['Items']:
            return None
        
        return response['Items'][0]
        
    except Exception as e:
        logger.error(f"Error getting air quality data: {str(e)}")
        return None

def generate_personalized_guidance(user_profile: Dict[str, Any], air_quality: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate personalized guidance using AWS Bedrock AgentCore.
    
    Args:
        user_profile: User profile data
        air_quality: Current air quality data
        
    Returns:
        Personalized guidance recommendations
    """
    try:
        # Prepare context for Bedrock
        context = {
            'user_profile': {
                'asthma_severity': user_profile.get('asthma_severity', 'mild'),
                'sensitivity_settings': user_profile.get('sensitivity_settings', {}),
                'location': user_profile.get('location', {})
            },
            'air_quality': {
                'aqi': air_quality.get('aqi', 0),
                'quality_rating': air_quality.get('quality_rating', 'unknown'),
                'pollutants': {
                    'pm25': air_quality.get('pm25', 0),
                    'pm10': air_quality.get('pm10', 0),
                    'ozone': air_quality.get('ozone', 0),
                    'no2': air_quality.get('no2', 0),
                    'so2': air_quality.get('so2', 0)
                }
            }
        }
        
        # Create prompt for Bedrock
        prompt = create_guidance_prompt(context)
        
        # Call Bedrock (using Claude model as example)
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1000,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        guidance_text = response_body['content'][0]['text']
        
        # Parse the guidance into structured format
        guidance = parse_guidance_response(guidance_text, context)
        
        return guidance
        
    except Exception as e:
        logger.error(f"Error generating guidance with Bedrock: {str(e)}")
        # Fallback to rule-based guidance
        return generate_fallback_guidance(user_profile, air_quality)

def create_guidance_prompt(context: Dict[str, Any]) -> str:
    """
    Create a prompt for Bedrock to generate personalized guidance.
    
    Args:
        context: User and air quality context
        
    Returns:
        Formatted prompt string
    """
    user = context['user_profile']
    air = context['air_quality']
    
    prompt = f"""
You are an AI assistant specialized in providing personalized asthma guidance based on air quality data.

User Profile:
- Asthma Severity: {user['asthma_severity']}
- Location: {user['location'].get('postcode', 'Unknown')}
- Sensitivity Settings: {json.dumps(user['sensitivity_settings'], indent=2)}

Current Air Quality:
- AQI: {air['aqi']}
- Quality Rating: {air['quality_rating']}
- Pollutants: {json.dumps(air['pollutants'], indent=2)}

Please provide personalized guidance in the following JSON format:
{{
    "risk_level": "low|moderate|high|very_high",
    "recommendations": [
        {{
            "type": "immediate|preventive|long_term",
            "title": "Brief title",
            "description": "Detailed description",
            "priority": "high|medium|low"
        }}
    ],
    "actions": [
        {{
            "action": "stay_indoors|limit_exercise|use_inhaler|seek_medical_help",
            "description": "What the user should do",
            "urgency": "immediate|soon|when_possible"
        }}
    ],
    "explanation": "Brief explanation of why these recommendations are important for this user's specific situation"
}}

Focus on:
1. User's asthma severity level
2. Current air quality conditions
3. Specific pollutants that may affect them
4. Practical, actionable advice
5. When to seek medical help

Respond only with valid JSON, no additional text.
"""
    
    return prompt

def parse_guidance_response(guidance_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse Bedrock response into structured guidance format.
    
    Args:
        guidance_text: Raw response from Bedrock
        context: Original context
        
    Returns:
        Structured guidance data
    """
    try:
        # Try to parse as JSON
        guidance = json.loads(guidance_text)
        
        # Add metadata
        guidance['generated_at'] = datetime.utcnow().isoformat() + 'Z'
        guidance['user_id'] = context['user_profile'].get('user_id')
        guidance['air_quality_data'] = context['air_quality']
        
        return guidance
        
    except json.JSONDecodeError:
        logger.error("Failed to parse Bedrock response as JSON")
        return generate_fallback_guidance(
            context['user_profile'], 
            context['air_quality']
        )

def generate_fallback_guidance(user_profile: Dict[str, Any], air_quality: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate fallback guidance using rule-based logic.
    
    Args:
        user_profile: User profile data
        air_quality: Current air quality data
        
    Returns:
        Rule-based guidance recommendations
    """
    aqi = air_quality.get('aqi', 0)
    severity = user_profile.get('asthma_severity', 'mild')
    
    # Determine risk level based on AQI and asthma severity
    if aqi <= 50:
        risk_level = "low"
    elif aqi <= 100:
        risk_level = "moderate" if severity == "mild" else "high"
    elif aqi <= 150:
        risk_level = "high" if severity == "mild" else "very_high"
    else:
        risk_level = "very_high"
    
    # Generate recommendations based on risk level
    recommendations = []
    actions = []
    
    if risk_level == "low":
        recommendations.append({
            "type": "preventive",
            "title": "Good Air Quality",
            "description": "Air quality is good. You can enjoy outdoor activities normally.",
            "priority": "low"
        })
    elif risk_level == "moderate":
        recommendations.append({
            "type": "preventive",
            "title": "Moderate Air Quality",
            "description": "Air quality is moderate. Consider reducing prolonged outdoor activities if you experience symptoms.",
            "priority": "medium"
        })
    elif risk_level == "high":
        recommendations.append({
            "type": "immediate",
            "title": "Poor Air Quality",
            "description": "Air quality is poor. Limit outdoor activities and stay indoors when possible.",
            "priority": "high"
        })
        actions.append({
            "action": "stay_indoors",
            "description": "Stay indoors with windows closed",
            "urgency": "immediate"
        })
    else:  # very_high
        recommendations.append({
            "type": "immediate",
            "title": "Very Poor Air Quality",
            "description": "Air quality is very poor. Avoid all outdoor activities and stay indoors.",
            "priority": "high"
        })
        actions.append({
            "action": "stay_indoors",
            "description": "Stay indoors with windows closed and air conditioning on",
            "urgency": "immediate"
        })
        actions.append({
            "action": "use_inhaler",
            "description": "Use your rescue inhaler if you have symptoms",
            "urgency": "immediate"
        })
    
    return {
        "risk_level": risk_level,
        "recommendations": recommendations,
        "actions": actions,
        "explanation": f"Based on your {severity} asthma and current AQI of {aqi}, these recommendations are tailored to your specific needs.",
        "generated_at": datetime.utcnow().isoformat() + 'Z',
        "user_id": user_profile.get('user_id'),
        "air_quality_data": air_quality
    }

def store_guidance_recommendation(user_id: str, guidance: Dict[str, Any]) -> None:
    """
    Store guidance recommendation in DynamoDB.
    
    Args:
        user_id: User ID
        guidance: Guidance data to store
    """
    try:
        item = {
            'PK': f'USER#{user_id}',
            'SK': f'GUIDANCE#{guidance["generated_at"]}',
            'GSI1PK': f'LOCATION#{guidance["air_quality_data"].get("location", {}).get("postcode", "unknown")}',
            'GSI1SK': f'GUIDANCE#{guidance["generated_at"]}',
            'user_id': user_id,
            'guidance_data': guidance,
            'created_at': guidance['generated_at'],
            'ttl': int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }
        
        guidance_table.put_item(Item=item)
        
    except Exception as e:
        logger.error(f"Error storing guidance recommendation: {str(e)}")

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
