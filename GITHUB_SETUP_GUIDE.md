# GitHub Setup Guide for Instagram Repost App

This guide will help you properly set up your GitHub repository without exposing sensitive information.

## Step 1: Create a .gitignore File

First, create a `.gitignore` file to exclude sensitive files from being pushed to GitHub:

```bash
# Create .gitignore file in your project root
touch .gitignore
```

Add the following content to your `.gitignore` file:

```
# Environment variables
.env
.env.*
.env.local
.env.development
.env.test
.env.production
**/.env

# Python virtual environment
venv/
__pycache__/
*.py[cod]
*$py.class

# Node.js dependencies
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log

# Build outputs
/build
/dist
/.next
/.cache

# IDE and editor files
.idea/
.vscode/
*.swp
*.swo
*.sublime-workspace
*.sublime-project

# OS files
.DS_Store
Thumbs.db
```

## Step 2: Clean Up Password Hardcoding

1. Modify all Python files with hardcoded passwords:

   - Replace direct password assignments like `INSTAGRAM_PASSWORD = "DantesisBest101"` with:
   ```python
   INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")
   ```

   - Add proper environment loading at the top of the files:
   ```python
   import os
   from dotenv import load_dotenv
   
   # Load environment variables from .env file
   load_dotenv()
   ```

2. Add a template .env file (named `.env.example`) with placeholders:

```
# Instagram API Configuration
INSTAGRAM_CLIENT_ID=your_client_id_here
INSTAGRAM_CLIENT_SECRET=your_client_secret_here
INSTAGRAM_REDIRECT_URI=your_redirect_uri_here
WEBHOOK_VERIFY_TOKEN=your_webhook_token_here

# Instagram Credentials (for fallback non-OAuth authentication)
INSTAGRAM_USERNAME=your_username_here
INSTAGRAM_PASSWORD=your_password_here

# Build Configuration
CI=false
ESLINT_NO_DEV_ERRORS=true

# Server Configuration
PORT=3000
```

## Step 3: Create a GitHub Repository

1. Go to [GitHub](https://github.com/) and sign in
2. Click on the "+" icon in the top right corner and select "New repository"
3. Name your repository (e.g., "instagram-repost-app")
4. Add a description (optional)
5. Choose visibility (public or private)
6. Do not initialize with README, .gitignore, or license (we'll add our own)
7. Click "Create repository"

## Step 4: Initialize Local Repository and Push to GitHub

After cleaning up all sensitive data, run the following commands:

```bash
# Initialize Git repository (if not already done)
git init

# Add all files (except those in .gitignore)
git add .

# Commit changes
git commit -m "Initial commit"

# Add GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/instagram-repost-app.git

# Push to GitHub
git push -u origin main
```

## Step 5: Document Environment Setup Requirements

Add instructions to your README.md explaining how to set up the environment variables:

1. Copy the `.env.example` file to `.env`
2. Fill in the required values
3. Install dependencies
4. Run the application

## Security Notes

1. **NEVER commit .env files with real secrets to GitHub**
2. Consider using GitHub Secrets for CI/CD workflows if needed
3. Rotate any compromised secrets (client IDs, tokens, etc.) immediately
4. For Vercel deployments, use their Environment Variables settings in the project dashboard instead of committed .env files
