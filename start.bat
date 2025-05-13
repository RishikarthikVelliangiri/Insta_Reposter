@echo off
echo Starting Instagram Repost Tool...
echo.

echo Starting backend server...
start powershell -NoExit -Command "cd 'C:\Users\rishi\Insta report system\backend'; npm run dev"

echo Starting frontend server...
timeout /t 3 > nul
start powershell -NoExit -Command "cd 'C:\Users\rishi\Insta report system\insta-repost-web'; npm start"

echo.
echo Servers are starting up! The application will open in your browser shortly.
echo If it doesn't open automatically, go to http://localhost:3000
