import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  CircularProgress,
} from '@mui/material';
import {
  People as PeopleIcon,
  Warning as WarningIcon,
  MeetingRoom as RoomIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface DashboardData {
  students: {
    total: number;
    at_risk: number;
    risk_percentage: number;
  };
  alerts: {
    total: number;
    critical_unresolved: number;
  };
  resources: {
    average_utilization: number;
  };
  assessments: {
    recent_weekly: number;
  };
  interventions: {
    active: number;
  };
}

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setDashboardData({
        students: {
          total: 1250,
          at_risk: 87,
          risk_percentage: 6.96,
        },
        alerts: {
          total: 234,
          critical_unresolved: 12,
        },
        resources: {
          average_utilization: 78.5,
        },
        assessments: {
          recent_weekly: 45,
        },
        interventions: {
          active: 156,
        },
      });
      setLoading(false);
    }, 1000);
  }, []);

  // Sample data for charts
  const riskTrendData = [
    { date: 'Mon', low: 120, medium: 45, high: 23, critical: 8 },
    { date: 'Tue', low: 118, medium: 48, high: 25, critical: 10 },
    { date: 'Wed', low: 115, medium: 52, high: 28, critical: 12 },
    { date: 'Thu', low: 112, medium: 50, high: 30, critical: 11 },
    { date: 'Fri', low: 110, medium: 47, high: 32, critical: 13 },
    { date: 'Sat', low: 108, medium: 45, high: 31, critical: 14 },
    { date: 'Sun', low: 105, medium: 43, high: 29, critical: 15 },
  ];

  const resourceUtilizationData = [
    { name: 'Hostel Rooms', value: 85, fill: '#1976d2' },
    { name: 'Library', value: 92, fill: '#388e3c' },
    { name: 'Labs', value: 78, fill: '#f57c00' },
    { name: 'Sports Facilities', value: 65, fill: '#7b1fa2' },
    { name: 'Cafeteria', value: 88, fill: '#c2185b' },
  ];

  const StatCard: React.FC<{ 
    title: string; 
    value: string | number; 
    icon: React.ReactNode; 
    color: string 
  }> = ({ title, value, icon, color }) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center">
          <Box sx={{ mr: 2, color }}>{icon}</Box>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="overline">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Campus Intelligence Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Statistics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Students"
            value={dashboardData?.students.total || 0}
            icon={<PeopleIcon fontSize="large" />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Students at Risk"
            value={`${dashboardData?.students.at_risk} (${dashboardData?.students.risk_percentage}%)`}
            icon={<WarningIcon fontSize="large" />}
            color="#f44336"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Critical Alerts"
            value={dashboardData?.alerts.critical_unresolved || 0}
            icon={<WarningIcon fontSize="large" />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Resource Utilization"
            value={`${dashboardData?.resources.average_utilization}%`}
            icon={<RoomIcon fontSize="large" />}
            color="#4caf50"
          />
        </Grid>

        {/* Risk Trends Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Risk Level Trends (Last 7 Days)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={riskTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="critical" stroke="#f44336" strokeWidth={2} />
                <Line type="monotone" dataKey="high" stroke="#ff9800" strokeWidth={2} />
                <Line type="monotone" dataKey="medium" stroke="#ffeb3b" strokeWidth={2} />
                <Line type="monotone" dataKey="low" stroke="#4caf50" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Resource Utilization Pie Chart */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Resource Utilization by Type
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={resourceUtilizationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {resourceUtilizationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <Box display="flex" flexWrap="wrap" justifyContent="center" mt={2}>
              {resourceUtilizationData.map((item) => (
                <Box key={item.name} display="flex" alignItems="center" mx={1}>
                  <Box sx={{ width: 12, height: 12, backgroundColor: item.fill, mr: 1 }} />
                  <Typography variant="caption">{item.name}: {item.value}%</Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity Summary
            </Typography>
            <Box>
              <Typography variant="body2" paragraph>
                <strong>Weekly Risk Assessments:</strong> {dashboardData?.assessments.recent_weekly}
              </Typography>
              <Typography variant="body2" paragraph>
                <strong>Active Interventions:</strong> {dashboardData?.interventions.active}
              </Typography>
              <Typography variant="body2" paragraph>
                <strong>Total Alerts:</strong> {dashboardData?.alerts.total}
              </Typography>
              <Typography variant="body2">
                <strong>Students Requiring Attention:</strong> {dashboardData?.students.at_risk}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            <Box>
              <Typography variant="body2" paragraph>
                <strong>ML Models:</strong> ✅ Operational
              </Typography>
              <Typography variant="body2" paragraph>
                <strong>Data Sync:</strong> ✅ Up to date
              </Typography>
              <Typography variant="body2" paragraph>
                <strong>Alert System:</strong> ✅ Active
              </Typography>
              <Typography variant="body2">
                <strong>Resource Optimization:</strong> ✅ Running
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
