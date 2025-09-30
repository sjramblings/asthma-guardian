/**
 * Dashboard Component
 * 
 * Main dashboard displaying air quality data, user guidance,
 * and real-time information.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Air as AirIcon,
  LocationOn as LocationIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { AirQualityData, GuidanceRecommendation } from '../api/client';
import apiClient from '../api/client';

const Dashboard: React.FC = () => {
  const [airQualityData, setAirQualityData] = useState<AirQualityData | null>(null);
  const [guidance, setGuidance] = useState<GuidanceRecommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [postcode, setPostcode] = useState('2000'); // Default to Sydney CBD
  const [refreshing, setRefreshing] = useState(false);

  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load air quality data
      const airQuality = await apiClient.getCurrentAirQuality(postcode);
      setAirQualityData(airQuality);

      // Load guidance (if user is logged in)
      const token = apiClient.getToken();
      if (token) {
        try {
          // For demo purposes, we'll use a mock user ID
          const guidanceData = await apiClient.getGuidance('demo-user-id');
          setGuidance(guidanceData);
        } catch (guidanceError) {
          console.warn('Could not load guidance:', guidanceError);
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handlePostcodeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPostcode(event.target.value);
  };

  const handlePostcodeSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    loadDashboardData();
  };

  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return '#4caf50'; // Good - Green
    if (aqi <= 100) return '#ffeb3b'; // Moderate - Yellow
    if (aqi <= 150) return '#ff9800'; // Unhealthy for sensitive groups - Orange
    if (aqi <= 200) return '#f44336'; // Unhealthy - Red
    if (aqi <= 300) return '#9c27b0'; // Very unhealthy - Purple
    return '#e91e63'; // Hazardous - Pink
  };

  const getAQILabel = (aqi: number) => {
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Moderate';
    if (aqi <= 150) return 'Unhealthy for Sensitive Groups';
    if (aqi <= 200) return 'Unhealthy';
    if (aqi <= 300) return 'Very Unhealthy';
    return 'Hazardous';
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return '#4caf50';
      case 'moderate': return '#ffeb3b';
      case 'high': return '#ff9800';
      case 'very_high': return '#f44336';
      default: return '#757575';
    }
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
          Air Quality Dashboard
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
          disabled={refreshing}
        >
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </Button>
      </Box>

      {/* Postcode Search */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <form onSubmit={handlePostcodeSubmit}>
          <TextField
            fullWidth
            label="NSW Postcode"
            value={postcode}
            onChange={handlePostcodeChange}
            placeholder="Enter NSW postcode (e.g., 2000)"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ maxWidth: 300 }}
          />
        </form>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Air Quality Data */}
      {airQualityData && (
        <Grid container spacing={3}>
          {/* Current Air Quality */}
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <AirIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Current Air Quality</Typography>
                </Box>
                
                <Box display="flex" alignItems="center" mb={2}>
                  <Typography variant="h2" sx={{ color: getAQIColor(airQualityData.current.aqi), mr: 2 }}>
                    {airQualityData.current.aqi}
                  </Typography>
                  <Box>
                    <Typography variant="h6" color="text.secondary">
                      AQI
                    </Typography>
                    <Chip
                      label={getAQILabel(airQualityData.current.aqi)}
                      sx={{
                        backgroundColor: getAQIColor(airQualityData.current.aqi),
                        color: 'white',
                        fontWeight: 'bold',
                      }}
                    />
                  </Box>
                </Box>

                <Box display="flex" alignItems="center" mb={2}>
                  <LocationIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary">
                    {airQualityData.location.postcode}
                    {airQualityData.location.latitude && airQualityData.location.longitude && (
                      <span> ({airQualityData.location.latitude.toFixed(4)}, {airQualityData.location.longitude.toFixed(4)})</span>
                    )}
                  </Typography>
                </Box>

                <Typography variant="body2" color="text.secondary" mb={2}>
                  Last updated: {new Date(airQualityData.current.timestamp).toLocaleString()}
                </Typography>

                {/* Pollutants */}
                <Typography variant="subtitle2" gutterBottom>
                  Pollutant Levels
                </Typography>
                <Box>
                  {Object.entries(airQualityData.current.pollutants).map(([key, value]) => (
                    <Box key={key} display="flex" alignItems="center" mb={1}>
                      <Typography variant="body2" sx={{ minWidth: 60, textTransform: 'uppercase' }}>
                        {key}:
                      </Typography>
                      <Box sx={{ flexGrow: 1, ml: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={Math.min((value / 100) * 100, 100)}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            backgroundColor: 'rgba(0,0,0,0.1)',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: value > 50 ? '#f44336' : value > 25 ? '#ff9800' : '#4caf50',
                            },
                          }}
                        />
                      </Box>
                      <Typography variant="body2" sx={{ ml: 1, minWidth: 40 }}>
                        {value.toFixed(1)}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Forecast */}
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Air Quality Forecast
                </Typography>
                {airQualityData.forecast && airQualityData.forecast.length > 0 ? (
                  <List>
                    {airQualityData.forecast.map((day, index) => (
                      <React.Fragment key={index}>
                        <ListItem>
                          <ListItemIcon>
                            <AirIcon />
                          </ListItemIcon>
                          <ListItemText
                            primary={new Date(day.date).toLocaleDateString()}
                            secondary={
                              <Box>
                                <Typography variant="body2">
                                  AQI: {day.aqi} - {getAQILabel(day.aqi)}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  Confidence: {day.confidence}
                                </Typography>
                              </Box>
                            }
                          />
                          <Chip
                            label={day.aqi}
                            size="small"
                            sx={{
                              backgroundColor: getAQIColor(day.aqi),
                              color: 'white',
                            }}
                          />
                        </ListItem>
                        {index < airQualityData.forecast!.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No forecast data available
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Guidance Recommendations */}
          {guidance && (
            <Grid size={{ xs: 12 }}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <InfoIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6">Personalized Guidance</Typography>
                    <Chip
                      label={guidance.risk_level.toUpperCase()}
                      sx={{
                        ml: 2,
                        backgroundColor: getRiskLevelColor(guidance.risk_level),
                        color: 'white',
                        fontWeight: 'bold',
                      }}
                    />
                  </Box>

                  <Typography variant="body1" paragraph>
                    {guidance.explanation}
                  </Typography>

                  {/* Recommendations */}
                  {guidance.recommendations.length > 0 && (
                    <Box mb={2}>
                      <Typography variant="subtitle1" gutterBottom>
                        Recommendations
                      </Typography>
                      <List dense>
                        {guidance.recommendations.map((rec, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              {rec.priority === 'high' ? (
                                <WarningIcon color="error" />
                              ) : rec.priority === 'medium' ? (
                                <InfoIcon color="warning" />
                              ) : (
                                <CheckCircleIcon color="success" />
                              )}
                            </ListItemIcon>
                            <ListItemText
                              primary={rec.title}
                              secondary={rec.description}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {/* Actions */}
                  {guidance.actions.length > 0 && (
                    <Box>
                      <Typography variant="subtitle1" gutterBottom>
                        Actions
                      </Typography>
                      <List dense>
                        {guidance.actions.map((action, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              {action.urgency === 'immediate' ? (
                                <WarningIcon color="error" />
                              ) : action.urgency === 'soon' ? (
                                <InfoIcon color="warning" />
                              ) : (
                                <CheckCircleIcon color="success" />
                              )}
                            </ListItemIcon>
                            <ListItemText
                              primary={action.description}
                              secondary={`Urgency: ${action.urgency}`}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}
    </Box>
  );
};

export default Dashboard;
