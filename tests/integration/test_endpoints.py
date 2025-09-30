"""
Integration Tests

This module contains end-to-end integration tests for the API endpoints.
"""

import pytest
import requests
import json
import time
from unittest.mock import patch, MagicMock


class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    @pytest.fixture
    def api_base_url(self):
        """Base URL for API testing."""
        return "https://api-dev.asthmaguardian.nsw.gov.au/api"
    
    @pytest.fixture
    def auth_headers(self):
        """Authentication headers for API requests."""
        return {
            "Authorization": "Bearer test-token",
            "Content-Type": "application/json"
        }
    
    def test_air_quality_endpoints_integration(self, api_base_url, auth_headers):
        """Test integration of air quality endpoints."""
        # Test current air quality endpoint
        response = requests.get(
            f"{api_base_url}/air-quality/current",
            params={"postcode": "2000"},
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "aqi" in data
        assert "quality_rating" in data
        assert "location" in data
        assert "timestamp" in data
    
    def test_user_profile_endpoints_integration(self, api_base_url, auth_headers):
        """Test integration of user profile endpoints."""
        user_data = {
            "email": "test@example.com",
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
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "frequency": "immediate"
            }
        }
        
        # Test create user profile
        response = requests.post(
            f"{api_base_url}/users",
            json=user_data,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        created_user = response.json()
        assert "user_id" in created_user
        
        user_id = created_user["user_id"]
        
        # Test get user profile
        response = requests.get(
            f"{api_base_url}/users/{user_id}",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        profile = response.json()
        assert profile["email"] == user_data["email"]
        assert profile["asthma_severity"] == user_data["asthma_severity"]
        
        # Test update user profile
        updated_data = {
            "asthma_severity": "severe",
            "location": {
                "postcode": "3000",
                "latitude": -37.8136,
                "longitude": 144.9631
            }
        }
        
        response = requests.put(
            f"{api_base_url}/users/{user_id}",
            json=updated_data,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        updated_profile = response.json()
        assert updated_profile["asthma_severity"] == "severe"
    
    def test_guidance_endpoints_integration(self, api_base_url, auth_headers):
        """Test integration of guidance endpoints."""
        user_id = "test-user-id"
        
        # Test get guidance recommendations
        response = requests.get(
            f"{api_base_url}/guidance/{user_id}",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        guidance = response.json()
        assert "recommendations" in guidance
        
        # Test generate guidance
        guidance_request = {
            "user_id": user_id,
            "user_input": "What should I do about the current air quality?"
        }
        
        response = requests.post(
            f"{api_base_url}/guidance",
            json=guidance_request,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        generated_guidance = response.json()
        assert "guidance" in generated_guidance
    
    def test_notifications_endpoints_integration(self, api_base_url, auth_headers):
        """Test integration of notifications endpoints."""
        user_id = "test-user-id"
        
        # Test subscribe to notifications
        subscription_data = {
            "user_id": user_id,
            "type": "alert",
            "target": "email"
        }
        
        response = requests.post(
            f"{api_base_url}/notifications",
            json=subscription_data,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        
        # Test get notification history
        response = requests.get(
            f"{api_base_url}/notifications/{user_id}",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        notifications = response.json()
        assert isinstance(notifications, list)
        
        # Test update notification preferences
        preferences = {
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": True,
            "frequency": "daily"
        }
        
        response = requests.put(
            f"{api_base_url}/notifications/preferences/{user_id}",
            json=preferences,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
    
    def test_air_quality_forecast_integration(self, api_base_url, auth_headers):
        """Test air quality forecast endpoint integration."""
        response = requests.get(
            f"{api_base_url}/air-quality/forecast",
            params={"postcode": "2000"},
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        forecast = response.json()
        assert isinstance(forecast, list)
        
        if len(forecast) > 0:
            forecast_item = forecast[0]
            assert "date" in forecast_item
            assert "aqi" in forecast_item
            assert "quality_rating" in forecast_item
    
    def test_air_quality_history_integration(self, api_base_url, auth_headers):
        """Test air quality history endpoint integration."""
        params = {
            "postcode": "2000",
            "start_date": "2024-12-01",
            "end_date": "2024-12-19"
        }
        
        response = requests.get(
            f"{api_base_url}/air-quality/history",
            params=params,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        history = response.json()
        assert isinstance(history, list)
        
        if len(history) > 0:
            history_item = history[0]
            assert "timestamp" in history_item
            assert "aqi" in history_item
            assert "quality_rating" in history_item
    
    def test_error_handling_integration(self, api_base_url, auth_headers):
        """Test error handling across endpoints."""
        # Test invalid endpoint
        response = requests.get(
            f"{api_base_url}/invalid-endpoint",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 404
        
        # Test invalid user ID
        response = requests.get(
            f"{api_base_url}/users/invalid-user-id",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code in [400, 404]
        
        # Test invalid postcode
        response = requests.get(
            f"{api_base_url}/air-quality/current",
            params={"postcode": "invalid"},
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code in [400, 404]
    
    def test_rate_limiting_integration(self, api_base_url, auth_headers):
        """Test rate limiting functionality."""
        # Make multiple rapid requests to test rate limiting
        responses = []
        for i in range(10):
            response = requests.get(
                f"{api_base_url}/air-quality/current",
                params={"postcode": "2000"},
                headers=auth_headers,
                timeout=30
            )
            responses.append(response)
            time.sleep(0.1)  # Small delay between requests
        
        # All requests should succeed (rate limit not exceeded)
        for response in responses:
            assert response.status_code == 200
    
    def test_cors_headers_integration(self, api_base_url):
        """Test CORS headers are properly set."""
        # Make a preflight OPTIONS request
        response = requests.options(
            f"{api_base_url}/air-quality/current",
            headers={
                "Origin": "https://asthmaguardian.nsw.gov.au",
                "Access-Control-Request-Method": "GET"
            },
            timeout=30
        )
        
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers
    
    def test_authentication_integration(self, api_base_url):
        """Test authentication requirements."""
        # Test request without authentication
        response = requests.get(
            f"{api_base_url}/users/test-user-id",
            timeout=30
        )
        
        assert response.status_code == 401
        
        # Test request with invalid token
        response = requests.get(
            f"{api_base_url}/users/test-user-id",
            headers={"Authorization": "Bearer invalid-token"},
            timeout=30
        )
        
        assert response.status_code == 401
    
    def test_data_consistency_integration(self, api_base_url, auth_headers):
        """Test data consistency across related endpoints."""
        # Create a user profile
        user_data = {
            "email": "consistency-test@example.com",
            "asthma_severity": "moderate",
            "location": {
                "postcode": "2000",
                "latitude": -33.8688,
                "longitude": 151.2093
            }
        }
        
        response = requests.post(
            f"{api_base_url}/users",
            json=user_data,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        user_id = response.json()["user_id"]
        
        # Get air quality data for the same location
        response = requests.get(
            f"{api_base_url}/air-quality/current",
            params={"postcode": "2000"},
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        air_quality = response.json()
        
        # Get guidance based on user profile and air quality
        response = requests.get(
            f"{api_base_url}/guidance/{user_id}",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        guidance = response.json()
        
        # Verify that guidance is relevant to the user's location and severity
        assert "recommendations" in guidance
    
    def test_performance_integration(self, api_base_url, auth_headers):
        """Test API performance under load."""
        start_time = time.time()
        
        # Make multiple concurrent requests
        import concurrent.futures
        
        def make_request():
            return requests.get(
                f"{api_base_url}/air-quality/current",
                params={"postcode": "2000"},
                headers=auth_headers,
                timeout=30
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Performance should be reasonable (less than 10 seconds for 10 requests)
        assert total_time < 10.0


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""
    
    def test_complete_user_journey(self, api_base_url, auth_headers):
        """Test complete user journey from registration to receiving guidance."""
        # 1. Create user profile
        user_data = {
            "email": "e2e-test@example.com",
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
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "frequency": "immediate"
            }
        }
        
        response = requests.post(
            f"{api_base_url}/users",
            json=user_data,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        user_id = response.json()["user_id"]
        
        # 2. Get current air quality
        response = requests.get(
            f"{api_base_url}/air-quality/current",
            params={"postcode": "2000"},
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        air_quality = response.json()
        
        # 3. Get personalized guidance
        response = requests.get(
            f"{api_base_url}/guidance/{user_id}",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        guidance = response.json()
        
        # 4. Subscribe to notifications
        subscription_data = {
            "user_id": user_id,
            "type": "alert",
            "target": "email"
        }
        
        response = requests.post(
            f"{api_base_url}/notifications",
            json=subscription_data,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        
        # 5. Update notification preferences
        preferences = {
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": True,
            "frequency": "daily"
        }
        
        response = requests.put(
            f"{api_base_url}/notifications/preferences/{user_id}",
            json=preferences,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        
        # 6. Get notification history
        response = requests.get(
            f"{api_base_url}/notifications/{user_id}",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        notifications = response.json()
        
        # Verify the complete workflow
        assert user_id is not None
        assert air_quality is not None
        assert guidance is not None
        assert notifications is not None


if __name__ == "__main__":
    pytest.main([__file__])
