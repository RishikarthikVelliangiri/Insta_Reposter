# Instagram OAuth and Webhook Setup Guide

This guide will help you configure your Instagram API and webhook settings in the Meta Developer Console to work with your deployed application.

## 1. Update App Settings in Meta Developer Console

1. Log in to the [Meta Developer Console](https://developers.facebook.com/)
2. Select your Instagram app (ID: 1842291649888953)
3. Go to "Settings > Basic"

### Update OAuth Redirect URLs

1. Find the "Valid OAuth Redirect URIs" section
2. Add the following URLs:
   - `https://insta-report-system-970xqhbou.vercel.app/auth/callback`
   - `https://insta-report-system-l1lc8sqx5.vercel.app/auth/callback` (latest deployment)
3. Click "Save Changes"

### Update App Domains

1. Find the "App Domains" section
2. Add the following domains:
   - `insta-report-system-970xqhbou.vercel.app`
   - `insta-report-system-l1lc8sqx5.vercel.app`
   - `insta-report-system-4zxlqolkg.vercel.app`
3. Click "Save Changes"

## 2. Configure Webhook

1. Go to "Products > Webhooks" in the left menu
2. Click "Edit" or "Add Webhook"
3. Configure the webhook with the following settings:
   - **Callback URL**: `https://insta-report-system-4zxlqolkg.vercel.app/webhook`
   - **Verify Token**: `insta-repost-verify-token-12345`
   - **Subscription Fields**: Select the fields you need (typically `mentions`, `comments`, etc.)
4. Click "Verify and Save"

## 3. Testing the Setup

You can test your OAuth and webhook setup using our test page:

1. Access the OAuth test page: [https://insta-report-system-l1lc8sqx5.vercel.app/oauth-test.html](https://insta-report-system-l1lc8sqx5.vercel.app/oauth-test.html)
2. Click "Login with Instagram" to test the OAuth flow
3. Click "Test Webhook" to verify your webhook configuration
4. Click "Check Auth Status" to verify your authentication status

## 4. Common Issues and Solutions

### OAuth Errors

- **Invalid redirect_uri**: Make sure the redirect URI in your app exactly matches what's configured in the Meta Developer Console.
- **User authentication failure**: Check that your app has the correct permissions configured.

### Webhook Verification Failures

- **Failed Challenge Verification**: Ensure the verify token matches exactly between your app and the Meta Developer Console.
- **Endpoint not accessible**: Make sure your backend is deployed and accessible.

## 5. Important Environment Variables

Your application is configured with the following environment variables:

### Frontend
```
REACT_APP_API_URL=https://insta-report-system-4zxlqolkg.vercel.app
REACT_APP_REDIRECT_URI=https://insta-report-system-970xqhbou.vercel.app/auth/callback
REACT_APP_INSTAGRAM_APP_ID=1842291649888953
```

### Backend
```
INSTAGRAM_CLIENT_ID=1842291649888953
INSTAGRAM_CLIENT_SECRET=4315cb405ae229639ec08
INSTAGRAM_REDIRECT_URI=https://insta-report-system-970xqhbou.vercel.app/auth/callback
WEBHOOK_VERIFY_TOKEN=insta-repost-verify-token-12345
FRONTEND_URL=https://insta-report-system-970xqhbou.vercel.app
```

## 6. Final Verification

After completing all the steps above, perform a full end-to-end test:

1. Go to your deployed application: [https://insta-report-system-l1lc8sqx5.vercel.app](https://insta-report-system-l1lc8sqx5.vercel.app)
2. Log in with Instagram
3. Test the reposting functionality
4. Verify that the webhooks are receiving events by checking the logs in your Vercel deployment
