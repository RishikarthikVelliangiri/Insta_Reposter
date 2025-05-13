// Load environment variables from .env file
require('dotenv').config();

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const path = require('path');
const axios = require('axios');
const fs = require('fs');
const app = express();
const PORT = process.env.PORT || 5000;

// Instagram OAuth configuration (to be set up in Meta Developer Console)
const INSTAGRAM_CLIENT_ID = process.env.INSTAGRAM_CLIENT_ID || 'REPLACE_WITH_YOUR_APP_ID';
const INSTAGRAM_CLIENT_SECRET = process.env.INSTAGRAM_CLIENT_SECRET || 'REPLACE_WITH_YOUR_APP_SECRET';
const INSTAGRAM_REDIRECT_URI = process.env.INSTAGRAM_REDIRECT_URI || 'http://localhost:3000/auth/callback';
const WEBHOOK_VERIFY_TOKEN = process.env.WEBHOOK_VERIFY_TOKEN || 'insta-repost-verify-token-12345';

// Middleware
app.use(cors({
  origin: [
    'https://insta-reposter32.vercel.app',
    process.env.FRONTEND_URL || 'http://localhost:3000'
  ],
  credentials: true
}));
app.use(bodyParser.json());

// Instagram webhook verification endpoint
app.get('/webhook', (req, res) => {
    // If there's a test parameter, return a simple success message for direct testing
    if (req.query.test === 'true') {
        return res.status(200).send({
            success: true,
            message: 'Webhook endpoint is accessible',
            environment: process.env.NODE_ENV || 'development',
            verifyToken: WEBHOOK_VERIFY_TOKEN ? 'Configured' : 'Not configured'
        });
    }
    
    // Parse params from the webhook verification request
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];
    
    console.log('Webhook verification request received:');
    console.log('- Mode:', mode);
    console.log('- Token:', token);
    console.log('- Challenge:', challenge);
    console.log('- Expected token:', WEBHOOK_VERIFY_TOKEN);
    
    // Check if a token and mode were sent
    if (mode && token) {
        // Check the mode and token sent are correct
        if (mode === 'subscribe' && token === WEBHOOK_VERIFY_TOKEN) {
            // Respond with 200 OK and challenge token from the request
            console.log('WEBHOOK_VERIFIED: Token matches expected value');
            res.status(200).send(challenge);
        } else {
            // Respond with '403 Forbidden' if verify tokens do not match
            console.log('VERIFICATION_FAILED: Token does not match expected value');
            res.sendStatus(403);
        }
    } else {
        // Respond with '400 Bad Request' if required parameters are missing
        console.log('MISSING_PARAMETERS: Mode or token is missing');
        res.sendStatus(400);
    }
});

// Also add a simple route for testing the backend deployment
app.get('/api/test', (req, res) => {
    res.status(200).json({
        success: true,
        message: 'Backend server is running',
        environment: process.env.NODE_ENV || 'development',
        time: new Date().toISOString()
    });
});

// Additional test endpoint to verify webhook is accessible
app.get('/webhook-test', (req, res) => {
    res.status(200).json({
        status: 'success',
        message: 'Webhook endpoint is accessible',
        webhook_token: WEBHOOK_VERIFY_TOKEN,
        timestamp: new Date().toISOString()
    });
});

// Also add a deauthorize callback and data deletion endpoints
app.post('/auth/deauthorize', (req, res) => {
    console.log('Deauthorization request received:', req.body);
    
    // Logic to handle user deauthorization
    // Here you would remove the user's token from your storage
    try {
        const tokenFilePath = path.join(__dirname, '..', 'instagram_oauth.json');
        if (fs.existsSync(tokenFilePath)) {
            fs.unlinkSync(tokenFilePath);
            console.log('OAuth token removed');
        }
        res.status(200).json({ success: true });
    } catch (error) {
        console.error('Error during deauthorization:', error);
        res.status(500).json({ success: false });
    }
});

app.post('/auth/delete-data', (req, res) => {
    console.log('Data deletion request received:', req.body);
    
    // Logic to delete all user data
    try {
        // Delete token data
        const tokenFilePath = path.join(__dirname, '..', 'instagram_oauth.json');
        if (fs.existsSync(tokenFilePath)) {
            fs.unlinkSync(tokenFilePath);
        }
        
        // Add code to delete any other user data you store
        
        res.status(200).json({ 
            success: true, 
            message: 'All user data has been deleted'
        });
    } catch (error) {
        console.error('Error during data deletion:', error);
        res.status(500).json({ success: false });
    }
});

// Status tracking for repost jobs
const jobStatus = {};

