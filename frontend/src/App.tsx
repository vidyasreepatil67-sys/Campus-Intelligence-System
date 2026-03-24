import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Students from './pages/Students';
import Alerts from './pages/Alerts';
import Resources from './pages/Resources';
import Analytics from './pages/Analytics';
import StudentDetail from './pages/StudentDetail';

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/students" element={<Students />} />
          <Route path="/students/:id" element={<StudentDetail />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/resources" element={<Resources />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Box>
    </Box>
  );
}

export default App;
