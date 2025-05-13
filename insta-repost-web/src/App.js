import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import axios from 'axios';

// Import components
import AuthCallbackComponent from './components/AuthCallback';
import InstagramAuthComponent from './components/InstagramAuth';

// Material UI imports
import { 
  TextField, 
  Button, 
  Container, 
  Typography, 
  Box, 
  Paper, 
  CircularProgress, 
  Alert, 
  Snackbar
} from '@mui/material';
import InstagramIcon from '@mui/icons-material/Instagram';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import YouTubeIcon from '@mui/icons-material/YouTube';

// Keeping these temporary components for backward compatibility
// InstagramAuth component - will use the imported component instead
const InstagramAuth = ({ authenticated, user }) => {
  const handleLogin = () => {
    alert('This is a placeholder. Authentication feature will be implemented soon.');
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
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
          <Typography variant="body1">{user?.username || 'User'}</Typography>
          <Button variant="outlined" size="small">Log out</Button>
        </Box>
      ) : (
        <>
          <Typography variant="body1" mb={2}>Connect with Instagram</Typography>
          <Button variant="contained" startIcon={<InstagramIcon />} onClick={handleLogin}>
            Log in with Instagram
          </Button>
        </>
      )}
    </Box>
  );
};

// AuthCallback wrapper component
const AuthCallbackWrapper = ({ setUser, setAuthenticated }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 3 }}>
      <CircularProgress size={60} sx={{ mb: 3 }} />
      <Typography variant="h6">Authenticating with Instagram...</Typography>
    </Box>
  );
};

// Use the imported components instead of placeholders
const AuthCallback = AuthCallbackComponent;

