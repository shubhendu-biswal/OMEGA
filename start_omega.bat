@echo off
echo Starting OMEGA Intelligent Assistant System...

echo [1/3] Launching Flask ML Service on port 5000...
start "OMEGA ML Service" cmd /k "cd /d %~dp0ml_service && python app.py"

echo [2/3] Launching Spring Boot Backend on port 9090...
start "OMEGA Spring Boot Backend" cmd /k "cd /d %~dp0backend && mvn spring-boot:run"

echo [3/3] Launching Vite Frontend on port 3000...
start "OMEGA React Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo All services launched! Check individual console windows for logs.
pause


