@echo off
chcp 65001 >nul
title SMG Hub Server - Smart Green
echo ======================================================
echo    เปิดระบบ SMG Hub (Smart Green Hub)
echo ======================================================
echo.
echo กำลังเริ่มระบบที่: http://localhost:8080
start "" powershell -NoProfile -Command "Start-Sleep -Seconds 1; Start-Process 'http://localhost:8080'"
python "%~dp0serve.py"
pause
