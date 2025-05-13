# Initialize Git repository and push to GitHub
# This script helps you set up a Git repository and push your code to GitHub

# Instructions:
# 1. Replace YOUR_USERNAME with your GitHub username
# 2. Replace REPO_NAME with your desired repository name
# 3. Run this script after ensuring all sensitive data is removed

# Set your GitHub information
$githubUsername = "RishikarthikVelliangiri"
$repoName = "Insta_Reposter"
$repoUrl = "https://github.com/RishikarthikVelliangiri/Insta_Reposter.git"

Write-Host "Initializing Git repository for Instagram Repost App..." -ForegroundColor Green

# Initialize Git if not already initialized
if (-not (Test-Path ".git")) {
    git init
    Write-Host "Git repository initialized." -ForegroundColor Green
} else {
    Write-Host "Git repository already exists." -ForegroundColor Yellow
}

# Check for .gitignore file
if (-not (Test-Path ".gitignore")) {
    Write-Host "ERROR: .gitignore file not found! This is required to prevent committing sensitive data." -ForegroundColor Red
    exit 1
}

# Verify .env files are in .gitignore
$gitignoreContent = Get-Content ".gitignore"
if ($gitignoreContent -notcontains ".env" -and $gitignoreContent -notcontains "**/.env") {
    Write-Host "WARNING: .env files might not be properly excluded in .gitignore!" -ForegroundColor Red
    $continue = Read-Host "Do you want to continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

# Show files that would be committed
Write-Host "`nThe following files will be added to the repository:" -ForegroundColor Cyan
git status

# Final confirmation
Write-Host "`nPLEASE VERIFY: Have you removed all passwords, API keys, and sensitive data?" -ForegroundColor Red
$confirmation = Read-Host "Type 'YES' to confirm and proceed with the commit"

if ($confirmation -ne "YES") {
    Write-Host "Operation cancelled. Please remove sensitive data before committing." -ForegroundColor Red
    exit 1
}

# Add all files
git add .

# Commit
git commit -m "Initial commit: Instagram Repost App"

# Set remote origin
Write-Host "`nSetting remote origin to: $repoUrl" -ForegroundColor Cyan
git remote add origin $repoUrl

# Push
Write-Host "`nPushing to GitHub repository..." -ForegroundColor Green
git push -u origin main

Write-Host "`nDone! Your code is now on GitHub at: $repoUrl" -ForegroundColor Green