// API endpoint to handle repost requests
app.post('/api/repost', (req, res) => {
    const { videoUrl, caption, hashtags, source } = req.body;
    
    if (!videoUrl) {
        return res.status(400).json({ success: false, error: 'Video URL is required' });
    }
    
    // Generate a unique job ID
    const jobId = Date.now().toString();
    
    // Set initial status with three distinct phases
    jobStatus[jobId] = {
        status: 'processing',
        steps: [],
        log: [],
        completed: false,
        success: false,
        error: null,
        source: source || 'instagram',
        phases: {
            download: { started: false, completed: false, current: false },
            login: { started: false, completed: false, current: false },
            upload: { started: false, completed: false, current: false }
        }
    };
    
    // Send back the job ID immediately
    res.json({ success: true, jobId });
      // Prepare arguments for the Python script
    const scriptPath = path.join(__dirname, '..', 'simple_repost_api.py');
    const args = ['-u', scriptPath, videoUrl];
    
    // Add source parameter
    if (source) {
        args.push('--source');
        args.push(source);
    }
    
    // Add caption and hashtags if provided
    if (caption) {
        args.push('--caption');
        args.push(caption);
    }
    
    if (hashtags) {
        args.push('--hashtags');
        args.push(hashtags);
    }
    
    // Execute the Python script
    console.log(`Running Python with arguments: ${JSON.stringify(args)}`);
    const pythonProcess = spawn('python', args);
    
    // Set a timeout to ensure process completes even with output buffering
    let outputBuffer = '';
    
    // Collect data from stdout
    pythonProcess.stdout.on('data', (data) => {
        const message = data.toString().trim();
        outputBuffer += message + '\n';
        console.log(`Python stdout: ${message}`);
        
        // Update job status with logs
        jobStatus[jobId].log.push(message);        
          // Check for explicit step markers first
        if (message.includes('STEP_MARKER:')) {
            const step = message.split('STEP_MARKER:')[1].trim().toLowerCase();
            console.log(`Step marker detected: ${step}`);
            
            switch(step) {
                case 'download_started':
                    jobStatus[jobId].steps.push('download_started');
                    jobStatus[jobId].currentStep = 'download';
                    
                    // Update phase tracking
                    jobStatus[jobId].phases.download.started = true;
                    jobStatus[jobId].phases.download.current = true;
                    jobStatus[jobId].phases.login.current = false;
                    jobStatus[jobId].phases.upload.current = false;
                    break;
                    
                case 'download_completed':
                    jobStatus[jobId].steps.push('download_completed');
                    
                    // Update phase tracking
                    jobStatus[jobId].phases.download.completed = true;
                    jobStatus[jobId].phases.download.current = false;
                    break;
                    
                case 'login_started':
                    jobStatus[jobId].steps.push('login_started');
                    jobStatus[jobId].currentStep = 'login';
                    
                    // Update phase tracking
                    jobStatus[jobId].phases.login.started = true;
                    jobStatus[jobId].phases.login.current = true;
                    jobStatus[jobId].phases.download.current = false;
                    jobStatus[jobId].phases.upload.current = false;
                    break;
                    
                case 'login_completed':
                    jobStatus[jobId].steps.push('login_completed');
                    
                    // Update phase tracking
                    jobStatus[jobId].phases.login.completed = true;
                    jobStatus[jobId].phases.login.current = false;
                    break;
                    
                case 'upload_started':
                    jobStatus[jobId].steps.push('upload_started');
                    jobStatus[jobId].currentStep = 'upload';
                    
                    // Update phase tracking
                    jobStatus[jobId].phases.upload.started = true;
                    jobStatus[jobId].phases.upload.current = true;
                    jobStatus[jobId].phases.download.current = false;
                    jobStatus[jobId].phases.login.current = false;
                    break;
                    
                case 'upload_completed':
                    jobStatus[jobId].steps.push('upload_completed');
                    jobStatus[jobId].completed = true;
                    jobStatus[jobId].success = true;
                    
                    // Update phase tracking
                    jobStatus[jobId].phases.upload.completed = true;
                    jobStatus[jobId].phases.upload.current = false;
                    break;
                    
                case 'upload_failed':
                    jobStatus[jobId].error = "Upload failed";
                    jobStatus[jobId].completed = true;
                    jobStatus[jobId].success = false;
                    
                    // Update phase tracking
                    jobStatus[jobId].phases.upload.current = false;
                    break;
            }
        }
        // Fall back to checking for keyword indicators
        else if (message.includes('Downloading reel from:')) {
            if (!jobStatus[jobId].steps.includes('download_started')) {
                jobStatus[jobId].steps.push('download_started');
                jobStatus[jobId].currentStep = 'download';
            }
        } else if (message.includes('Downloaded video:')) {
            if (!jobStatus[jobId].steps.includes('download_completed')) {
                jobStatus[jobId].steps.push('download_completed');
            }
        } else if (message.includes('Logging into Instagram')) {
            if (!jobStatus[jobId].steps.includes('login_started')) {
                jobStatus[jobId].steps.push('login_started');
                jobStatus[jobId].currentStep = 'login';
            }
        } else if (message.includes('Logged in successfully')) {
            if (!jobStatus[jobId].steps.includes('login_completed')) {
                jobStatus[jobId].steps.push('login_completed');
            }
        } else if (message.includes('Uploading reel to Instagram')) {
            if (!jobStatus[jobId].steps.includes('upload_started')) {
                jobStatus[jobId].steps.push('upload_started');
                jobStatus[jobId].currentStep = 'upload';
            }
        } else if (message.includes('STEP_MARKER: UPLOAD_COMPLETED') || 
                 message.includes('Reel uploaded successfully') || 
                 message.includes('Video uploaded successfully') ||
                 message.includes('Upload successful') ||
                 message.includes('Upload completed successfully')) {
            if (!jobStatus[jobId].steps.includes('upload_completed')) {
                console.log('Upload completed detected in log output: ' + message);
                jobStatus[jobId].steps.push('upload_completed');
                jobStatus[jobId].completed = true;
                jobStatus[jobId].success = true;
            }
        } else if (message.includes('Error:') || 
                 message.includes('Failed to') || 
                 message.includes('STEP_MARKER: UPLOAD_FAILED') ||
                 message.includes('Upload failed')) {
            // Handle errors
            console.log('Error detected in log output: ' + message);
            jobStatus[jobId].error = message;
            if (!jobStatus[jobId].completed) {
                jobStatus[jobId].completed = true;
                jobStatus[jobId].success = false;
            }
        } else if (message.includes('FINAL_STATUS:')) {
            // Check for final status marker
            const status = message.split('FINAL_STATUS:')[1].trim().toLowerCase();
            if (status === 'success') {
                console.log('Final success status detected');
                if (!jobStatus[jobId].steps.includes('upload_completed')) {
                    jobStatus[jobId].steps.push('upload_completed');
                }
                jobStatus[jobId].completed = true;
                jobStatus[jobId].success = true;
            } else if (status === 'failed') {
                console.log('Final failed status detected');
                jobStatus[jobId].completed = true;
                jobStatus[jobId].success = false;
                if (!jobStatus[jobId].error) {
                    jobStatus[jobId].error = 'Process reported failure';
                }
            }
        }
    });
    
    // Handle errors from the Python process
    pythonProcess.stderr.on('data', (data) => {
        const errorMsg = data.toString().trim();
        console.error(`Python stderr: ${errorMsg}`);
        
        jobStatus[jobId].log.push(`ERROR: ${errorMsg}`);
        jobStatus[jobId].error = errorMsg;
    });
    
    // Handle process completion
    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
        
        // Add a small delay before processing completion to ensure all stdout has been processed
        setTimeout(() => {
            // Only mark as completed if we haven't already done so in the stdout handler
            if (!jobStatus[jobId].completed) {
                jobStatus[jobId].completed = true;
                
                // Check if we have upload_completed in the steps list
                const hasUploadCompleted = jobStatus[jobId].steps.includes('upload_completed');
                
                if (code !== 0) {
                    jobStatus[jobId].error = `Process exited with code ${code}`;
                    jobStatus[jobId].success = false;
                } else if (!jobStatus[jobId].error) {
                    // For success code (0), look for success markers in the logs if no explicit upload_completed step
                    if (!hasUploadCompleted) {
                        const logs = jobStatus[jobId].log.join('\n').toLowerCase();
                        
                        // More comprehensive check for success markers
                        const successIndicators = [
                            'upload successful',
                            'upload completed',
                            'upload_completed',
                            'video uploaded successfully',
                            'reel uploaded successfully',
                            'step_marker: upload_completed',
                            'final_status: success',
                            'downloaded video'
                        ];
                        
                        const hasSuccessIndicator = successIndicators.some(indicator => 
                            logs.includes(indicator.toLowerCase()));
                        
                        if (hasSuccessIndicator) {
                            console.log('Success indicators found in logs, marking job as successful');
                            // Add upload_completed step
                            jobStatus[jobId].steps.push('upload_completed');
                            jobStatus[jobId].success = true;
                        } else {
                            // Track the progress based on available step information
                            if (jobStatus[jobId].steps.includes('upload_started')) {
                                jobStatus[jobId].error = "Upload process started but didn't complete";
                            } else if (jobStatus[jobId].steps.includes('login_completed')) {
                                jobStatus[jobId].error = "Login successful but upload didn't start";
                            } else if (jobStatus[jobId].steps.includes('login_started')) {
                                jobStatus[jobId].error = "Login process started but didn't complete";
                            } else if (jobStatus[jobId].steps.includes('download_completed')) {
                                jobStatus[jobId].error = "Download completed but login didn't start";
                            } else if (jobStatus[jobId].steps.includes('download_started')) {
                                jobStatus[jobId].error = "Download started but didn't complete";
                            } else {
                                jobStatus[jobId].error = "Process completed without expected steps";
                            }
                        }
                    } else {
                        // We already have upload_completed in steps
                        jobStatus[jobId].success = true;
                    }
                }
            }
        }, 100); // 100ms delay to ensure all stdout is processed
    });
});

