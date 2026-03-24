import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
} from '@mui/material';
import { MeetingRoom as RoomIcon } from '@mui/icons-material';

interface Resource {
  id: string;
  name: string;
  type: string;
  location: string;
  capacity: number;
  current_utilization: number;
  utilization_rate: number;
  status: string;
}

const Resources: React.FC = () => {
  // Sample data
  const resources: Resource[] = [
    {
      id: '1',
      name: 'Hostel Block A - Room 101',
      type: 'hostel_room',
      location: 'Main Campus',
      capacity: 2,
      current_utilization: 2,
      utilization_rate: 100,
      status: 'active',
    },
    {
      id: '2',
      name: 'Library - Study Area 1',
      type: 'study_area',
      location: 'Academic Building',
      capacity: 50,
      current_utilization: 35,
      utilization_rate: 70,
      status: 'active',
    },
    {
      id: '3',
      name: 'Computer Lab 1',
      type: 'lab',
      location: 'Engineering Building',
      capacity: 30,
      current_utilization: 25,
      utilization_rate: 83,
      status: 'active',
    },
    {
      id: '4',
      name: 'Sports Complex - Gym',
      type: 'sports_facility',
      location: 'Sports Complex',
      capacity: 100,
      current_utilization: 45,
      utilization_rate: 45,
      status: 'active',
    },
  ];

  const getUtilizationColor = (rate: number) => {
    if (rate >= 90) return 'error';
    if (rate >= 70) return 'warning';
    return 'success';
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Resources
      </Typography>

      <Grid container spacing={3}>
        {resources.map((resource) => (
          <Grid item xs={12} sm={6} md={4} key={resource.id}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <RoomIcon color="action" sx={{ mr: 1 }} />
                  <Typography variant="h6" component="div">
                    {resource.name}
                  </Typography>
                </Box>
                
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  {resource.type} • {resource.location}
                </Typography>
                
                <Box mb={2}>
                  <Typography variant="body2" gutterBottom>
                    Utilization: {resource.current_utilization}/{resource.capacity}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={resource.utilization_rate}
                    color={getUtilizationColor(resource.utilization_rate) as any}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                  <Typography variant="caption" color="textSecondary">
                    {resource.utilization_rate}% utilized
                  </Typography>
                </Box>
                
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Chip
                    label={resource.status}
                    color={resource.status === 'active' ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default Resources;
