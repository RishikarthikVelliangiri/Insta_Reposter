// OAuth flow test utility
const fs = require('fs');
const path = require('path');
const axios = require('axios');

// Configuration - replace with your actual values from Meta Developer Console
const testConfig = {
    clientId: process.env.INSTAGRAM_CLIENT_ID || 'YOUR_INSTAGRAM_APP_ID',
    clientSecret: process.env.INSTAGRAM_CLIENT_SECRET || 'YOUR_INSTAGRAM_APP_SECRET',
    redirectUri: 'http://localhost:3000/auth/callback',
    // This code should be obtained from manual testing the OAuth flow
    // After clicking "Login with Instagram" and authorizing, extract the code from URL
    testAuthCode: 'PASTE_AUTH_CODE_HERE' 
};

async function testOAuthFlow() {
    console.log('🧪 Testing Instagram OAuth Flow');
    console.log('------------------------------');
    
    if (testConfig.testAuthCode === 'PASTE_AUTH_CODE_HERE') {
        console.log('❌ Error: You need to set a test auth code first!');
        console.log('To get a test auth code:');
        console.log('1. Start your frontend and backend servers');
        console.log('2. Click "Login with Instagram"');
        console.log('3. Authorize your app');
        console.log('4. Copy the "code" parameter from the redirect URL');
        console.log('5. Paste it in this file as testAuthCode');
        return;
    }
    
    try {
        console.log('📤 Testing code exchange...');
        
        // Call the backend API to exchange the code for a token
        const response = await axios.post('http://localhost:5000/api/auth/instagram/callback', {
            code: testConfig.testAuthCode
        });
        
        if (response.data.success) {
            console.log('✅ OAuth code exchange successful!');
            console.log(`User authenticated: ${response.data.userData.username}`);
            
            // Check if token file was created
            const tokenFilePath = path.join(__dirname, '..', 'instagram_oauth.json');
            if (fs.existsSync(tokenFilePath)) {
                console.log('✅ OAuth token file created successfully!');
                const tokenData = JSON.parse(fs.readFileSync(tokenFilePath, 'utf8'));
                console.log(`Token saved for user: ${tokenData.username}`);
            } else {
                console.log('❌ OAuth token file was not created');
            }
        } else {
            console.log('❌ OAuth code exchange failed');
            console.log(`Error: ${response.data.error}`);
        }
    } catch (error) {
        console.log('❌ Test failed with error:');
        if (error.response) {
            console.log(error.response.data);
        } else {
            console.log(error.message);
        }
    }
}

// Run the test
testOAuthFlow();
