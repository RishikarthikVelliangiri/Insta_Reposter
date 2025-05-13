import React from 'react';
import { Button, Box, Typography, Avatar } from '@mui/material';
import InstagramIcon from '@mui/icons-material/Instagram';
import axios from 'axios';

const InstagramAuth = ({ authenticated, user }) => {
  const handleLogin = () => {
    // Define Instagram OAuth parameters
    const clientId = process.env.REACT_APP_INSTAGRAM_APP_ID || '1234567890';
    const redirectUri = encodeURIComponent(process.env.REACT_APP_REDIRECT_URI || 'http://localhost:3000/auth/callback');
    const scope = encodeURIComponent('user_profile,user_media');
    
    // Construct the Instagram authorization URL
    const instagramAuthUrl = `https://api.instagram.com/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}&response_type=code`;
    
    // Redirect to Instagram login
    window.location.href = instagramAuthUrl;
  };

  const handleLogout = async () => {
    try {
      await axios.get('http://localhost:5000/api/auth/logout');
      window.location.reload();
    } catch (err) {
      console.error('Error during logout:', err);
      alert('Failed to logout. Please try again.');
    }
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      p: 2, 
      borderRadius: 2,
      border: '1px solid #e0e0e0',
      maxWidth: '400px',
      width: '100%',
    }}>
      {authenticated && user ? (
        // Logged in state
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center',
          justifyContent: 'space-between',
          width: '100%',
          p: 1,
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar 
              src={user?.profile_pic_url} 
              alt={user?.username} 
              sx={{ width: 40, height: 40, mr: 2, border: '1px solid #e0e0e0' }} 
            />
            <Box>
              <Typography variant="body1" fontWeight="medium">
                {user?.username}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Connected to Instagram
              </Typography>
            </Box>
          </Box>
          
          <Button 
            variant="outlined" 
            color="primary" 
            size="small"
            onClick={handleLogout}
            sx={{ textTransform: 'none' }}
          >
            Log out
          </Button>
        </Box>
      ) : (
        // Logged out state
        <>
          <Typography variant="body1" align="center" mb={2}>
            Connect with Instagram to repost content
          </Typography>
          
          <Button
            variant="contained"
            color="primary"
            startIcon={<InstagramIcon />}
            onClick={handleLogin}
            sx={{ 
              textTransform: 'none',
              bgcolor: '#E1306C',
              '&:hover': { bgcolor: '#d62762' } 
            }}
          >
            Log in with Instagram
          </Button>
        </>
      )}
    </Box>
  );
};

export default InstagramAuth;
