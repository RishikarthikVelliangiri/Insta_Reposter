# PowerShell script to start Instagram Repost Tool
Write-Host "Starting Instagram Repost Tool..." -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting backend server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\rishi\Insta report system\backend'; npm run dev"

Write-Host "Starting frontend server..." -ForegroundColor Green
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\rishi\Insta report system\insta-repost-web'; npm start"

Write-Host ""
Write-Host "Servers are starting up! The application will open in your browser shortly." -ForegroundColor Magenta
Write-Host "If it doesn't open automatically, go to http://localhost:3000" -ForegroundColor Magenta
