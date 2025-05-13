import React, { useEffect, useState } from 'react';
import { Navigate, useSearchParams } from 'react-router-dom';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';
import axios from 'axios';

const AuthCallback = ({ setUser, setAuthenticated }) => {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const authCode = searchParams.get('code');
    
    if (!authCode) {
      setError('No authorization code received from Instagram');
      setLoading(false);
      return;
    }    const exchangeCodeForToken = async () => {
      try {
        // Use the environment variable for API URL
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
        
        const response = await axios.post(`${apiUrl}/api/auth/instagram/callback`, { 
          code: authCode 
        });
        
        if (response.data.success) {
          // Update auth state in parent component
          if (setAuthenticated) setAuthenticated(true);
          if (setUser && response.data.user) setUser(response.data.user);
          setSuccess(true);
        } else {
          setError(response.data.error || 'Failed to authenticate');
        }
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to authenticate with Instagram');
        console.error('Authentication error:', err);
      } finally {
        setLoading(false);
      }
    };

    exchangeCodeForToken();
  }, [searchParams, setAuthenticated, setUser]);

  // Redirect to home page if authenticated successfully
  if (success) {
    return <Navigate to="/" />;
  }

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '50vh',
      p: 3
    }}>
      {loading ? (
        <>
          <CircularProgress size={60} sx={{ mb: 3 }} />
          <Typography variant="h6">
            Authenticating with Instagram...
          </Typography>
        </>
      ) : error ? (
        <Alert severity="error" sx={{ maxWidth: '600px', width: '100%' }}>
          {error}
        </Alert>
      ) : (
        <Alert severity="success" sx={{ maxWidth: '600px', width: '100%' }}>
          Successfully authenticated with Instagram! Redirecting...
        </Alert>
      )}
    </Box>
  );
};

export default AuthCallback;