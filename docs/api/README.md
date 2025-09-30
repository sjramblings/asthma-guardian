# Asthma Guardian v3 API Documentation

## Overview

The Asthma Guardian v3 API provides endpoints for air quality data, user management, personalized guidance, and notifications. This API is designed to help people with asthma in NSW stay safer on poor air quality days.

## Base URL

- **Development**: `https://api-dev.asthmaguardian.nsw.gov.au/api`
- **Production**: `https://api.asthmaguardian.nsw.gov.au/api`

## Authentication

All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Rate Limiting

- **Rate Limit**: 1000 requests per hour per user
- **Burst Limit**: 200 requests per minute
- **Headers**: Rate limit information is included in response headers

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional error details"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |

## Endpoints

### Air Quality Endpoints

#### Get Current Air Quality

```http
GET /air-quality/current
```

**Query Parameters:**
- `postcode` (string, optional): NSW postcode
- `latitude` (number, optional): Latitude coordinate
- `longitude` (number, optional): Longitude coordinate

**Response:**
```json
{
  "aqi": 45,
  "quality_rating": "good",
  "location": "Sydney",
  "postcode": "2000",
  "timestamp": "2024-12-19T10:30:00Z",
  "pollutants": {
    "pm25": 12.5,
    "pm10": 18.2,
    "ozone": 45.0,
    "no2": 25.0,
    "so2": 8.5
  },
  "health_advice": "Air quality is good. No health impacts expected."
}
```

#### Get Air Quality Forecast

```http
GET /air-quality/forecast
```

**Query Parameters:**
- `postcode` (string, optional): NSW postcode
- `latitude` (number, optional): Latitude coordinate
- `longitude` (number, optional): Longitude coordinate
- `days` (number, optional): Number of forecast days (default: 7, max: 14)

**Response:**
```json
[
  {
    "date": "2024-12-20",
    "aqi": 50,
    "quality_rating": "good",
    "location": "Sydney",
    "pollutants": {
      "pm25": 15.0,
      "pm10": 22.0,
      "ozone": 50.0,
      "no2": 30.0,
      "so2": 10.0
    },
    "health_advice": "Air quality is good. No health impacts expected."
  }
]
```

#### Get Air Quality History

```http
GET /air-quality/history
```

**Query Parameters:**
- `postcode` (string, optional): NSW postcode
- `latitude` (number, optional): Latitude coordinate
- `longitude` (number, optional): Longitude coordinate
- `start_date` (string, required): Start date (YYYY-MM-DD)
- `end_date` (string, required): End date (YYYY-MM-DD)
- `limit` (number, optional): Maximum number of records (default: 100, max: 1000)

**Response:**
```json
[
  {
    "timestamp": "2024-12-19T10:30:00Z",
    "aqi": 45,
    "quality_rating": "good",
    "location": "Sydney",
    "pollutants": {
      "pm25": 12.5,
      "pm10": 18.2,
      "ozone": 45.0,
      "no2": 25.0,
      "so2": 8.5
    }
  }
]
```

### User Profile Endpoints

#### Create User Profile

```http
POST /users
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "asthma_severity": "moderate",
  "location": {
    "postcode": "2000",
    "latitude": -33.8688,
    "longitude": 151.2093
  },
  "sensitivity_settings": {
    "pm25_threshold": 50,
    "pm10_threshold": 100,
    "ozone_threshold": 100,
    "no2_threshold": 200,
    "so2_threshold": 100
  },
  "notification_preferences": {
    "email_enabled": true,
    "sms_enabled": false,
    "push_enabled": true,
    "frequency": "immediate"
  }
}
```

**Response:**
```json
{
  "user_id": "user-123456",
  "email": "user@example.com",
  "asthma_severity": "moderate",
  "created_at": "2024-12-19T10:30:00Z",
  "updated_at": "2024-12-19T10:30:00Z"
}
```

#### Get User Profile

```http
GET /users/{user_id}
```

