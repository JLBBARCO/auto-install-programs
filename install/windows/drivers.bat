@echo off
echo Starting update of all installed applications...
winget update --all --accept-source-agreements --accept-package-agreements >nul 2>&1
timeout /t 2 /nobreak >nul
set UPDATE_ERROR=%ERRORLEVEL%
echo Update process completed.
echo.

setlocal enabledelayedexpansion

echo Checking the Video Card...
for /f "tokens=2 delims==" %%i in ('wmic path win32_VideoController get name /value') do set GPU_NAME=%%i
echo GPU Detected: %GPU_NAME%

echo.
echo %GPU_NAME% | findstr /I "NVIDIA" >nul
if %ERRORLEVEL% EQU 0 (
    echo Installing NVIDIA Drivers...
    winget install Nvidia.GeForceExperience --accept-source-agreements --accept-package-agreements
    timeout /t 2 /nobreak >nul
    goto :end
)

echo %GPU_NAME% | findstr /I "AMD" >nul
if %ERRORLEVEL% EQU 0 (
    echo Installing AMD Radeon Drivers...
    winget install AMD.RadeonSoftware --accept-source-agreements --accept-package-agreements
    timeout /t 2 /nobreak >nul
    goto :end
)

echo %GPU_NAME% | findstr /I "Intel" >nul
if %ERRORLEVEL% EQU 0 (
    echo Installing Intel Graphics Drivers...
    winget install Intel.GraphicsDriver Assistant --accept-source-agreements --accept-package-agreements
    timeout /t 2 /nobreak >nul
    goto :end
)

:end
echo Process completed. Check if the installer has opened in the taskbar.
pause