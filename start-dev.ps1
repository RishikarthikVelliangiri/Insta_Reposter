$scriptPath = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# Start the backend server (Node.js)
$backendPath = Join-Path -Path $scriptPath -ChildPath "backend"

Write-Host "Starting backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "cd `"$backendPath`"; npm start"

# Wait a bit for the backend to initialize
Start-Sleep -Seconds 3

# Start the frontend (React)
$frontendPath = Join-Path -Path $scriptPath -ChildPath "insta-repost-web"

Write-Host "Starting frontend React app..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "cd `"$frontendPath`"; npm start"

Write-Host "Both services started. Press ENTER to stop them when done." -ForegroundColor Yellow
$null = Read-Host
