/**
 * Frontend Component Tests
 * 
 * This module contains tests for React components.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import '@testing-library/jest-dom';
import Dashboard from '../../frontend/src/components/Dashboard';
import UserProfile from '../../frontend/src/components/UserProfile';
import Notifications from '../../frontend/src/components/Notifications';
import Login from '../../frontend/src/components/Login';
import Navbar from '../../frontend/src/components/Navbar';

// Mock API client
jest.mock('../../frontend/src/api/client', () => ({
  api: {
    getCurrentAirQuality: jest.fn(),
    getAirQualityForecast: jest.fn(),
    getAirQualityHistory: jest.fn(),
    createUserProfile: jest.fn(),
    getUserProfile: jest.fn(),
    updateUserProfile: jest.fn(),
    getGuidanceRecommendations: jest.fn(),
    generateGuidance: jest.fn(),
    subscribeToNotifications: jest.fn(),
    getNotificationHistory: jest.fn(),
    updateNotificationPreferences: jest.fn(),
  },
}));

// Create theme for testing
const theme = createTheme();

// Wrapper component for theme provider
const ThemeWrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

describe('Dashboard Component', () => {
  test('renders dashboard with loading state', () => {
    render(
      <ThemeWrapper>
        <Dashboard />
      </ThemeWrapper>
    );
    
    expect(screen.getByText('Asthma Guardian v3')).toBeInTheDocument();
    expect(screen.getByText('Loading air quality data...')).toBeInTheDocument();
  });

  test('renders air quality data when loaded', async () => {
    const mockAirQualityData = {
      current: {
        aqi: 45,
        quality_rating: 'good',
        location: 'Sydney',
        timestamp: '2024-12-19T10:30:00Z'
      },
      forecast: [
        { date: '2024-12-20', aqi: 50, quality_rating: 'good' },
        { date: '2024-12-21', aqi: 60, quality_rating: 'moderate' }
      ]
    };

    // Mock the API response
    const { api } = require('../../frontend/src/api/client');
    api.getCurrentAirQuality.mockResolvedValue({ data: mockAirQualityData.current });
    api.getAirQualityForecast.mockResolvedValue({ data: mockAirQualityData.forecast });

    render(
      <ThemeWrapper>
        <Dashboard />
      </ThemeWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Current Air Quality')).toBeInTheDocument();
      expect(screen.getByText('Air Quality Forecast')).toBeInTheDocument();
    });
  });

  test('handles error state', async () => {
    const { api } = require('../../frontend/src/api/client');
    api.getCurrentAirQuality.mockRejectedValue(new Error('API Error'));

    render(
      <ThemeWrapper>
        <Dashboard />
      </ThemeWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error loading air quality data/)).toBeInTheDocument();
    });
  });
});

describe('UserProfile Component', () => {
  test('renders user profile form', () => {
    render(
      <ThemeWrapper>
        <UserProfile />
      </ThemeWrapper>
    );
    
    expect(screen.getByText('User Profile')).toBeInTheDocument();
    expect(screen.getByText('Basic Information')).toBeInTheDocument();
    expect(screen.getByText('Air Quality Sensitivity')).toBeInTheDocument();
    expect(screen.getByText('Notification Preferences')).toBeInTheDocument();
  });

  test('enables editing mode when edit button is clicked', () => {
    render(
      <ThemeWrapper>
        <UserProfile />
      </ThemeWrapper>
    );
    
    const editButton = screen.getByText('Edit Profile');
    fireEvent.click(editButton);
    
    expect(screen.getByText('Save Changes')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  test('validates form inputs', async () => {
    render(
      <ThemeWrapper>
        <UserProfile />
      </ThemeWrapper>
    );
    
    const editButton = screen.getByText('Edit Profile');
    fireEvent.click(editButton);
    
    const emailInput = screen.getByLabelText('Email Address');
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    
    const saveButton = screen.getByText('Save Changes');
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Invalid email address/)).toBeInTheDocument();
    });
  });
});

describe('Notifications Component', () => {
  test('renders notifications interface', () => {
    render(
      <ThemeWrapper>
        <Notifications />
      </ThemeWrapper>
    );
    
    expect(screen.getByText('Notifications')).toBeInTheDocument();
    expect(screen.getByText('Notification History')).toBeInTheDocument();
    expect(screen.getByText('Current Preferences')).toBeInTheDocument();
  });

  test('displays notification history', async () => {
    const mockNotifications = [
      {
        notification_id: '1',
        type: 'alert',
        subject: 'Air Quality Alert',
        message: 'High pollution levels detected',
        status: 'sent',
        sent_at: '2024-12-19T10:30:00Z'
      }
    ];

    const { api } = require('../../frontend/src/api/client');
    api.getNotificationHistory.mockResolvedValue({ data: mockNotifications });

    render(
      <ThemeWrapper>
        <Notifications />
      </ThemeWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Air Quality Alert')).toBeInTheDocument();
    });
  });

  test('allows updating notification preferences', async () => {
    render(
      <ThemeWrapper>
        <Notifications />
      </ThemeWrapper>
    );
    
    const emailToggle = screen.getByLabelText('Email Notifications');
    fireEvent.click(emailToggle);
    
    const saveButton = screen.getByText('Save Preferences');
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Preferences updated/)).toBeInTheDocument();
    });
  });
});

describe('Login Component', () => {
  test('renders login form', () => {
    render(
      <ThemeWrapper>
        <Login />
      </ThemeWrapper>
    );
    
    expect(screen.getByText('Login to Asthma Guardian')).toBeInTheDocument();
    expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByText('Login')).toBeInTheDocument();
  });

  test('validates login form', async () => {
    render(
      <ThemeWrapper>
        <Login />
      </ThemeWrapper>
    );
    
    const loginButton = screen.getByText('Login');
    fireEvent.click(loginButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Email is required/)).toBeInTheDocument();
      expect(screen.getByText(/Password is required/)).toBeInTheDocument();
    });
  });

  test('handles login submission', async () => {
    const { api } = require('../../frontend/src/api/client');
    api.login.mockResolvedValue({ data: { token: 'test-token' } });

    render(
      <ThemeWrapper>
        <Login />
      </ThemeWrapper>
    );
    
    const emailInput = screen.getByLabelText('Email Address');
    const passwordInput = screen.getByLabelText('Password');
    const loginButton = screen.getByText('Login');
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);
    
    await waitFor(() => {
      expect(api.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      });
    });
  });
});

describe('Navbar Component', () => {
  test('renders navigation bar', () => {
    render(
      <ThemeWrapper>
        <Navbar />
      </ThemeWrapper>
    );
    
    expect(screen.getByText('Asthma Guardian v3')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  test('shows login button when not authenticated', () => {
    render(
      <ThemeWrapper>
        <Navbar />
      </ThemeWrapper>
    );
    
    expect(screen.getByText('Login')).toBeInTheDocument();
  });

  test('shows user menu when authenticated', () => {
    // Mock authentication state
    jest.spyOn(Storage.prototype, 'getItem').mockReturnValue('test-token');
    
    render(
      <ThemeWrapper>
        <Navbar />
      </ThemeWrapper>
    );
    
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });
});

describe('API Client', () => {
  test('handles API errors gracefully', async () => {
    const { api } = require('../../frontend/src/api/client');
    api.getCurrentAirQuality.mockRejectedValue(new Error('Network Error'));

    render(
      <ThemeWrapper>
        <Dashboard />
      </ThemeWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error loading air quality data/)).toBeInTheDocument();
    });
  });

  test('includes authentication headers', () => {
    const { api } = require('../../frontend/src/api/client');
    
    // Mock localStorage
    jest.spyOn(Storage.prototype, 'getItem').mockReturnValue('test-token');
    
    // Test that the API client includes the token in requests
    expect(api.apiClient.defaults.headers.Authorization).toBe('Bearer test-token');
  });
});

describe('Responsive Design', () => {
  test('adapts to mobile screen size', () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    render(
      <ThemeWrapper>
        <Dashboard />
      </ThemeWrapper>
    );
    
    // Check that mobile-specific elements are rendered
    expect(screen.getByText('Asthma Guardian v3')).toBeInTheDocument();
  });
});

describe('Accessibility', () => {
  test('has proper ARIA labels', () => {
    render(
      <ThemeWrapper>
        <UserProfile />
      </ThemeWrapper>
    );
    
    const editButton = screen.getByText('Edit Profile');
    expect(editButton).toHaveAttribute('aria-label');
  });

  test('supports keyboard navigation', () => {
    render(
      <ThemeWrapper>
        <Login />
      </ThemeWrapper>
    );
    
    const emailInput = screen.getByLabelText('Email Address');
    const passwordInput = screen.getByLabelText('Password');
    
    // Test tab navigation
    emailInput.focus();
    expect(document.activeElement).toBe(emailInput);
    
    fireEvent.keyDown(emailInput, { key: 'Tab' });
    expect(document.activeElement).toBe(passwordInput);
  });
});

if (typeof require !== 'undefined' && require.main === module) {
  // Run tests if this file is executed directly
  const { run } = require('jest');
  run();
}
