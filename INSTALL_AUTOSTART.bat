@echo off
title Cai dat Tu dong chay ngam cung Windows
cd /d "%~dp0"

echo ========================================================
echo   DANG CAI DAT BOT CHAY NGAM TU DONG CUNG WINDOWS
echo ========================================================

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_PATH=%~dp0RUN_BOT_BACKGROUND.vbs"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\TelegramBotTaskRunner.lnk"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%VBS_PATH%'; $s.Save()"

echo.
echo ✅ DA CAI DAT THANH CONG!
echo.
echo Tu nay moi khi ban mo may tinh len:
echo - Bot se TU DONG CHAY NGAM 100%% duoi nen Windows.
echo - Ban KHONG CAN BAM BAT KY NUT NAO CA.
echo.
echo Dang khoi chay Bot ngay bay gio...
start "" "%VBS_PATH%"
echo.
echo ========================================================
echo   HOAN THANH! DANG CHAY NGAM NAY.
echo ========================================================
pause
