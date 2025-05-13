# Vercel Deployment Script for Instagram Repost Tool

# This script prepares your project for Vercel deployment
# and provides instructions on how to deploy

# Update frontend .env for production
$env:REACT_APP_API_URL = "https://insta-repost.vercel.app/api"
$env:REACT_APP_INSTAGRAM_APP_ID = "1842291649888953"
$env:REACT_APP_REDIRECT_URI = "https://insta-repost.vercel.app/auth/callback"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Instagram Repost Tool - Vercel Deployment   " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will help you deploy your Instagram Repost Tool to Vercel."
Write-Host ""

# Check if Vercel CLI is installed
$vercelInstalled = $null
try {
    $vercelInstalled = vercel --version
} catch {
    $vercelInstalled = $null
}

if (-not $vercelInstalled) {
    Write-Host "Vercel CLI is not installed. Installing now..." -ForegroundColor Yellow
    npm install -g vercel
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install Vercel CLI. Please install it manually:" -ForegroundColor Red
        Write-Host "npm install -g vercel" -ForegroundColor Red
        exit 1
    }
}

# Step 1: Build React app
Write-Host "Step 1: Building React frontend..." -ForegroundColor Green
Set-Location "C:\Users\rishi\Insta report system\insta-repost-web"
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build React app. Please check for errors." -ForegroundColor Red
    exit 1
}

# Step 2: Deployment Instructions
Write-Host ""
Write-Host "Step 2: Deploy to Vercel" -ForegroundColor Green
Write-Host ""
Write-Host "To deploy your application to Vercel, run the following commands:" -ForegroundColor Yellow
Write-Host ""
Write-Host "cd 'C:\Users\rishi\Insta report system'" -ForegroundColor White
Write-Host "vercel login" -ForegroundColor White
Write-Host "vercel --prod" -ForegroundColor White
Write-Host ""
Write-Host "When prompted during deployment:" -ForegroundColor Yellow
Write-Host "- Set the root directory to 'C:\Users\rishi\Insta report system'" -ForegroundColor White
Write-Host "- Confirm the build settings from vercel.json" -ForegroundColor White
Write-Host ""

# Step 3: Post-deployment instructions
Write-Host "Step 3: After Deployment" -ForegroundColor Green
Write-Host ""
Write-Host "Once deployed, update your Instagram App settings with:" -ForegroundColor Yellow
Write-Host "1. Valid OAuth Redirect URI: https://insta-repost.vercel.app/auth/callback" -ForegroundColor White
Write-Host "2. Deauthorize Callback URL: https://insta-repost.vercel.app/auth/deauthorize" -ForegroundColor White
Write-Host "3. Data Deletion Request URL: https://insta-repost.vercel.app/auth/delete-data" -ForegroundColor White
Write-Host ""
Write-Host "After deployment, your app will be available at:" -ForegroundColor Yellow
Write-Host "https://insta-repost.vercel.app" -ForegroundColor Green
Write-Host ""

Set-Location "C:\Users\rishi\Insta report system"
