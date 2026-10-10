@echo off
title Push code lên GitHub cho Render 24/7
cd /d "%~dp0"
echo ========================================================
echo   DANG CAP NHAT CODE LEN GITHUB DE BOT CHAY CLOUD 24/7
echo ========================================================
git add .
git commit -m "Fix Render cloud auto deployment 24/7"
git push origin main
echo.
echo ========================================================
echo   DA PUSH CODE THANH CONG! RENDER DANG CHAY AUTOMATIC 24/7.
echo ========================================================
pause