// API endpoint to check job status
app.get('/api/status/:jobId', (req, res) => {
    const { jobId } = req.params;
    
    if (!jobStatus[jobId]) {
        return res.status(404).json({ 
            success: false, 
            error: 'Job not found'
        });
    }
    
    res.json({
        success: true,
        jobStatus: jobStatus[jobId]
    });
});

// Import OAuth handler
const { saveOAuthToken, getOAuthToken } = require('./oauthHandler');

// OAuth status endpoint to check if user is authenticated
app.get('/api/auth/status', (req, res) => {
    try {
        const userData = getOAuthToken();
        
        if (userData && userData.access_token) {
            res.json({
                authenticated: true,
                user: {
                    id: userData.id,
                    username: userData.username,
                    profile_pic_url: userData.profile_pic_url || null
                }
            });
        } else {
            res.json({
                authenticated: false
            });
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
        res.status(500).json({
            authenticated: false,
            error: 'Failed to check authentication status'
        });
    }
});

// Logout endpoint
app.get('/api/auth/logout', (req, res) => {
    try {
        const tokenFilePath = path.join(__dirname, '..', 'instagram_oauth.json');
        if (fs.existsSync(tokenFilePath)) {
            fs.unlinkSync(tokenFilePath);
            console.log('OAuth token removed');
        }
        
        res.json({
            success: true,
            message: 'Successfully logged out'
        });
    } catch (error) {
        console.error('Error during logout:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to logout'
        });
    }
});

