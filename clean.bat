@echo off
setlocal EnableDelayedExpansion

echo ====================================================================
echo =              "NewWorld Config Manager" Clean Script               =
echo ====================================================================
echo.

REM Navigate to the script's directory to ensure correct paths
cd /d "%~dp0"

echo Cleaning build artifacts...
echo.

if exist "dist" (
    echo Deleting 'dist' folder...
    rmdir /S /Q "dist"
    echo Done.
) else (
    echo 'dist' folder not found. Skipping.
)

if exist "build" (
    echo Deleting 'build' folder...
    rmdir /S /Q "build"
    echo Done.
) else (
    echo 'build' folder not found. Skipping.
)

if exist ".mypy_cache" (
    echo Deleting '.mypy_cache' folder...
    rmdir /S /Q ".mypy_cache"
    echo Done.
) else (
    echo '.mypy_cache' folder not found. Skipping.
)

if exist "newworld_config_manager.egg-info" (
    echo Deleting 'newworld_config_manager.egg-info' folder...
    rmdir /S /Q "newworld_config_manager.egg-info"
    echo Done.
) else (
    echo 'newworld_config_manager.egg-info' folder not found. Skipping.
)

if exist "__pycache__" (
    echo Deleting '__pycache__' folders...
    for /d /r . %%d in (__pycache__) do @if exist "%%d" (
        rmdir /S /Q "%%d"
    )
    echo Done.
) else (
    echo '__pycache__' folders not found. Skipping.
)

echo.
echo Cleaning archive files...
for %%f in (NewWorld_Config_Manager_v*.zip) do (
    echo Deleting %%f...
    del "%%f" >nul
)

echo.
echo ====================================================================
echo Clean complete!
echo ====================================================================
echo.
pause
endlocal