# GitHub Push Checklist

Before pushing your code to GitHub, ensure you've completed the following steps to protect sensitive information:

## Security Checklist

- [ ] All hardcoded passwords have been removed and replaced with environment variables
- [ ] All `.env` files with real credentials are in `.gitignore`
- [ ] `.env.example` files are created with placeholder values
- [ ] No API keys, client secrets, or tokens are hardcoded in the source
- [ ] No session tokens or authentication cookies are committed
- [ ] Webhook verification tokens are stored as environment variables
- [ ] Instagram usernames and passwords are not hardcoded

## Files to Check

- [ ] `usernamepass.py`
- [ ] `simple_repost_api.py` and all its variants
- [ ] `instagram_graph_api.py`
- [ ] `repost_with_graph_api.py` and `repost_with_graph_api_new.py`
- [ ] `backend/server.js`
- [ ] `insta-repost-web/src` React components with API URLs

## GitHub Setup Steps

1. Create a new repository on GitHub (public or private)
2. Initialize the local repository:
   ```
   git init
   ```
3. Add all files (those not in .gitignore):
   ```
   git add .
   ```
4. Commit changes:
   ```
   git commit -m "Initial commit with secure configuration"
   ```
5. Add the GitHub repository as remote:
   ```
   git remote add origin https://github.com/YOUR_USERNAME/instagram-repost-app.git
   ```
6. Push to GitHub:
   ```
   git push -u origin main
   ```

## After Pushing

1. Verify that no sensitive information is visible in the GitHub repository
2. Set up proper documentation for users to understand the setup process
3. Consider setting up GitHub Actions for automated testing/deployment if needed