**Response:**
```json
{
  "user_id": "user-123456",
  "email": "user@example.com",
  "asthma_severity": "moderate",
  "location": {
    "postcode": "2000",
    "latitude": -33.8688,
    "longitude": 151.2093
  },
  "sensitivity_settings": {
    "pm25_threshold": 50,
    "pm10_threshold": 100,
    "ozone_threshold": 100,
    "no2_threshold": 200,
    "so2_threshold": 100
  },
  "notification_preferences": {
    "email_enabled": true,
    "sms_enabled": false,
    "push_enabled": true,
    "frequency": "immediate"
  },
  "created_at": "2024-12-19T10:30:00Z",
  "updated_at": "2024-12-19T10:30:00Z"
}
```

#### Update User Profile

```http
PUT /users/{user_id}
```

**Request Body:**
```json
{
  "asthma_severity": "severe",
  "location": {
    "postcode": "3000",
    "latitude": -37.8136,
    "longitude": 144.9631
  },
  "sensitivity_settings": {
    "pm25_threshold": 30,
    "pm10_threshold": 80,
    "ozone_threshold": 80,
    "no2_threshold": 150,
    "so2_threshold": 80
  }
}
```

**Response:**
```json
{
  "user_id": "user-123456",
  "email": "user@example.com",
  "asthma_severity": "severe",
  "location": {
    "postcode": "3000",
    "latitude": -37.8136,
    "longitude": 144.9631
  },
  "sensitivity_settings": {
    "pm25_threshold": 30,
    "pm10_threshold": 80,
    "ozone_threshold": 80,
    "no2_threshold": 150,
    "so2_threshold": 80
  },
  "notification_preferences": {
    "email_enabled": true,
    "sms_enabled": false,
    "push_enabled": true,
    "frequency": "immediate"
  },
  "created_at": "2024-12-19T10:30:00Z",
  "updated_at": "2024-12-19T11:00:00Z"
}
```

### Guidance Endpoints

#### Get Personalized Guidance

```http
GET /guidance/{user_id}
```

**Response:**
```json
{
  "user_id": "user-123456",
  "recommendations": [
    {
      "id": "rec-001",
      "type": "precaution",
      "priority": "high",
      "title": "Limit Outdoor Activities",
      "description": "Due to moderate air quality, consider reducing outdoor activities, especially exercise.",
      "actions": [
        "Stay indoors when possible",
        "Use air purifiers",
        "Keep windows closed",
        "Consider rescheduling outdoor plans"
      ],
      "valid_until": "2024-12-20T10:30:00Z"
    }
  ],
  "generated_at": "2024-12-19T10:30:00Z"
}
```

#### Generate Custom Guidance

```http
POST /guidance
```

**Request Body:**
```json
{
  "user_id": "user-123456",
  "user_input": "What should I do about the current air quality?"
}
```

**Response:**
```json
{
  "user_id": "user-123456",
  "guidance": "Based on your moderate asthma severity and the current air quality (AQI: 45), I recommend taking the following precautions: 1) Limit outdoor activities, especially exercise, 2) Keep windows closed, 3) Use air purifiers if available, 4) Monitor your symptoms closely. The air quality is currently good, but it's always better to be cautious with asthma.",
  "confidence": 0.85,
  "generated_at": "2024-12-19T10:30:00Z"
}
```

### Notification Endpoints

#### Subscribe to Notifications

```http
POST /notifications
```

**Request Body:**
```json
{
  "user_id": "user-123456",
  "type": "alert",
  "target": "email",
  "message": "High pollution levels detected in your area"
}
```

**Response:**
```json
{
  "notification_id": "notif-123456",
  "user_id": "user-123456",
  "type": "alert",
  "channel": "email",
  "status": "sent",
  "sent_at": "2024-12-19T10:30:00Z"
}
```

#### Get Notification History

```http
GET /notifications/{user_id}
```

**Query Parameters:**
- `limit` (number, optional): Maximum number of notifications (default: 50, max: 200)
- `offset` (number, optional): Number of notifications to skip (default: 0)
- `type` (string, optional): Filter by notification type
- `status` (string, optional): Filter by notification status

