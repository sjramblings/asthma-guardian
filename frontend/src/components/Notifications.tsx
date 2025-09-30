/**
 * Notifications Component
 * 
 * Component for managing notifications, viewing notification history,
 * and updating notification preferences.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Button,
  TextField,
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
  Grid,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Email as EmailIcon,
  Sms as SmsIcon,
  PhoneAndroid as PushIcon,
  Send as SendIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { Notification, NotificationPreferences } from '../api/client';
import apiClient from '../api/client';

const Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [sendDialogOpen, setSendDialogOpen] = useState(false);
  const [preferencesDialogOpen, setPreferencesDialogOpen] = useState(false);

  // Send notification form
  const [sendForm, setSendForm] = useState({
    message: '',
    subject: '',
    type: 'alert',
  });

  // Notification preferences form
  const [preferencesForm, setPreferencesForm] = useState<NotificationPreferences>({
    email_enabled: true,
    sms_enabled: false,
    push_enabled: true,
    frequency: 'immediate',
  });

  // Load notifications and preferences
  useEffect(() => {
    loadNotifications();
    loadPreferences();
  }, []);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      setError(null);

      const userId = 'demo-user-id';
      const data = await apiClient.getNotifications(userId);
      setNotifications(data.notifications);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const loadPreferences = async () => {
    try {
      const userId = 'demo-user-id';
      const prefs = await apiClient.updateNotificationPreferences(userId, preferencesForm);
      setPreferences(prefs);
      setPreferencesForm(prefs);
    } catch (err: any) {
      console.warn('Could not load notification preferences:', err);
    }
  };

  const handleSendNotification = async () => {
    try {
      setSending(true);
      setError(null);
      setSuccess(null);

      const userId = 'demo-user-id';
      await apiClient.sendNotification(
        userId,
        sendForm.message,
        sendForm.subject,
        sendForm.type
      );

      setSuccess('Notification sent successfully!');
      setSendDialogOpen(false);
      setSendForm({ message: '', subject: '', type: 'alert' });
      loadNotifications();
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to send notification');
    } finally {
      setSending(false);
    }
  };

  const handleUpdatePreferences = async () => {
    try {
      setSending(true);
      setError(null);
      setSuccess(null);

      const userId = 'demo-user-id';
      const updatedPrefs = await apiClient.updateNotificationPreferences(userId, preferencesForm);
      setPreferences(updatedPrefs);
      setSuccess('Notification preferences updated successfully!');
      setPreferencesDialogOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to update preferences');
    } finally {
      setSending(false);
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'email':
        return <EmailIcon />;
      case 'sms':
        return <SmsIcon />;
      case 'push':
        return <PushIcon />;
      default:
        return <NotificationsIcon />;
    }
  };

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'email':
        return 'primary';
      case 'sms':
        return 'secondary';
      case 'push':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'sent':
        return 'success';
      case 'failed':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
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
          Notifications
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadNotifications}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<SettingsIcon />}
            onClick={() => setPreferencesDialogOpen(true)}
          >
            Preferences
          </Button>
          <Button
            variant="contained"
            startIcon={<SendIcon />}
            onClick={() => setSendDialogOpen(true)}
          >
            Send Notification
          </Button>
        </Box>
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
        {/* Notification History */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Notification History
              </Typography>
              {notifications.length > 0 ? (
                <List>
                  {notifications.map((notification, index) => (
                    <React.Fragment key={notification.notification_id}>
                      <ListItem>
                        <ListItemIcon>
                          {getChannelIcon(notification.channel)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="body1">
                                {notification.subject || 'Air Quality Alert'}
                              </Typography>
                              <Chip
                                label={notification.channel.toUpperCase()}
                                size="small"
                                color={getChannelColor(notification.channel) as any}
                              />
                              <Chip
                                label={notification.status.toUpperCase()}
                                size="small"
                                color={getStatusColor(notification.status) as any}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                {notification.message}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                Sent: {formatDate(notification.sent_at)}
                                {notification.read_at && (
                                  <span> • Read: {formatDate(notification.read_at)}</span>
                                )}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < notifications.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No notifications found
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Current Preferences */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Preferences
              </Typography>
              {preferences ? (
                <Box>
                  <FormControlLabel
                    control={<Switch checked={preferences.email_enabled} disabled />}
                    label="Email Notifications"
                  />
                  <FormControlLabel
                    control={<Switch checked={preferences.sms_enabled} disabled />}
                    label="SMS Notifications"
                  />
                  <FormControlLabel
                    control={<Switch checked={preferences.push_enabled} disabled />}
                    label="Push Notifications"
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    Frequency: {preferences.frequency}
                  </Typography>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No preferences set
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Send Notification Dialog */}
      <Dialog open={sendDialogOpen} onClose={() => setSendDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Send Test Notification</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Subject"
            value={sendForm.subject}
            onChange={(e) => setSendForm(prev => ({ ...prev, subject: e.target.value }))}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Message"
            value={sendForm.message}
            onChange={(e) => setSendForm(prev => ({ ...prev, message: e.target.value }))}
            margin="normal"
            multiline
            rows={4}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Type</InputLabel>
            <Select
              value={sendForm.type}
              onChange={(e) => setSendForm(prev => ({ ...prev, type: e.target.value }))}
              label="Type"
            >
              <MenuItem value="alert">Alert</MenuItem>
              <MenuItem value="warning">Warning</MenuItem>
              <MenuItem value="info">Information</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSendDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSendNotification}
            variant="contained"
            disabled={sending || !sendForm.message}
            startIcon={sending ? <CircularProgress size={20} /> : <SendIcon />}
          >
            {sending ? 'Sending...' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Preferences Dialog */}
      <Dialog open={preferencesDialogOpen} onClose={() => setPreferencesDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Notification Preferences</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            Configure how and when you want to receive notifications about air quality conditions.
          </Typography>
          
          <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
            Notification Channels
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={preferencesForm.email_enabled}
                onChange={(e) => setPreferencesForm(prev => ({ ...prev, email_enabled: e.target.checked }))}
              />
            }
            label="Email Notifications"
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={preferencesForm.sms_enabled}
                onChange={(e) => setPreferencesForm(prev => ({ ...prev, sms_enabled: e.target.checked }))}
              />
            }
            label="SMS Notifications"
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={preferencesForm.push_enabled}
                onChange={(e) => setPreferencesForm(prev => ({ ...prev, push_enabled: e.target.checked }))}
              />
            }
            label="Push Notifications"
          />

          <FormControl fullWidth margin="normal">
            <InputLabel>Notification Frequency</InputLabel>
            <Select
              value={preferencesForm.frequency}
              onChange={(e) => setPreferencesForm(prev => ({ ...prev, frequency: e.target.value as any }))}
              label="Notification Frequency"
            >
              <MenuItem value="immediate">Immediate</MenuItem>
              <MenuItem value="hourly">Hourly</MenuItem>
              <MenuItem value="daily">Daily</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreferencesDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleUpdatePreferences}
            variant="contained"
            disabled={sending}
            startIcon={sending ? <CircularProgress size={20} /> : <SettingsIcon />}
          >
            {sending ? 'Saving...' : 'Save Preferences'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Notifications;
