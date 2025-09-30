/**
 * Login Component
 * 
 * Simple login component for authentication.
 * For demo purposes, this provides a mock login experience.
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Container,
  Paper,
} from '@mui/material';
import {
  Login as LoginIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!email.trim()) {
      setError('Please enter your email address');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // For demo purposes, we'll simulate a login
      // In a real app, this would call an authentication API
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      
      // Set a mock token
      const mockToken = 'demo-token-' + Date.now();
      apiClient.setToken(mockToken);
      
      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err: any) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    setEmail('demo@asthmaguardian.nsw.gov.au');
    // Auto-trigger login after setting email
    setTimeout(() => {
      handleLogin(new Event('submit') as any);
    }, 100);
  };

  return (
    <Container maxWidth="sm">
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        py={4}
      >
        {/* Logo and Title */}
        <Box textAlign="center" mb={4}>
          <Typography variant="h3" component="h1" gutterBottom>
            🌬️ Asthma Guardian
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Stay safe on poor air quality days
          </Typography>
        </Box>

        {/* Login Card */}
        <Card sx={{ width: '100%', maxWidth: 400 }}>
          <CardContent sx={{ p: 4 }}>
            <Box display="flex" alignItems="center" mb={3}>
              <LoginIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h5" component="h2">
                Sign In
              </Typography>
            </Box>

            <Typography variant="body2" color="text.secondary" paragraph>
              Enter your email address to access your personalized air quality dashboard.
            </Typography>

            {/* Error Alert */}
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {/* Login Form */}
            <form onSubmit={handleLogin}>
              <TextField
                fullWidth
                label="Email Address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                margin="normal"
                required
                autoFocus
                InputProps={{
                  startAdornment: <PersonIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <LoginIcon />}
                sx={{ mt: 3, mb: 2 }}
              >
                {loading ? 'Signing In...' : 'Sign In'}
              </Button>
            </form>

            {/* Demo Login */}
            <Box textAlign="center" mt={3}>
              <Typography variant="body2" color="text.secondary" paragraph>
                Want to try the demo?
              </Typography>
              <Button
                variant="outlined"
                onClick={handleDemoLogin}
                disabled={loading}
                fullWidth
              >
                Try Demo
              </Button>
            </Box>
          </CardContent>
        </Card>

        {/* Features */}
        <Paper sx={{ p: 3, mt: 4, width: '100%', maxWidth: 400 }}>
          <Typography variant="h6" gutterBottom textAlign="center">
            Features
          </Typography>
          <Box component="ul" sx={{ m: 0, pl: 2 }}>
            <Typography component="li" variant="body2" color="text.secondary">
              Real-time air quality monitoring
            </Typography>
            <Typography component="li" variant="body2" color="text.secondary">
              Personalized asthma guidance
            </Typography>
            <Typography component="li" variant="body2" color="text.secondary">
              Multi-channel notifications
            </Typography>
            <Typography component="li" variant="body2" color="text.secondary">
              Location-based alerts
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;
