import React from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  Button,
  Divider,
} from '@mui/material';
import { CheckCircle as CheckCircleIcon } from '@mui/icons-material';

interface Alert {
  id: string;
  student_name: string;
  type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  message: string;
  created_at: string;
  resolved: boolean;
}

const Alerts: React.FC = () => {
  // Sample data
  const alerts: Alert[] = [
    {
      id: '1',
      student_name: 'John Doe',
      type: 'ACADEMIC_DECLINE',
      severity: 'HIGH',
      message: 'Significant drop in attendance over the past 2 weeks',
      created_at: '2024-03-23T10:30:00Z',
      resolved: false,
    },
    {
      id: '2',
      student_name: 'Sarah Williams',
      type: 'SUICIDE_RISK',
      severity: 'CRITICAL',
      message: 'High-risk indicators detected from behavioral patterns',
      created_at: '2024-03-23T09:15:00Z',
      resolved: false,
    },
    {
      id: '3',
      student_name: 'Mike Johnson',
      type: 'SOCIAL_ISOLATION',
      severity: 'MEDIUM',
      message: 'Reduced social interaction detected',
      created_at: '2024-03-22T14:20:00Z',
      resolved: true,
    },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'LOW':
        return 'success';
      case 'MEDIUM':
        return 'warning';
      case 'HIGH':
        return 'error';
      case 'CRITICAL':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Alerts
      </Typography>

      <Paper>
        <List>
          {alerts.map((alert, index) => (
            <React.Fragment key={alert.id}>
              <ListItem alignItems="flex-start">
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle1">
                        {alert.student_name}
                      </Typography>
                      <Chip
                        label={alert.severity}
                        color={getSeverityColor(alert.severity) as any}
                        size="small"
                      />
                      {alert.resolved && (
                        <CheckCircleIcon color="success" fontSize="small" />
                      )}
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="textPrimary">
                        {alert.message}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {alert.type} • {formatDate(alert.created_at)}
                      </Typography>
                    </Box>
                  }
                />
                <Box>
                  {!alert.resolved && (
                    <Button variant="outlined" size="small">
                      Resolve
                    </Button>
                  )}
                </Box>
              </ListItem>
              {index < alerts.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default Alerts;
