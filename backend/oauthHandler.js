// OAuth token handler for Instagram OAuth
const fs = require('fs');
const path = require('path');

// Path for the OAuth token file
const tokenFilePath = path.join(__dirname, '..', 'instagram_oauth.json');

// Function to get the OAuth token from the file
const getOAuthToken = () => {
    try {
        if (fs.existsSync(tokenFilePath)) {
            const tokenData = fs.readFileSync(tokenFilePath, 'utf8');
            return JSON.parse(tokenData);
        }
        return null;
    } catch (error) {
        console.error('Error reading OAuth token:', error);
        return null;
    }
};

// Function to save the OAuth token to a file that the Python script can use
const saveOAuthToken = (userData) => {
    if (!userData || !userData.access_token || !userData.username) {
        console.error('Invalid OAuth user data provided');
        return false;
    }
    
    try {
        // Path to save the OAuth token file
        const tokenFilePath = path.join(__dirname, '..', 'instagram_oauth.json');
        
        // Write the token data to the file
        fs.writeFileSync(
            tokenFilePath, 
            JSON.stringify(userData, null, 2)
        );
        
        console.log(`OAuth token saved to ${tokenFilePath}`);
        return true;
    } catch (error) {
        console.error('Error saving OAuth token:', error);
        return false;
    }
};

module.exports = { saveOAuthToken, getOAuthToken };
