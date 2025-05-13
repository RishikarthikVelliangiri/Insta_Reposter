# URL Migration Summary

## Overview

This document summarizes the changes made to update the application from previous Vercel deployments to the new URL: `https://insta-reposter32.vercel.app`.

## Updated Files

The following files have been updated with the new deployment URL:

1. **Configuration Files**
   - `insta-repost-web/vercel.json` - Updated frontend environment variables
   - `backend/vercel.json` - Updated backend environment variables
   - `vercel.json` (root) - Updated environment variables

2. **Server Configuration**
   - `backend/server.js` - Updated CORS settings to allow the new domain

3. **Instagram API Integration**
   - `instagram_graph_api.py` - Updated redirect URI

4. **HTML/JS Files**
   - `insta-repost-web/public/oauth-test.html` - Updated API URL and frontend URL variables

5. **Documentation**
   - `INSTAGRAM_SETUP_GUIDE.md` - Updated all references to deployment URLs
   - `DEPLOYMENT_SUMMARY.md` - Updated all deployment information
   - `GITHUB_REPO_SUMMARY.md` - Updated next steps with new URLs

## Changes Required in Meta Developer Console

To complete the migration, the following changes must be made in the Meta Developer Console:

1. **Update OAuth Redirect URIs**
   - Add: `https://insta-reposter32.vercel.app/auth/callback`
   - Remove old redirect URIs if no longer needed

2. **Update App Domains**
   - Add: `insta-reposter32.vercel.app`
   - Remove old domains if no longer needed

3. **Update Privacy Policy & Terms of Service URLs**
   - Privacy Policy URL: `https://insta-reposter32.vercel.app/pp`
   - Terms of Service URL: `https://insta-reposter32.vercel.app/tos`
   - Ensure these pages are publicly accessible without requiring authentication

3. **Update Webhook Configuration**
   - Callback URL: `https://insta-reposter32.vercel.app/webhook`
   - Verify Token: `insta-repost-verify-token-12345` (unchanged)

## Verification Steps

After updating the code and Meta Developer Console settings:

1. Test the OAuth flow via: `https://insta-reposter32.vercel.app/oauth-test.html`
2. Verify webhook operation via: `https://insta-reposter32.vercel.app/webhook?test=true`
3. Test the full application functionality at: `https://insta-reposter32.vercel.app`

## Security Considerations

- No sensitive information like client secrets was exposed during this migration
- All environment variables have been properly updated in the Vercel deployment settings
- GitHub repository has been updated with the new URLs, but no sensitive information was committed

## Next Steps

1. Monitor the application for any issues related to the URL change
2. Consider rotating the Instagram client secret and webhook verification token for added security
3. Update any external documentation or links referring to the old deployment URLs
