# API Contracts: Asthma Guardian v3

## Overview
This document defines the API contracts for the Asthma Guardian v3 application, including request/response schemas, error handling, and authentication requirements.

## Base URL
- **Production:** `https://api.asthmaguardian.nsw.gov.au`
- **Staging:** `https://api-staging.asthmaguardian.nsw.gov.au`
- **Development:** `https://api-dev.asthmaguardian.nsw.gov.au`

## Authentication
All API endpoints require authentication via JWT tokens:
```
Authorization: Bearer <jwt_token>
```

## API Endpoints

### Air Quality Endpoints

#### GET /api/air-quality/current
Get current air quality data for a location.

**Query Parameters:**
- `postcode` (string, required): NSW postcode
- `latitude` (number, optional): Latitude coordinate
- `longitude` (number, optional): Longitude coordinate

**Response (200 OK):**
```json
{
    "location": {
        "postcode": "2000",
        "latitude": -33.8688,
        "longitude": 151.2093
    },
    "current": {
        "timestamp": "2024-12-19T10:30:00Z",
        "aqi": 45,
        "quality_rating": "good",
        "pollutants": {
            "pm25": 12.5,
            "pm10": 18.2,
            "ozone": 0.045,
            "no2": 0.025,
            "so2": 0.008
        }
    },
    "forecast": [
        {
            "timestamp": "2024-12-19T11:00:00Z",
            "aqi": 48,
            "quality_rating": "good"
        }
    ]
}
```

#### GET /api/air-quality/history
Get historical air quality data for a location.

**Query Parameters:**
- `postcode` (string, required): NSW postcode
- `start_date` (string, required): ISO 8601 date
- `end_date` (string, required): ISO 8601 date
- `limit` (number, optional): Maximum records (default: 100)

**Response (200 OK):**
```json
{
    "location": {
        "postcode": "2000",
        "latitude": -33.8688,
        "longitude": 151.2093
    },
    "data": [
        {
            "timestamp": "2024-12-19T10:00:00Z",
            "aqi": 45,
            "quality_rating": "good",
            "pollutants": {
                "pm25": 12.5,
                "pm10": 18.2,
                "ozone": 0.045,
                "no2": 0.025,
                "so2": 0.008
            }
        }
    ],
    "pagination": {
        "next_token": "eyJ0aW1lc3RhbXAiOiIyMDI0LTEyLTE5VDEwOjAwOjAwWiJ9"
    }
}
```

### User Profile Endpoints

#### GET /api/users/profile
Get current user profile.

**Response (200 OK):**
```json
{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "asthma_severity": "moderate",
    "location": {
        "postcode": "2000",
        "latitude": -33.8688,
        "longitude": 151.2093
    },
    "sensitivity_settings": {
        "pm25_threshold": 25.0,
        "pm10_threshold": 50.0,
        "ozone_threshold": 0.1,
        "no2_threshold": 0.05,
        "so2_threshold": 0.02
    },
    "notification_preferences": {
        "email_enabled": true,
        "sms_enabled": false,
        "push_enabled": true,
        "frequency": "immediate"
    },
    "created_at": "2024-12-01T00:00:00Z",
    "updated_at": "2024-12-19T10:30:00Z"
}
```

#### PUT /api/users/profile
Update user profile.

**Request Body:**
```json
{
    "asthma_severity": "moderate",
    "location": {
        "postcode": "2000",
        "latitude": -33.8688,
        "longitude": 151.2093
    },
    "sensitivity_settings": {
        "pm25_threshold": 25.0,
        "pm10_threshold": 50.0,
        "ozone_threshold": 0.1,
        "no2_threshold": 0.05,
        "so2_threshold": 0.02
    },
    "notification_preferences": {
        "email_enabled": true,
        "sms_enabled": false,
        "push_enabled": true,
        "frequency": "immediate"
    }
}
```

**Response (200 OK):**
```json
{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "message": "Profile updated successfully",
    "updated_at": "2024-12-19T10:30:00Z"
}
```

### Guidance Endpoints

#### GET /api/guidance/recommendations
Get personalized guidance recommendations.

**Query Parameters:**
- `postcode` (string, optional): Override user's default location
- `include_forecast` (boolean, optional): Include forecast recommendations

**Response (200 OK):**
```json
{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "location": {
        "postcode": "2000",
        "latitude": -33.8688,
        "longitude": 151.2093
    },
    "timestamp": "2024-12-19T10:30:00Z",
    "risk_level": "low",
    "recommendations": [
        {
            "category": "outdoor_activities",
            "title": "Safe for outdoor exercise",
            "description": "Air quality is good. You can safely engage in outdoor activities.",
            "priority": "low"
        },
        {
            "category": "medication",
            "title": "Continue regular medication",
            "description": "No changes to your medication routine needed.",
            "priority": "low"
        }
    ],
    "air_quality_context": {
        "current_aqi": 45,
        "quality_rating": "good",
        "trend": "stable"
    }
}
```

### Notification Endpoints

#### POST /api/notifications/subscribe
Subscribe to notifications.

**Request Body:**
```json
{
    "notification_types": ["air_quality", "health_risk"],
    "channels": ["email", "push"],
    "frequency": "immediate",
    "thresholds": {
        "pm25": 25.0,
        "pm10": 50.0
    }
}
```

**Response (200 OK):**
```json
{
    "subscription_id": "sub_123e4567-e89b-12d3-a456-426614174000",
    "status": "active",
    "message": "Successfully subscribed to notifications"
}
```

#### GET /api/notifications/history
Get notification history.

**Query Parameters:**
- `limit` (number, optional): Maximum records (default: 50)
- `status` (string, optional): Filter by status (sent, delivered, failed)

**Response (200 OK):**
```json
{
    "notifications": [
        {
            "notification_id": "notif_123e4567-e89b-12d3-a456-426614174000",
            "type": "air_quality",
            "severity": "medium",
            "message": "Air quality is deteriorating in your area",
            "status": "delivered",
            "delivery_method": "email",
            "created_at": "2024-12-19T10:00:00Z",
            "sent_at": "2024-12-19T10:01:00Z"
        }
    ],
    "pagination": {
        "next_token": "eyJub3RpZmljYXRpb25faWQiOiJub3RpZl8xMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAifQ=="
    }
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "bad_request",
    "message": "Invalid request parameters",
    "details": {
        "field": "postcode",
        "issue": "Invalid NSW postcode format"
    }
}
```

### 401 Unauthorized
```json
{
    "error": "unauthorized",
    "message": "Invalid or expired authentication token"
}
```

### 403 Forbidden
```json
{
    "error": "forbidden",
    "message": "Insufficient permissions for this operation"
}
```

### 404 Not Found
```json
{
    "error": "not_found",
    "message": "Requested resource not found"
}
```

### 429 Too Many Requests
```json
{
    "error": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please try again later.",
    "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
    "error": "internal_server_error",
    "message": "An unexpected error occurred",
    "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
}
```

## Rate Limiting
- **Authenticated requests:** 1000 requests per hour per user
- **Unauthenticated requests:** 100 requests per hour per IP
- **Burst limit:** 50 requests per minute

## Data Validation
- **Postcodes:** Must be valid NSW postcodes (1000-9999)
- **Coordinates:** Latitude (-37.5 to -28.0), Longitude (141.0 to 153.6)
- **Email:** Valid email format
- **Timestamps:** ISO 8601 format
- **Thresholds:** Positive numbers within valid ranges
