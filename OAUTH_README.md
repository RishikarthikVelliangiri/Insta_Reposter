# Instagram OAuth Implementation

This document provides instructions for setting up and testing the Instagram OAuth authentication feature that has been added to the Instagram Repost Tool.

## Setup Summary

The following components have been implemented:

1. **Frontend Components**:
   - `InstagramAuth.js`: Provides the "Login with Instagram" button and OAuth flow initiation
   - `AuthCallback.js`: Handles the OAuth callback and token exchange
   - React Router v6 integration for authentication routes
   - User state management for authenticated sessions

2. **Backend Components**:
   - OAuth callback endpoint in `server.js` to exchange auth code for access token
   - Token storage mechanism in `oauthHandler.js`

3. **Python Integration**:
   - Modified `simple_repost_api.py` to use OAuth token when available
   - Fallback to traditional login when OAuth is not configured

## Setup Instructions

1. **Register your app with Meta for Developers**:
   - Follow the detailed instructions in `OAUTH_SETUP.md`
   - Get your Client ID and Client Secret

2. **Update the configuration**:
   - In `backend/server.js`, replace the placeholder values:
     ```js
     const INSTAGRAM_CLIENT_ID = process.env.INSTAGRAM_CLIENT_ID || 'YOUR_INSTAGRAM_APP_ID';
     const INSTAGRAM_CLIENT_SECRET = process.env.INSTAGRAM_CLIENT_SECRET || 'YOUR_INSTAGRAM_APP_SECRET';
     ```
   - In `insta-repost-web/src/components/InstagramAuth.js`, update:
     ```js
     const instagramClientId = 'YOUR_INSTAGRAM_APP_ID';
     ```

3. **For production deployment**:
   - Set environment variables instead of hardcoding values
   - Ensure HTTPS is used for all OAuth redirects

## Testing the OAuth Flow

1. **Start both servers**:
   ```
   # Terminal 1 - Start backend
   cd "C:\Users\rishi\Insta report system\backend"
   npm run dev

   # Terminal 2 - Start frontend
   cd "C:\Users\rishi\Insta report system\insta-repost-web"
   npm start
   ```

2. **Test the login flow**:
   - Open `http://localhost:3000` in your browser
   - Click "Login with Instagram"
   - Authorize the application
   - You should be redirected back to the application

3. **Run automated test** (after obtaining an auth code):
   - First complete a manual login to get an auth code from the URL
   - Update the `testAuthCode` in `backend/test-oauth.js`
   - Run the test script:
     ```
     cd "C:\Users\rishi\Insta report system\backend"
     node test-oauth.js
     ```

## Troubleshooting

- **Invalid Redirect URI**: Make sure your redirect URI exactly matches what's configured in Meta Developer Console
- **Authentication Errors**: Check browser console and backend logs for details
- **"App Not Live" Error**: In development, make sure your Instagram account is added as a test user

## Security Notes

- Never commit your Client Secret to version control
- In production, store sensitive values in environment variables
- Implement token refresh logic for long-term usage
