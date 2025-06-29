@echo off
setlocal EnableDelayedExpansion

echo ====================================================================
echo =           "NewWorld Config Manager" Build Script                 =
echo ====================================================================
echo.

REM Navigate to the script's directory to ensure correct paths
cd /d "%~dp0"

REM ====================================================================
echo.
echo STEP 1: Installing Python dependencies
echo ====================================================================
if not exist "requirements.txt" (
    echo WARNING: "requirements.txt" not found. Skipping dependency installation.
    echo It is recommended to have a requirements.txt file for reproducible builds.
) else (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo.
        echo ERROR: Failed to install Python dependencies.
        echo Please check your Python environment and requirements.txt.
        pause
        exit /b 1
    )
    echo Dependencies installed successfully.
)

REM ====================================================================
echo.
echo STEP 2: Cleaning up previous builds
echo ====================================================================
if exist "dist" (
    echo Deleting 'dist' folder...
    rmdir /S /Q "dist"
)
if exist "build" (
    echo Deleting 'build' folder...
    rmdir /S /Q "build"
)
echo Cleanup complete.

REM ====================================================================
echo.
echo STEP 3: Building executable with PyInstaller
echo ====================================================================
set SPEC_FILE="NewWorld Config Manager.spec"

REM Check if the spec file exists before trying to build
if not exist %SPEC_FILE% (
    echo.
    echo ERROR: %SPEC_FILE% not found.
    echo Please ensure the spec file is present in the project root.
    pause
    exit /b 1
)

echo Running PyInstaller...
pyinstaller %SPEC_FILE%

REM Check if PyInstaller succeeded
if !errorlevel! neq 0 (
    echo.
    echo ERROR: PyInstaller failed to build the executable.
    echo Please check the output above for errors.
    echo The 'dist' folder will likely be empty or incomplete.
    pause
    exit /b 1
)
echo PyInstaller build successful.

REM ====================================================================
echo.
echo STEP 4: Copying additional files to distribution folder
echo ====================================================================

REM Determine the correct output directory inside 'dist'
set "OUTPUT_DIR="
if exist "dist\NewWorld Config Manager\" (
    set "OUTPUT_DIR=dist\NewWorld Config Manager"
) else if exist "dist\" (
    set "OUTPUT_DIR=dist"
)

if not defined OUTPUT_DIR (
    echo WARNING: Could not determine PyInstaller output directory. Skipping file copy.
) else (
    REM List of files to copy into the distribution folder
    set "FILES_TO_COPY=clear_icon_cache.bat LICENSE README.md"

    for %%F in (%FILES_TO_COPY%) do (
        if exist "%%F" (
            echo Copying %%F...
            copy "%%F" "%OUTPUT_DIR%\" >nul
        ) else (
            echo WARNING: "%%F" not found. Skipping copy.
        )
    )
)

REM ====================================================================
echo.
echo STEP 5: Creating distributable archive
echo ====================================================================
REM Read version from a file to include in the archive name.
set "APP_VERSION=0.0.0"
if exist "VERSION" (
    for /f "delims=" %%i in (VERSION) do set "APP_VERSION=%%i"
) else (
    echo WARNING: VERSION file not found. Using default version !APP_VERSION!.
)

set "ARCHIVE_NAME=NewWorld_Config_Manager_v%APP_VERSION%_dist.zip"
set "ARCHIVE_CREATED="

if not exist "dist\" (
    echo No 'dist' folder found to archive. Skipping.
) else (
    echo Creating zip archive of the 'dist' folder...
    if exist "%ARCHIVE_NAME%" (
        del "%ARCHIVE_NAME%" >nul
    )
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'dist\*' -DestinationPath '%ARCHIVE_NAME%'"
    if !errorlevel! neq 0 (
        echo ERROR: Failed to create zip archive. Check PowerShell permissions.
    ) else (
        echo Archive created successfully: %ARCHIVE_NAME%
        set "ARCHIVE_CREATED=true"
    )
)

echo.
echo ====================================================================
echo Build process complete!
echo The executable and other files can be found in the 'dist' folder.
if defined ARCHIVE_CREATED (
    echo A distributable archive can be found at %ARCHIVE_NAME%
)
echo ====================================================================
echo.
pause
endlocal