function App() {
  const [url, setUrl] = useState('');
  const [caption, setCaption] = useState('');
  const [hashtags, setHashtags] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [error, setError] = useState(null);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [cooldownActive, setCooldownActive] = useState(false);
  const [cooldownRemaining, setCooldownRemaining] = useState(0);
  const [user, setUser] = useState(null);
  const [authenticated, setAuthenticated] = useState(false);
  // Handle user logout
  const handleLogout = async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      await axios.get(`${apiUrl}/api/auth/logout`);
      localStorage.removeItem('instagram_user');
      setUser(null);
      setAuthenticated(false);
    } catch (err) {
      console.error('Error during logout:', err);
    }
  };

  // Check for existing authentication on component mount
  useEffect(() => {
    // First check localStorage for cached user data
    const storedUser = localStorage.getItem('instagram_user');
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        setUser(userData);
        setAuthenticated(true);
      } catch (e) {
        console.error('Error parsing stored auth:', e);
      }
    }

    // Then verify with server
    const checkAuth = async () => {
      try {
        // Use environment variable for API URL
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
        const response = await axios.get(`${apiUrl}/api/auth/status`);
        if (response.data.authenticated) {
          setAuthenticated(true);
          setUser(response.data.user);
          localStorage.setItem('instagram_user', JSON.stringify(response.data.user));
        }
      } catch (err) {
        console.log('Not authenticated with server');
      }
    };
    
    checkAuth();
  }, []);
  
  // Cooldown timer effect
  useEffect(() => {
    if (!cooldownActive) return;
    
    const cooldownTimer = setInterval(() => {
      setCooldownRemaining(prevTime => {
        if (prevTime <= 1) {
          clearInterval(cooldownTimer);
          setCooldownActive(false);
          return 0;
        }
        return prevTime - 1;
      });
    }, 1000);
    
    return () => clearInterval(cooldownTimer);
  }, [cooldownActive]);

  // Monitor job status
  useEffect(() => {
    if (!jobId) return;
      const statusInterval = setInterval(async () => {
      try {
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
        const response = await axios.get(`${apiUrl}/api/status/${jobId}`);
        const data = response.data;
        
        if (data.success) {
          setJobStatus(data.jobStatus);
          
          // Stop polling if job is completed
          if (data.jobStatus.completed) {
            clearInterval(statusInterval);
            setIsSubmitting(false);
            
            // Show success notification
            if (data.jobStatus.success) {
              setOpenSnackbar(true);
              
              // Start cooldown timer if successful
              setCooldownActive(true);
              setCooldownRemaining(60);
            }
          }
        } else {
          setError(data.error || 'Failed to check job status');
          clearInterval(statusInterval);
          setIsSubmitting(false);
        }
      } catch (err) {
        setError('Server error while checking status');
        clearInterval(statusInterval);
        setIsSubmitting(false);
      }
    }, 1000); // Poll every second
    
    return () => clearInterval(statusInterval);
  }, [jobId]);
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const isInstagramUrl = url.includes('instagram.com');
    const isYoutubeShorts = url.includes('youtube.com/shorts') || url.includes('youtu.be');
    
    if (!isInstagramUrl && !isYoutubeShorts) {
      setError('Please enter a valid Instagram Reel or YouTube Shorts URL');
      return;
    }
    
    // Don't allow submission during cooldown
    if (cooldownActive) {
      setError(`Please wait ${cooldownRemaining} seconds before posting again`);
      return;
    }
    
    // Check if authenticated
    if (!authenticated) {
      setError('Please log in with Instagram first');
      return;
    }
    
    setError(null);
    setIsSubmitting(true);
    setJobStatus(null);
      try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await axios.post(`${apiUrl}/api/repost`, {
        videoUrl: url,
        caption: caption || undefined, // Only send if not empty
        hashtags: hashtags || undefined, // Only send if not empty
        source: isYoutubeShorts ? 'youtube' : 'instagram'
      });
      
      const data = response.data;
      
      if (data.success) {
        setJobId(data.jobId);
      } else {
        setError(data.error || 'Failed to start repost job');
        setIsSubmitting(false);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Server error. Please try again later.');
      setIsSubmitting(false);
    }
  };
  
  const handleCloseSnackbar = () => {
    setOpenSnackbar(false);
  };

  // Determine if the URL is for YouTube or Instagram
  const isYouTubeUrl = url.includes('youtube.com') || url.includes('youtu.be');
    // Handle successful login from OAuth
  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setAuthenticated(true);
    localStorage.setItem('instagram_user', JSON.stringify(userData));
  };

  return (
    <Router>
      <Routes>
        <Route path="/auth/callback" element={<AuthCallback onLoginSuccess={handleLoginSuccess} />} />
        <Route path="/" element={
          <Container maxWidth="md" className="App">
            <Box component="header" py={4} textAlign="center">
              <Box display="flex" justifyContent="center" alignItems="center" mb={1}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <InstagramIcon sx={{ fontSize: 40, color: '#E1306C' }} />
                  {isYouTubeUrl ? (
                    <YouTubeIcon sx={{ fontSize: 40, color: '#FF0000', ml: -1 }} />
                  ) : null}
                </Box>
                <Typography variant="h3" component="h1" fontWeight="400" color="primary" ml={1}>
                  Reels Repost
                </Typography>
              </Box>
              <Typography variant="h6" color="text.secondary" fontWeight="normal">
                Easily repost Instagram Reels and YouTube Shorts to your Instagram account
              </Typography>
            </Box>
              {/* Authentication section */}
            <Box mb={3} display="flex" justifyContent="center">
              <InstagramAuthComponent authenticated={authenticated} user={user} />
            </Box>
            
            <Box component="main" mb={4}>
              <Paper 
                elevation={2} 
                sx={{ 
                  p: 4, 
                  borderRadius: 3,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    boxShadow: '0 8px 16px rgba(0,0,0,0.1)'
                  }
                }}
              >
                <Box component="form" onSubmit={handleSubmit} mb={4}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TextField
                      fullWidth
                      variant="outlined"
                      label={isYouTubeUrl ? "YouTube Shorts URL" : "Instagram Reel URL"}
                      placeholder={isYouTubeUrl ? 
                        "https://youtube.com/shorts/..." :
                        "https://www.instagram.com/reel/..."
                      }
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      disabled={isSubmitting || !authenticated}
                      sx={{ mr: 2 }}
                      InputProps={{
                        sx: { borderRadius: '24px 0 0 24px' }
                      }}
                    />
                    <Button
                      type="submit"
                      variant="contained"
                      color="primary"
                      size="large"
                      disabled={isSubmitting || !url || cooldownActive || !authenticated}
                      sx={{ 
                        height: '56px',
                        borderRadius: '0 24px 24px 0',
                        textTransform: 'none',
                        px: 4
                      }}
                      startIcon={isSubmitting ? <CircularProgress size={20} color="inherit" /> : <CloudUploadIcon />}
                    >
                      {isSubmitting ? 'Processing...' : cooldownActive ? `Wait ${cooldownRemaining}s` : 'Repost'}
                    </Button>
                  </Box>
                  
                  {/* Caption and Hashtags fields */}
                  <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2, mt: 3 }}>
                    <TextField
                      fullWidth
                      variant="outlined"
                      label="Caption"
                      placeholder="Thanks for watching, hit follow for more! 🙏"
                      value={caption}
                      onChange={(e) => setCaption(e.target.value)}
                      disabled={isSubmitting || !authenticated}
                      multiline
                      rows={3}
                      sx={{ flexBasis: '50%' }}
                    />
                    <TextField
                      fullWidth
                      variant="outlined"
                      label="Hashtags"
                      placeholder="#reels #instareels #trending #viral #foryou #fyp #repost"
                      value={hashtags}
                      onChange={(e) => setHashtags(e.target.value)}
                      disabled={isSubmitting || !authenticated}
                      multiline
                      rows={3}
                      sx={{ flexBasis: '50%' }}
                    />
                  </Box>
                  
                  {error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      {error}
                    </Alert>
                  )}
                  
                  {cooldownActive && !isSubmitting && (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Typography variant="body2">
                          Cooldown period active to prevent Instagram from flagging automated posts.
                        </Typography>
                        <Typography variant="body2" fontWeight="bold" sx={{ ml: 2 }}>
                          {cooldownRemaining}s
                        </Typography>
                      </Box>
                      <Box sx={{ width: '100%', mt: 1 }}>
                        <div style={{ 
                          height: '4px', 
                          width: `${(cooldownRemaining / 60) * 100}%`, 
                          backgroundColor: '#1a73e8',
                          borderRadius: '2px',
                          transition: 'width 1s linear'
                        }} />
                      </Box>
                    </Alert>
                  )}
                </Box>
                
                {jobStatus && (
                  <Box mt={4}>
                    <Typography variant="h5" component="h2" mb={3} fontWeight="normal">
                      Repost Status
                    </Typography>
                    
                    {/* Simple status display */}              
                    <Box 
                      sx={{ 
                        p: 3, 
                        border: '1px solid #e0e0e0',
                        borderRadius: 2,
                        bgcolor: 'rgba(0, 0, 0, 0.02)',
                        mb: 3
                      }}
                    >
                      {/* Overall status heading */}
                      <Typography variant="body1" sx={{ mb: 3, fontWeight: 500, textAlign: 'center' }}>
                        {
                          jobStatus.completed && jobStatus.success ? 'Successfully Posted!' :
                          jobStatus.completed && !jobStatus.success ? 'Upload Failed' : 'Processing'
                        }
                      </Typography>
                      
                      {/* Three distinct phases visualization */}
                      <Box sx={{ mb: 3 }}>
                        {/* Phase 1: Download */}
                        <Box sx={{ 
                          mb: 3, 
                          p: 2, 
                          borderRadius: 2,
                          border: '1px solid',
                          borderColor: jobStatus.phases?.download?.current ? '#1976d2' :
                                    jobStatus.phases?.download?.completed ? '#4caf50' : '#e0e0e0',
                          bgcolor: jobStatus.phases?.download?.current ? 'rgba(25, 118, 210, 0.08)' :
                                  jobStatus.phases?.download?.completed ? 'rgba(76, 175, 80, 0.08)' : 'transparent'
                        }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Typography variant="subtitle1" fontWeight="medium">
                                1. Download
                              </Typography>
                            </Box>
                            <Box>
                              {jobStatus.phases?.download?.completed ? (
                                <Box sx={{ color: '#4caf50', display: 'flex', alignItems: 'center' }}>
                                  <span style={{ fontSize: '18px', marginRight: '4px' }}>✓</span>
                                  <Typography variant="body2">Complete</Typography>
                                </Box>
                              ) : jobStatus.phases?.download?.started ? (
                                <Box sx={{ color: '#1976d2', display: 'flex', alignItems: 'center' }}>
                                  <CircularProgress size={16} sx={{ mr: 1 }} />
                                  <Typography variant="body2">In Progress</Typography>
                                </Box>
                              ) : (
                                <Typography variant="body2" color="text.secondary">Pending</Typography>
                              )}
                            </Box>
                          </Box>
                          
                          {/* Description */}
                          <Typography variant="body2" color="text.secondary" mt={1}>
                            {jobStatus.phases?.download?.completed 
                              ? "Video successfully downloaded and processed."
                              : jobStatus.phases?.download?.started 
                              ? "Downloading video from source..."
                              : "Waiting to start download phase."}
                          </Typography>
                        </Box>
                      
                        {/* Phase 2: Login */}
                        <Box sx={{ 
                          mb: 3, 
                          p: 2, 
                          borderRadius: 2,
                          border: '1px solid',
                          borderColor: jobStatus.phases?.login?.current ? '#1976d2' :
                                    jobStatus.phases?.login?.completed ? '#4caf50' : '#e0e0e0',
                          bgcolor: jobStatus.phases?.login?.current ? 'rgba(25, 118, 210, 0.08)' :
                                  jobStatus.phases?.login?.completed ? 'rgba(76, 175, 80, 0.08)' : 'transparent'
                        }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Typography variant="subtitle1" fontWeight="medium">
                                2. Authentication
                              </Typography>
                            </Box>
                            <Box>
                              {jobStatus.phases?.login?.completed ? (
                                <Box sx={{ color: '#4caf50', display: 'flex', alignItems: 'center' }}>
                                  <span style={{ fontSize: '18px', marginRight: '4px' }}>✓</span>
                                  <Typography variant="body2">Complete</Typography>
                                </Box>
                              ) : jobStatus.phases?.login?.started ? (
                                <Box sx={{ color: '#1976d2', display: 'flex', alignItems: 'center' }}>
                                  <CircularProgress size={16} sx={{ mr: 1 }} />
                                  <Typography variant="body2">In Progress</Typography>
                                </Box>
                              ) : (
                                <Typography variant="body2" color="text.secondary">Pending</Typography>
                              )}
                            </Box>
                          </Box>
                          
                          {/* Description */}
                          <Typography variant="body2" color="text.secondary" mt={1}>
                            {jobStatus.phases?.login?.completed 
                              ? "Authentication successful."
                              : jobStatus.phases?.login?.started
                              ? "Authenticating with Instagram..." 
                              : "Waiting for download to complete."}
                          </Typography>
                        </Box>
                      
                        {/* Phase 3: Upload */}
                        <Box sx={{ 
                          p: 2, 
                          borderRadius: 2,
                          border: '1px solid',
                          borderColor: jobStatus.phases?.upload?.current ? '#1976d2' :
                                    jobStatus.phases?.upload?.completed ? '#4caf50' : '#e0e0e0',
                          bgcolor: jobStatus.phases?.upload?.current ? 'rgba(25, 118, 210, 0.08)' :
                                  jobStatus.phases?.upload?.completed ? 'rgba(76, 175, 80, 0.08)' : 'transparent'
                        }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Typography variant="subtitle1" fontWeight="medium">
                                3. Upload
                              </Typography>
                            </Box>
                            <Box>
                              {jobStatus.phases?.upload?.completed ? (
                                <Box sx={{ color: '#4caf50', display: 'flex', alignItems: 'center' }}>
                                  <span style={{ fontSize: '18px', marginRight: '4px' }}>✓</span>
                                  <Typography variant="body2">Complete</Typography>
                                </Box>
                              ) : jobStatus.phases?.upload?.started ? (
                                <Box sx={{ color: '#1976d2', display: 'flex', alignItems: 'center' }}>
                                  <CircularProgress size={16} sx={{ mr: 1 }} />
                                  <Typography variant="body2">In Progress</Typography>
                                </Box>
                              ) : (
                                <Typography variant="body2" color="text.secondary">Pending</Typography>
                              )}
                            </Box>
                          </Box>
                          
                          {/* Description */}
                          <Typography variant="body2" color="text.secondary" mt={1}>
                            {jobStatus.phases?.upload?.completed
                              ? "Upload successful! Content is now live."
                              : jobStatus.phases?.upload?.started
                              ? "Uploading video to Instagram..." 
                              : "Waiting for authentication to complete."}
                          </Typography>
                        </Box>
                      </Box>
                      
                      {/* Overall progress bar */}
                      <Box sx={{ mt: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="caption" fontWeight="500">Overall Progress</Typography>
                          <Typography variant="caption" fontWeight="500">
                            {jobStatus.phases?.upload?.completed ? '100%' : 
                            jobStatus.phases?.upload?.started ? '75%' : 
                            jobStatus.phases?.login?.completed ? '50%' : 
                            jobStatus.phases?.login?.started ? '35%' :
                            jobStatus.phases?.download?.completed ? '25%' :
                            jobStatus.phases?.download?.started ? '10%' : '0%'}
                          </Typography>
                        </Box>
                        
                        <Box sx={{ 
                          width: '100%', 
                          bgcolor: 'rgba(0, 0, 0, 0.1)', 
                          borderRadius: 1,
                          overflow: 'hidden',
                          height: 8
                        }}>
                          <Box sx={{
                            width: jobStatus.phases?.upload?.completed ? '100%' : 
                                  jobStatus.phases?.upload?.started ? '75%' : 
                                  jobStatus.phases?.login?.completed ? '50%' : 
                                  jobStatus.phases?.login?.started ? '35%' :
                                  jobStatus.phases?.download?.completed ? '25%' :
                                  jobStatus.phases?.download?.started ? '10%' : '0%',
                            bgcolor: jobStatus.completed && jobStatus.success ? '#4caf50' : '#1976d2',
                            height: '100%',
                            transition: 'width 0.8s ease-in-out'
                          }} />
                        </Box>
                      </Box>
                    </Box>
                    
                    {jobStatus.completed && jobStatus.success && (
                      <Alert 
                        severity="success" 
                        sx={{ 
                          mt: 2,
                          borderRadius: 2,
                          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
                        }}
                      >
                        Your video has been successfully reposted to Instagram!
                      </Alert>
                    )}
                    
                    {jobStatus.completed && !jobStatus.success && (
                      <Alert 
                        severity="error" 
                        sx={{ 
                          mt: 2,
                          borderRadius: 2
                        }}
                      >
                        Failed to complete the repost. Reason: {jobStatus.error || 'Unknown error'}
                      </Alert>
                    )}
                  </Box>
                )}
              </Paper>
            </Box>
            
            <Box component="footer" textAlign="center" py={2} mb={2}>
              <Typography variant="body2" color="text.secondary">
                &copy; {new Date().getFullYear()} Instagram Repost Tool
              </Typography>
            </Box>
            
            <Snackbar 
              open={openSnackbar} 
              autoHideDuration={6000} 
              onClose={handleCloseSnackbar}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
              <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
                Your video has been successfully reposted to Instagram!
              </Alert>
            </Snackbar>
          </Container>
        } />
      </Routes>
    </Router>
  );
}

export default App;