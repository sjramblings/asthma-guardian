# Data Model: Asthma Guardian v3

## Overview
This document defines the data model for the Asthma Guardian v3 application, including database schemas, API data structures, and data flow patterns.

## Database Schema (DynamoDB)

### Users Table
```python
{
    "PK": "USER#{user_id}",  # Partition Key
    "SK": "PROFILE",         # Sort Key
    "GSI1PK": "EMAIL#{email}",
    "GSI1SK": "USER#{user_id}",
    "user_id": "uuid",
    "email": "string",
    "asthma_severity": "mild|moderate|severe",
    "location": {
        "postcode": "string",
        "latitude": "number",
        "longitude": "number"
    },
    "sensitivity_settings": {
        "pm25_threshold": "number",
        "pm10_threshold": "number",
        "ozone_threshold": "number",
        "no2_threshold": "number",
        "so2_threshold": "number"
    },
    "notification_preferences": {
        "email_enabled": "boolean",
        "sms_enabled": "boolean",
        "push_enabled": "boolean",
        "frequency": "immediate|hourly|daily"
    },
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### Air Quality Data Table
```python
{
    "PK": "LOCATION#{postcode}",  # Partition Key
    "SK": "TIMESTAMP#{timestamp}", # Sort Key
    "GSI1PK": "DATE#{date}",
    "GSI1SK": "LOCATION#{postcode}",
    "location": {
        "postcode": "string",
        "latitude": "number",
        "longitude": "number"
    },
    "timestamp": "datetime",
    "pollutants": {
        "pm25": "number",
        "pm10": "number",
        "ozone": "number",
        "no2": "number",
        "so2": "number"
    },
    "aqi": "number",
    "data_source": "bom|epa_nsw",
    "quality_rating": "good|moderate|poor|hazardous"
}
```

### User Alerts Table
```python
{
    "PK": "USER#{user_id}",  # Partition Key
    "SK": "ALERT#{alert_id}", # Sort Key
    "GSI1PK": "STATUS#{status}",
    "GSI1SK": "TIMESTAMP#{timestamp}",
    "alert_id": "uuid",
    "user_id": "uuid",
    "alert_type": "air_quality|health_risk|medication_reminder",
    "severity": "low|medium|high|critical",
    "message": "string",
    "status": "pending|sent|delivered|failed",
    "delivery_method": "email|sms|push",
    "created_at": "datetime",
    "sent_at": "datetime"
}
```

### Guidance Recommendations Table
```python
{
    "PK": "USER#{user_id}",  # Partition Key
    "SK": "GUIDANCE#{guidance_id}", # Sort Key
    "GSI1PK": "LOCATION#{postcode}",
    "GSI1SK": "TIMESTAMP#{timestamp}",
    "guidance_id": "uuid",
    "user_id": "uuid",
    "location": {
        "postcode": "string",
        "latitude": "number",
        "longitude": "number"
    },
    "timestamp": "datetime",
    "recommendations": [
        {
            "category": "indoor_activities|outdoor_activities|medication|emergency",
            "title": "string",
            "description": "string",
            "priority": "low|medium|high|urgent"
        }
    ],
    "risk_level": "low|moderate|high|critical",
    "created_at": "datetime"
}
```

## API Data Structures

### Air Quality Response
```python
{
    "location": {
        "postcode": "string",
        "latitude": "number",
        "longitude": "number"
    },
    "current": {
        "timestamp": "datetime",
        "aqi": "number",
        "quality_rating": "string",
        "pollutants": {
            "pm25": "number",
            "pm10": "number",
            "ozone": "number",
            "no2": "number",
            "so2": "number"
        }
    },
    "forecast": [
        {
            "timestamp": "datetime",
            "aqi": "number",
            "quality_rating": "string"
        }
    ]
}
```

### User Profile Response
```python
{
    "user_id": "uuid",
    "email": "string",
    "asthma_severity": "string",
    "location": {
        "postcode": "string",
        "latitude": "number",
        "longitude": "number"
    },
    "sensitivity_settings": {
        "pm25_threshold": "number",
        "pm10_threshold": "number",
        "ozone_threshold": "number",
        "no2_threshold": "number",
        "so2_threshold": "number"
    },
    "notification_preferences": {
        "email_enabled": "boolean",
        "sms_enabled": "boolean",
        "push_enabled": "boolean",
        "frequency": "string"
    }
}
```

### Guidance Response
```python
{
    "user_id": "uuid",
    "location": {
        "postcode": "string",
        "latitude": "number",
        "longitude": "number"
    },
    "timestamp": "datetime",
    "risk_level": "string",
    "recommendations": [
        {
            "category": "string",
            "title": "string",
            "description": "string",
            "priority": "string"
        }
    ],
    "air_quality_context": {
        "current_aqi": "number",
        "quality_rating": "string",
        "trend": "improving|stable|worsening"
    }
}
```

## Data Flow Patterns

### Air Quality Data Ingestion
1. External API calls to NSW Government feeds
2. Data validation and normalization
3. Storage in DynamoDB with TTL for historical data
4. Real-time updates via DynamoDB Streams

### User Guidance Generation
1. User profile retrieval from DynamoDB
2. Current air quality data lookup
3. LLM-powered analysis via AWS Bedrock AgentCore
4. Personalized recommendation generation
5. Storage and delivery to user

### Notification Processing
1. Air quality threshold monitoring
2. User preference checking
3. Alert generation and queuing
4. Multi-channel delivery (email, SMS, push)
5. Delivery status tracking

## Data Retention Policies
- **User Data:** 2 years after last activity
- **Air Quality Data:** 1 year with TTL
- **Alerts:** 90 days
- **Guidance:** 30 days
- **Logs:** 7 days (CloudWatch), 90 days (S3)
