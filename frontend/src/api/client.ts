/**
 * API Client for Asthma Guardian v3
 * 
 * This module provides a centralized API client for communicating with
 * the Asthma Guardian v3 backend services.
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api-dev.asthmaguardian.nsw.gov.au';

// Types
export interface AirQualityData {
  location: {
    postcode: string;
    latitude?: number;
    longitude?: number;
  };
  current: {
    timestamp: string;
    aqi: number;
    quality_rating: string;
    pollutants: {
      pm25: number;
      pm10: number;
      ozone: number;
      no2: number;
      so2: number;
    };
  };
  forecast?: Array<{
    date: string;
    aqi: number;
    quality_rating: string;
    confidence: string;
  }>;
}

export interface UserProfile {
  user_id: string;
  email: string;
  asthma_severity: 'mild' | 'moderate' | 'severe';
  location: {
    postcode: string;
    latitude?: number;
    longitude?: number;
  };
  sensitivity_settings: {
    pm25_threshold: number;
    pm10_threshold: number;
    ozone_threshold: number;
    no2_threshold: number;
    so2_threshold: number;
  };
  notification_preferences: {
    email_enabled: boolean;
    sms_enabled: boolean;
    push_enabled: boolean;
    frequency: 'immediate' | 'hourly' | 'daily';
  };
  created_at: string;
  updated_at: string;
}

export interface GuidanceRecommendation {
  risk_level: 'low' | 'moderate' | 'high' | 'very_high';
  recommendations: Array<{
    type: 'immediate' | 'preventive' | 'long_term';
    title: string;
    description: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  actions: Array<{
    action: 'stay_indoors' | 'limit_exercise' | 'use_inhaler' | 'seek_medical_help';
    description: string;
    urgency: 'immediate' | 'soon' | 'when_possible';
  }>;
  explanation: string;
  generated_at: string;
  user_id: string;
  air_quality_data: any;
}

export interface Notification {
  notification_id: string;
  type: string;
  channel: string;
  message: string;
  subject?: string;
  status: string;
  sent_at: string;
  read_at?: string;
}

export interface NotificationPreferences {
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  frequency: 'immediate' | 'hourly' | 'daily';
}

export interface ApiError {
  error: {
    code: number;
    message: string;
  };
}

// API Client Class
class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication methods
  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  getToken(): string | null {
    return this.token || localStorage.getItem('auth_token');
  }

  // Air Quality API methods
  async getCurrentAirQuality(postcode: string, latitude?: number, longitude?: number): Promise<AirQualityData> {
    const params: any = { postcode };
    if (latitude) params.latitude = latitude;
    if (longitude) params.longitude = longitude;

    const response: AxiosResponse<AirQualityData> = await this.client.get('/api/air-quality/current', { params });
    return response.data;
  }

  async getAirQualityForecast(postcode: string): Promise<AirQualityData> {
    const response: AxiosResponse<AirQualityData> = await this.client.get('/api/air-quality/forecast', {
      params: { postcode }
    });
    return response.data;
  }

  async getAirQualityHistory(postcode: string, startDate?: string, endDate?: string): Promise<AirQualityData> {
    const params: any = { postcode };
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response: AxiosResponse<AirQualityData> = await this.client.get('/api/air-quality/history', { params });
    return response.data;
  }

  // User Profile API methods
  async createUserProfile(userData: Partial<UserProfile>): Promise<UserProfile> {
    const response: AxiosResponse<UserProfile> = await this.client.post('/api/users', userData);
    return response.data;
  }

  async getUserProfile(userId: string): Promise<UserProfile> {
    const response: AxiosResponse<UserProfile> = await this.client.get(`/api/users/${userId}`);
    return response.data;
  }

  async updateUserProfile(userId: string, userData: Partial<UserProfile>): Promise<UserProfile> {
    const response: AxiosResponse<UserProfile> = await this.client.put(`/api/users/${userId}`, userData);
    return response.data;
  }

  // Guidance API methods
  async getGuidance(userId: string): Promise<GuidanceRecommendation> {
    const response: AxiosResponse<GuidanceRecommendation> = await this.client.get(`/api/guidance/${userId}`);
    return response.data;
  }

  async createGuidance(userId: string): Promise<GuidanceRecommendation> {
    const response: AxiosResponse<GuidanceRecommendation> = await this.client.post('/api/guidance', { user_id: userId });
    return response.data;
  }

  // Notification API methods
  async getNotifications(userId: string, startDate?: string, endDate?: string): Promise<{ notifications: Notification[]; total_count: number }> {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response: AxiosResponse<{ notifications: Notification[]; total_count: number }> = await this.client.get(`/api/notifications/${userId}`, { params });
    return response.data;
  }

  async sendNotification(userId: string, message: string, subject?: string, type?: string): Promise<any> {
    const response: AxiosResponse<any> = await this.client.post('/api/notifications', {
      user_id: userId,
      message,
      subject,
      type
    });
    return response.data;
  }

  async updateNotificationPreferences(userId: string, preferences: NotificationPreferences): Promise<NotificationPreferences> {
    const response: AxiosResponse<NotificationPreferences> = await this.client.put(`/api/notifications/preferences/${userId}`, preferences);
    return response.data;
  }

  // Utility methods
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.get('/health');
      return true;
    } catch (error) {
      return false;
    }
  }
}

// Create and export singleton instance
export const apiClient = new ApiClient();
export default apiClient;
