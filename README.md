# Instagram Repost Tool

A modern, clean web application for reposting Instagram Reels and YouTube Shorts to your Instagram account using Instagram Graph API with OAuth authentication.

## Overview

This project consists of:
1. A React frontend (insta-repost-web) with Instagram OAuth support
2. A Node.js Express backend (backend) with Instagram API integration
3. Python scripts for Instagram operations:
   - simple_repost_api.py - Original version using instagrapi
   - repost_with_graph_api_new.py - Updated version using Instagram Graph API
4. Vercel deployment configuration for production hosting

## Requirements

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- Python packages:
  - instagrapi
  - yt_dlp
- Node packages:
  - For frontend: React, etc.
  - For backend: Express, CORS, body-parser

## Setup Instructions

### GitHub Repository Setup

This project is designed to be hosted on GitHub with proper security precautions to prevent exposure of sensitive information:

1. The `.gitignore` file is configured to exclude sensitive files like `.env`
2. Always use environment variables for sensitive information
3. Never hardcode passwords, tokens, or secrets
4. For detailed GitHub setup instructions, see [GITHUB_SETUP_GUIDE.md](GITHUB_SETUP_GUIDE.md)

### Environment Variables

This project uses environment variables for configuration. Set up your environment:

1. Copy `.env.example` to `.env` in both the root directory, backend directory, and insta-repost-web directory
2. Fill in the required values:
   ```
   # Instagram API Configuration
   INSTAGRAM_CLIENT_ID=your_client_id_here
   INSTAGRAM_CLIENT_SECRET=your_client_secret_here
   INSTAGRAM_REDIRECT_URI=your_redirect_uri_here
   WEBHOOK_VERIFY_TOKEN=your_webhook_token_here

   # For fallback non-OAuth authentication (optional)
   INSTAGRAM_USERNAME=your_username_here
   INSTAGRAM_PASSWORD=your_password_here
   ```

### Backend Setup

1. Install Python dependencies:
   ```
   pip install instagrapi yt_dlp moviepy==1.0.3 requests python-dotenv
   ```

### Instagram Graph API Setup

1. Create a Professional Account on Instagram (Business or Creator)
2. Go to [Meta for Developers](https://developers.facebook.com/)
3. Create a new app and configure the following:
   - Choose "Consumer" type app
   - Set up Instagram API integration
   - Add required products: Instagram Basic Display, Instagram Graph API
   - Configure Valid OAuth Redirect URIs (e.g., https://your-domain.com/auth/callback)
   - Create privacy policy and terms URLs
   - Add these URLs to your app settings
4. Copy the App ID and App Secret to your environment variables
5. For details, see [INSTAGRAM_SETUP_GUIDE.md](INSTAGRAM_SETUP_GUIDE.md)

### Vercel Deployment

1. Install Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Configure environment variables in Vercel:
   - Go to your Vercel project settings
   - Add environment variables from your `.env` file
   - Make sure to set the following for proper operation:
     - `INSTAGRAM_CLIENT_ID`
     - `INSTAGRAM_CLIENT_SECRET`
     - `INSTAGRAM_REDIRECT_URI`
     - `WEBHOOK_VERIFY_TOKEN`
     - `REACT_APP_API_URL` (for frontend)
     - `REACT_APP_INSTAGRAM_APP_ID` (for frontend)
     - `REACT_APP_REDIRECT_URI` (for frontend)

3. Deploy your project:
   ```
   vercel --prod
   ```

2. Run the deployment script:
   ```
   powershell -File deploy_to_vercel.ps1
   ```

3. Deploy to Vercel:
   ```
   cd "C:\Users\rishi\Insta report system"
   vercel login
   vercel --prod
   ```

4. After deployment, your app will be available at:
   ```
   https://insta-repost.vercel.app
   ```

5. Update your Instagram App settings in the Meta Developer Portal with:
   - Valid OAuth Redirect URI: https://insta-repost.vercel.app/auth/callback
   - Deauthorize Callback URL: https://insta-repost.vercel.app/auth/deauthorize
   - Data Deletion Request URL: https://insta-repost.vercel.app/auth/delete-data

2. Navigate to the backend directory:
   ```
   cd "C:\Users\rishi\Insta report system\backend"
   ```

3. Install Node.js dependencies:
   ```
   npm install
   ```

4. Start the backend server:
   ```
   npm start
   ```
   
   The server will run on http://localhost:5000

### Frontend Setup

1. Navigate to the React app directory:
   ```
   cd "C:\Users\rishi\Insta report system\insta-repost-web"
   ```

2. Install Node.js dependencies:
   ```
   npm install
   ```

3. Start the React development server:
   ```
   npm start
   ```
   
   The frontend will be available at http://localhost:3000

## How to Use

1. Open the web application in your browser at http://localhost:3000
2. Enter an Instagram Reel URL in the input field
3. Click the "Repost" button
4. The application will show the progress of downloading the reel, logging into Instagram, and uploading the reel
5. Once complete, you'll see a success message or any error that occurred

## Configuration

The Instagram username and password are currently hardcoded in the `simple_repost_api.py` file. You can change these values to your own Instagram credentials.

## Troubleshooting

- **Error uploading reel**: Make sure you have the correct version of moviepy (1.0.3) installed.
- **FFmpeg errors**: Ensure FFmpeg is installed and in your system PATH.
- **Backend connection errors**: Verify that the backend server is running on port 5000.

## Credits

This project uses several open-source libraries:
- instagrapi: For Instagram API interactions
- yt-dlp: For downloading Instagram reels
- React: For the frontend UI
- Express: For the backend server
