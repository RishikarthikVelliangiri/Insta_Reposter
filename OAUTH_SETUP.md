# OAuth Setup Guide

This guide explains how to set up Instagram OAuth for the Instagram Repost Tool.

## Why OAuth?

OAuth provides a more secure way to authenticate with Instagram. Instead of hardcoding credentials, users log in through Instagram's official login page, and our application receives a token that can be used for authentication.

## Setup Steps

1. **Create a Meta Developer Account**
   - Go to [Meta for Developers](https://developers.facebook.com/)
   - Sign in with your Facebook account
   - Create a new app by clicking "My Apps" > "Create App"
   - Choose "Consumer" as the app type
   - Fill in the app details and create the app

2. **Configure Instagram Basic Display**
   - In your app dashboard, navigate to "Products" and add "Instagram Basic Display"
   - Under "Basic Display", click "Create New App"
   - Fill in the required details:
     - Valid OAuth Redirect URIs: `http://localhost:3000/auth/callback` (for development)
     - Deauthorize Callback URL: `http://localhost:3000/auth/deauthorize`
     - Data Deletion Request URL: `http://localhost:3000/auth/delete-data`

3. **Configure Your App**
   - Under "Settings" > "Basic", copy the App ID and App Secret
   - Update these values in the backend server:
     - Open `backend/server.js`
     - Replace the placeholder values for `INSTAGRAM_CLIENT_ID` and `INSTAGRAM_CLIENT_SECRET`

4. **Add Test Users**
   - Under "Roles" > "Test Users", add your Instagram account as a test user
   - This allows your Instagram account to use the app while it's in development mode

5. **Update Environment Variables**
   - For production, set the following environment variables:
     ```
     INSTAGRAM_CLIENT_ID=your_app_id
     INSTAGRAM_CLIENT_SECRET=your_app_secret
     ```

6. **Test the Authentication Flow**
   - Start the application
   - Click "Login with Instagram"
   - Complete the Instagram authentication
   - You should be redirected back to the application with your user information

## Troubleshooting

- **Invalid Redirect URI**: Make sure the redirect URI exactly matches what you've configured in the Meta Developer Console
- **Authentication Fails**: Check that your app is properly configured and your test user has been approved
- **Token Not Saving**: Ensure the backend server has write permissions to create the OAuth token file

## Security Considerations

- Never commit your App Secret to version control
- Use HTTPS in production
- Store tokens securely and implement token refresh logic for long-lived access
