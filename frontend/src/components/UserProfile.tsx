/**
 * User Profile Component
 * 
 * Component for managing user profile information, asthma severity,
 * location, and notification preferences.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Divider,
  Paper,
  Chip,
} from '@mui/material';
import {
  Person as PersonIcon,
  LocationOn as LocationIcon,
  Notifications as NotificationsIcon,
  Save as SaveIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { UserProfile as UserProfileType, NotificationPreferences } from '../api/client';
import apiClient from '../api/client';

const UserProfile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfileType | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    asthma_severity: 'mild' as 'mild' | 'moderate' | 'severe',
    location: {
      postcode: '',
      latitude: '',
      longitude: '',
    },
    sensitivity_settings: {
      pm25_threshold: 25,
      pm10_threshold: 50,
      ozone_threshold: 0.1,
      no2_threshold: 0.1,
      so2_threshold: 0.05,
    },
    notification_preferences: {
      email_enabled: true,
      sms_enabled: false,
      push_enabled: true,
      frequency: 'immediate' as 'immediate' | 'hourly' | 'daily',
    },
  });

  // Load user profile
  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      setError(null);

      // For demo purposes, we'll use a mock user ID
      // In a real app, this would come from authentication context
      const userId = 'demo-user-id';
      const userProfile = await apiClient.getUserProfile(userId);
      setProfile(userProfile);
      setFormData({
        email: userProfile.email,
        asthma_severity: userProfile.asthma_severity,
        location: {
          postcode: userProfile.location.postcode || '',
          latitude: userProfile.location.latitude?.toString() || '',
          longitude: userProfile.location.longitude?.toString() || '',
        },
        sensitivity_settings: userProfile.sensitivity_settings,
        notification_preferences: userProfile.notification_preferences,
      });
    } catch (err: any) {
      if (err.response?.status === 404) {
        // User profile doesn't exist, show create form
        setProfile(null);
      } else {
        setError(err.response?.data?.error?.message || 'Failed to load user profile');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleNestedInputChange = (parentField: string, childField: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [parentField]: {
        ...(prev[parentField as keyof typeof prev] as any),
        [childField]: value,
      },
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const userId = 'demo-user-id';
      
      // Convert form data to proper types
      const profileData = {
        ...formData,
        location: {
          ...formData.location,
          latitude: formData.location.latitude ? parseFloat(formData.location.latitude) : undefined,
          longitude: formData.location.longitude ? parseFloat(formData.location.longitude) : undefined,
        },
      };
      
      if (profile) {
        // Update existing profile
        const updatedProfile = await apiClient.updateUserProfile(userId, profileData);
        setProfile(updatedProfile);
        setSuccess('Profile updated successfully!');
      } else {
        // Create new profile
        const newProfile = await apiClient.createUserProfile(profileData);
        setProfile(newProfile);
        setSuccess('Profile created successfully!');
      }
      
      setEditing(false);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    if (profile) {
      setFormData({
        email: profile.email,
        asthma_severity: profile.asthma_severity,
        location: {
          postcode: profile.location.postcode || '',
          latitude: profile.location.latitude?.toString() || '',
          longitude: profile.location.longitude?.toString() || '',
        },
        sensitivity_settings: profile.sensitivity_settings,
        notification_preferences: profile.notification_preferences,
      });
    }
    setEditing(false);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          User Profile
        </Typography>
        {profile && !editing && (
          <Button
            variant="contained"
            startIcon={<EditIcon />}
            onClick={() => setEditing(true)}
          >
            Edit Profile
          </Button>
        )}
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Basic Information */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Basic Information</Typography>
              </Box>

              <TextField
                fullWidth
                label="Email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                disabled={!editing}
                margin="normal"
                required
              />

              <FormControl fullWidth margin="normal" disabled={!editing}>
                <InputLabel>Asthma Severity</InputLabel>
                <Select
                  value={formData.asthma_severity}
                  onChange={(e) => handleInputChange('asthma_severity', e.target.value)}
                  label="Asthma Severity"
                >
                  <MenuItem value="mild">Mild</MenuItem>
                  <MenuItem value="moderate">Moderate</MenuItem>
                  <MenuItem value="severe">Severe</MenuItem>
                </Select>
              </FormControl>

              <Box display="flex" alignItems="center" mt={2}>
                <LocationIcon sx={{ mr: 1, color: 'text.secondary' }} />
                <Typography variant="subtitle2">Location</Typography>
              </Box>

              <TextField
                fullWidth
                label="Postcode"
                value={formData.location.postcode}
                onChange={(e) => handleNestedInputChange('location', 'postcode', e.target.value)}
                disabled={!editing}
                margin="normal"
                placeholder="e.g., 2000"
              />

              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid size={{ xs: 6 }}>
                  <TextField
                    fullWidth
                    label="Latitude"
                    value={formData.location.latitude}
                    onChange={(e) => handleNestedInputChange('location', 'latitude', e.target.value)}
                    disabled={!editing}
                    type="number"
                    inputProps={{ step: 'any' }}
                  />
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <TextField
                    fullWidth
                    label="Longitude"
                    value={formData.location.longitude}
                    onChange={(e) => handleNestedInputChange('location', 'longitude', e.target.value)}
                    disabled={!editing}
                    type="number"
                    inputProps={{ step: 'any' }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Sensitivity Settings */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Air Quality Sensitivity
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Set your personal thresholds for air quality alerts. You'll be notified when levels exceed these values.
              </Typography>

              <TextField
                fullWidth
                label="PM2.5 Threshold (μg/m³)"
                value={formData.sensitivity_settings.pm25_threshold}
                onChange={(e) => handleNestedInputChange('sensitivity_settings', 'pm25_threshold', parseFloat(e.target.value))}
                disabled={!editing}
                margin="normal"
                type="number"
                inputProps={{ step: '0.1' }}
              />

              <TextField
                fullWidth
                label="PM10 Threshold (μg/m³)"
                value={formData.sensitivity_settings.pm10_threshold}
                onChange={(e) => handleNestedInputChange('sensitivity_settings', 'pm10_threshold', parseFloat(e.target.value))}
                disabled={!editing}
                margin="normal"
                type="number"
                inputProps={{ step: '0.1' }}
              />

              <TextField
                fullWidth
                label="Ozone Threshold (ppm)"
                value={formData.sensitivity_settings.ozone_threshold}
                onChange={(e) => handleNestedInputChange('sensitivity_settings', 'ozone_threshold', parseFloat(e.target.value))}
                disabled={!editing}
                margin="normal"
                type="number"
                inputProps={{ step: '0.001' }}
              />

              <TextField
                fullWidth
                label="NO₂ Threshold (ppm)"
                value={formData.sensitivity_settings.no2_threshold}
                onChange={(e) => handleNestedInputChange('sensitivity_settings', 'no2_threshold', parseFloat(e.target.value))}
                disabled={!editing}
                margin="normal"
                type="number"
                inputProps={{ step: '0.001' }}
              />

              <TextField
                fullWidth
                label="SO₂ Threshold (ppm)"
                value={formData.sensitivity_settings.so2_threshold}
                onChange={(e) => handleNestedInputChange('sensitivity_settings', 'so2_threshold', parseFloat(e.target.value))}
                disabled={!editing}
                margin="normal"
                type="number"
                inputProps={{ step: '0.001' }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Notification Preferences */}
        <Grid size={{ xs: 12 }}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <NotificationsIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Notification Preferences</Typography>
              </Box>

              <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Notification Channels
                  </Typography>
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.notification_preferences.email_enabled}
                        onChange={(e) => handleNestedInputChange('notification_preferences', 'email_enabled', e.target.checked)}
                        disabled={!editing}
                      />
                    }
                    label="Email Notifications"
                  />

                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.notification_preferences.sms_enabled}
                        onChange={(e) => handleNestedInputChange('notification_preferences', 'sms_enabled', e.target.checked)}
                        disabled={!editing}
                      />
                    }
                    label="SMS Notifications"
                  />

                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.notification_preferences.push_enabled}
                        onChange={(e) => handleNestedInputChange('notification_preferences', 'push_enabled', e.target.checked)}
                        disabled={!editing}
                      />
                    }
                    label="Push Notifications"
                  />
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                  <FormControl fullWidth disabled={!editing}>
                    <InputLabel>Notification Frequency</InputLabel>
                    <Select
                      value={formData.notification_preferences.frequency}
                      onChange={(e) => handleNestedInputChange('notification_preferences', 'frequency', e.target.value)}
                      label="Notification Frequency"
                    >
                      <MenuItem value="immediate">Immediate</MenuItem>
                      <MenuItem value="hourly">Hourly</MenuItem>
                      <MenuItem value="daily">Daily</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Action Buttons */}
        {editing && (
          <Grid size={{ xs: 12 }}>
            <Paper sx={{ p: 2 }}>
              <Box display="flex" gap={2} justifyContent="flex-end">
                <Button
                  variant="outlined"
                  onClick={handleCancel}
                  disabled={saving}
                >
                  Cancel
                </Button>
                <Button
                  variant="contained"
                  startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                  onClick={handleSave}
                  disabled={saving}
                >
                  {saving ? 'Saving...' : 'Save Profile'}
                </Button>
              </Box>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default UserProfile;
