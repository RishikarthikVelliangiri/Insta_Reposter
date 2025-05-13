# Privacy Policy and Terms of Service Setup

## Overview

This document describes how the privacy policy and terms of service pages are set up for the Instagram Repost application. These pages are required by Meta/Instagram for your application to be approved.

## URLs

The privacy policy and terms of service are available at the following URLs:

1. **Privacy Policy**:
   - Full URL: `https://insta-reposter32.vercel.app/privacy-policy`
   - Short URL: `https://insta-reposter32.vercel.app/pp`

2. **Terms of Service**:
   - Full URL: `https://insta-reposter32.vercel.app/terms-of-service`
   - Short URL: `https://insta-reposter32.vercel.app/tos`

## Implementation Details

These pages are implemented as static HTML files:

- `insta-repost-web/public/privacy-policy.html`: Full privacy policy document
- `insta-repost-web/public/terms-of-service.html`: Full terms of service document
- `insta-repost-web/public/pp.html`: Shorter privacy policy document
- `insta-repost-web/public/tos.html`: Shorter terms of service document

## Routing Configuration

The URLs are configured in two places:

1. **Frontend Vercel configuration** (`insta-repost-web/vercel.json`):
   ```json
   "rewrites": [
     { "source": "/privacy-policy", "destination": "/privacy-policy.html" },
     { "source": "/terms-of-service", "destination": "/terms-of-service.html" },
     { "source": "/pp", "destination": "/pp.html" },
     { "source": "/tos", "destination": "/tos.html" }
   ]
   ```

2. **Root Vercel configuration** (`vercel.json`):
   ```json
   "rewrites": [
     // Other routes...
     {
       "source": "/privacy-policy",
       "destination": "/insta-repost-web/public/privacy-policy.html"
     },
     {
       "source": "/terms-of-service",
       "destination": "/insta-repost-web/public/terms-of-service.html"
     },
     {
       "source": "/pp",
       "destination": "/insta-repost-web/public/pp.html"
     },
     {
       "source": "/tos",
       "destination": "/insta-repost-web/public/tos.html"
     }
   ]
   ```

## Meta Developer Console Configuration

In the Meta Developer Console, you need to add the following URLs to your app settings:

1. Go to https://developers.facebook.com/ and select your app
2. Navigate to "Settings > Basic"
3. Find the "Privacy Policy URL" field and enter: `https://insta-reposter32.vercel.app/pp`
4. Find the "Terms of Service URL" field and enter: `https://insta-reposter32.vercel.app/tos`
5. Save changes

## Important Requirements

- Both pages must be publicly accessible (no login required)
- The content should align with Meta's requirements for privacy policies and terms of service
- The pages should be available at all times (not temporarily unavailable)
- The URLs must be secure (HTTPS)

## Verification

To verify these pages are properly accessible:

1. Open an incognito/private browser window (to ensure you're not logged in)
2. Visit the privacy policy URL: `https://insta-reposter32.vercel.app/pp`
3. Visit the terms of service URL: `https://insta-reposter32.vercel.app/tos`
4. Both should load without requiring authentication

If you encounter any issues with accessibility, check the Vercel deployment logs and ensure the routing configuration is correct.
