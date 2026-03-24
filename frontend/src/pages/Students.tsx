import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  TextField,
  InputAdornment,
  Pagination,
} from '@mui/material';
import { Search as SearchIcon, Visibility as VisibilityIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface Student {
  id: string;
  name: string;
  email: string;
  student_id: string;
  department: string;
  year: number;
  gpa: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  last_assessment: string;
}

const Students: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setStudents([
        {
          id: '1',
          name: 'John Doe',
          email: 'john.doe@university.edu',
          student_id: 'STU001',
          department: 'Computer Science',
          year: 3,
          gpa: 3.2,
          risk_level: 'MEDIUM',
          last_assessment: '2024-03-20',
        },
        {
          id: '2',
          name: 'Jane Smith',
          email: 'jane.smith@university.edu',
          student_id: 'STU002',
          department: 'Engineering',
          year: 2,
          gpa: 2.8,
          risk_level: 'HIGH',
          last_assessment: '2024-03-22',
        },
        {
          id: '3',
          name: 'Mike Johnson',
          email: 'mike.johnson@university.edu',
          student_id: 'STU003',
          department: 'Medicine',
          year: 4,
          gpa: 3.8,
          risk_level: 'LOW',
          last_assessment: '2024-03-21',
        },
        {
          id: '4',
          name: 'Sarah Williams',
          email: 'sarah.williams@university.edu',
          student_id: 'STU004',
          department: 'Arts',
          year: 1,
          gpa: 3.5,
          risk_level: 'CRITICAL',
          last_assessment: '2024-03-23',
        },
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const getRiskColor = (level: string) => {
    switch (level) {
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

  const filteredStudents = students.filter(student =>
    student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.student_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.department.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const itemsPerPage = 10;
  const totalPages = Math.ceil(filteredStudents.length / itemsPerPage);
  const paginatedStudents = filteredStudents.slice(
    (page - 1) * itemsPerPage,
    page * itemsPerPage
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <Typography>Loading students...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Students</Typography>
        <Button variant="contained" color="primary">
          Add Student
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search students by name, email, ID, or department..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Student ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Year</TableCell>
              <TableCell>GPA</TableCell>
              <TableCell>Risk Level</TableCell>
              <TableCell>Last Assessment</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedStudents.map((student) => (
              <TableRow key={student.id}>
                <TableCell>{student.student_id}</TableCell>
                <TableCell>{student.name}</TableCell>
                <TableCell>{student.email}</TableCell>
                <TableCell>{student.department}</TableCell>
                <TableCell>{student.year}</TableCell>
                <TableCell>{student.gpa.toFixed(2)}</TableCell>
                <TableCell>
                  <Chip
                    label={student.risk_level}
                    color={getRiskColor(student.risk_level) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{student.last_assessment}</TableCell>
                <TableCell>
                  <Button
                    size="small"
                    startIcon={<VisibilityIcon />}
                    onClick={() => navigate(`/students/${student.id}`)}
                  >
                    View
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={3}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, newPage) => setPage(newPage)}
            color="primary"
          />
        </Box>
      )}
    </Box>
  );
};

export default Students;
