# Instagram API Webhook Verification

This document explains how to configure the webhook verification for the Instagram API integration.

## What is Webhook Verification?

When you set up a webhook for Instagram API, Facebook/Meta requires your server to respond to a verification request. This is a security measure to ensure that the webhook endpoint belongs to you.

## How Verification Works

1. Facebook/Meta sends a GET request to your webhook URL with query parameters:
   - `hub.mode=subscribe`
   - `hub.challenge=<random_string>`
   - `hub.verify_token=<your_verify_token>`

2. Your server must:
   - Check if `hub.verify_token` matches your predefined token
   - If it matches, respond with `hub.challenge` value
   - If it doesn't match, respond with 403 (Forbidden)

## Configuring Your Application

### 1. Set Up Environment Variables

The verification token is stored in an environment variable `WEBHOOK_VERIFY_TOKEN`. The default value is `insta-repost-verify-token-12345`, but you should change this to something secure for production.

### 2. Configure Meta Developer Dashboard

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Select your Instagram app
3. Navigate to Products > Webhooks
4. Click "Add Subscription"
5. Enter your callback URL: `https://insta-report-system-gpu1ik6ku.vercel.app/webhook`
6. Enter the Verify Token: `insta-repost-verify-token-12345` (or your custom token)
7. Select the needed subscription fields (e.g., `user_media` for Instagram media updates)
8. Click "Verify and Save"

### 3. Testing the Webhook

After setting up the webhook, you can verify it by:

1. Facebook will automatically try to verify the endpoint when you add the subscription
2. You can also manually trigger a verification from the Meta Developer Dashboard

### 4. Security Considerations

For production use:
- Use a strong, random string for the verification token
- Store the token securely in environment variables
- Do not commit the token to version control
- Consider using a token generator to create a secure token

## Troubleshooting

If verification fails:
1. Check that your server is reachable from the internet
2. Ensure your verify token matches exactly
3. Check server logs for any errors in the verification process
4. Verify your server responds with 200 OK and the challenge string

## Required Routes

The following routes are set up for Instagram API:

- `/webhook` - For webhook verification and receiving updates
- `/auth/callback` - OAuth authentication callback
- `/auth/deauthorize` - Handle user deauthorization
- `/auth/delete-data` - Handle data deletion requests
