import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { useParams } from 'react-router-dom';

const StudentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Student Details - {id}
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>
          Detailed student information and analytics will be displayed here.
        </Typography>
      </Paper>
    </Box>
  );
};

export default StudentDetail;
