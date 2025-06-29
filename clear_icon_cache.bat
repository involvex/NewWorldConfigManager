@echo off
echo.
echo ====================================================================
echo =                WINDOWS ICON CACHE CLEANER                        =
echo ====================================================================
echo.
echo This script will attempt to clear the Windows icon cache, which
echo can resolve issues with incorrect icons on .exe files.
echo.
echo It needs to close and restart Windows Explorer to work.
echo PLEASE SAVE ALL YOUR WORK before continuing.
echo.
pause

echo.
echo Stopping Windows Explorer...
taskkill /f /im explorer.exe >nul

echo Deleting icon cache database...
del /a /q "%localappdata%\IconCache.db"
del /a /q "%localappdata%\Microsoft\Windows\Explorer\iconcache_*.db"

echo Restarting Windows Explorer...
start explorer.exe

echo.
echo Icon cache has been cleared. You may need to restart your computer
echo for all changes to take effect.
echo.
pause