// Instagram OAuth callback endpoint
app.post('/api/auth/instagram/callback', async (req, res) => {
    const { code } = req.body;
    
    if (!code) {
        return res.status(400).json({ 
            success: false, 
            error: 'Authorization code is required' 
        });
    }
    
    try {
        // Exchange authorization code for access token
        const tokenResponse = await axios.post('https://api.instagram.com/oauth/access_token', {
            client_id: INSTAGRAM_CLIENT_ID,
            client_secret: INSTAGRAM_CLIENT_SECRET,
            grant_type: 'authorization_code',
            redirect_uri: INSTAGRAM_REDIRECT_URI,
            code: code
        }, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });
        
        const { access_token, user_id } = tokenResponse.data;
        
        // Get user profile information
        const userInfoResponse = await axios.get(`https://graph.instagram.com/v12.0/${user_id}`, {
            params: {
                fields: 'id,username',
                access_token: access_token
            }
        });        
        // Get profile picture URL if available
        let profile_pic_url = null;
        try {
            const mediaResponse = await axios.get(`https://graph.instagram.com/v12.0/${user_id}/media`, {
                params: {
                    fields: 'id,caption,media_type,media_url,permalink,thumbnail_url',
                    access_token: access_token,
                    limit: 1
                }
            });
            
            if (mediaResponse.data.data && mediaResponse.data.data.length > 0) {
                profile_pic_url = mediaResponse.data.data[0].media_url || 
                                  mediaResponse.data.data[0].thumbnail_url;
            }
        } catch (mediaError) {
            console.log('Could not fetch profile image, continuing without it');
        }
        
        const userData = {
            id: userInfoResponse.data.id,
            username: userInfoResponse.data.username,
            profile_pic_url: profile_pic_url,
            access_token: access_token
        };
        
        // Save the OAuth token to a file for the Python script to use
        saveOAuthToken(userData);
        
        res.json({
            success: true,
            user: {
                id: userData.id,
                username: userData.username,
                profile_pic_url: userData.profile_pic_url
            }
        });
    } catch (error) {
        console.error('Instagram OAuth error:', error.response?.data || error.message);
        res.status(500).json({
            success: false,
            error: 'Failed to authenticate with Instagram'
        });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