**Response:**
```json
[
  {
    "notification_id": "notif-123456",
    "type": "alert",
    "subject": "Air Quality Alert",
    "message": "High pollution levels detected in your area",
    "channel": "email",
    "status": "sent",
    "sent_at": "2024-12-19T10:30:00Z",
    "read_at": "2024-12-19T10:35:00Z"
  }
]
```

#### Update Notification Preferences

```http
PUT /notifications/preferences/{user_id}
```

**Request Body:**
```json
{
  "email_enabled": true,
  "sms_enabled": false,
  "push_enabled": true,
  "frequency": "daily",
  "quiet_hours": {
    "enabled": true,
    "start": "22:00",
    "end": "07:00"
  }
}
```

**Response:**
```json
{
  "user_id": "user-123456",
  "preferences": {
    "email_enabled": true,
    "sms_enabled": false,
    "push_enabled": true,
    "frequency": "daily",
    "quiet_hours": {
      "enabled": true,
      "start": "22:00",
      "end": "07:00"
    }
  },
  "updated_at": "2024-12-19T10:30:00Z"
}
```

## Data Models

### Air Quality Data

```json
{
  "aqi": 45,
  "quality_rating": "good",
  "location": "Sydney",
  "postcode": "2000",
  "latitude": -33.8688,
  "longitude": 151.2093,
  "timestamp": "2024-12-19T10:30:00Z",
  "pollutants": {
    "pm25": 12.5,
    "pm10": 18.2,
    "ozone": 45.0,
    "no2": 25.0,
    "so2": 8.5
  },
  "health_advice": "Air quality is good. No health impacts expected.",
  "source": "NSW Government Air Quality API"
}
```

### User Profile

```json
{
  "user_id": "user-123456",
  "email": "user@example.com",
  "asthma_severity": "moderate",
  "location": {
    "postcode": "2000",
    "latitude": -33.8688,
    "longitude": 151.2093
  },
  "sensitivity_settings": {
    "pm25_threshold": 50,
    "pm10_threshold": 100,
    "ozone_threshold": 100,
    "no2_threshold": 200,
    "so2_threshold": 100
  },
  "notification_preferences": {
    "email_enabled": true,
    "sms_enabled": false,
    "push_enabled": true,
    "frequency": "immediate",
    "quiet_hours": {
      "enabled": true,
      "start": "22:00",
      "end": "07:00"
    }
  },
  "created_at": "2024-12-19T10:30:00Z",
  "updated_at": "2024-12-19T10:30:00Z"
}
```

## SDKs and Examples

### JavaScript/TypeScript

```javascript
import { AsthmaGuardianAPI } from '@asthma-guardian/api-client';

const api = new AsthmaGuardianAPI({
  baseURL: 'https://api.asthmaguardian.nsw.gov.au/api',
  token: 'your-jwt-token'
});

// Get current air quality
const airQuality = await api.airQuality.getCurrent({ postcode: '2000' });
console.log(airQuality);

// Create user profile
const user = await api.users.create({
  email: 'user@example.com',
  asthma_severity: 'moderate',
  location: {
    postcode: '2000',
    latitude: -33.8688,
    longitude: 151.2093
  }
});
```

### Python

```python
from asthma_guardian_api import AsthmaGuardianAPI

api = AsthmaGuardianAPI(
    base_url='https://api.asthmaguardian.nsw.gov.au/api',
    token='your-jwt-token'
)

# Get current air quality
air_quality = api.air_quality.get_current(postcode='2000')
print(air_quality)

# Create user profile
user = api.users.create({
    'email': 'user@example.com',
    'asthma_severity': 'moderate',
    'location': {
        'postcode': '2000',
        'latitude': -33.8688,
        'longitude': 151.2093
    }
})
```

## Support

For API support and questions:
- **Email**: api-support@asthmaguardian.nsw.gov.au
- **Documentation**: https://docs.asthmaguardian.nsw.gov.au
- **Status Page**: https://status.asthmaguardian.nsw.gov.au
