@echo off
echo Starting update Microsoft App Installer for correctly all future errors...
winget update Microsoft.AppInstaller --accept-source-agreements --accept-package-agreements >nul 2>&1
timeout /t 2 /nobreak >nul
set UPDATE_ERROR=%ERRORLEVEL%
echo Update process completed.
echo.

echo Starting installation applications...
echo.

call :install "Spacedesk Client" "Datronicsoft.SpacedeskDriver.Client"
call :install "Spacedesk Server" "Datronicsoft.SpacedeskDriver.Server"
call :install "AnyDesk" "AnyDesk.AnyDesk"

goto :eof

:install
set NAME=%~1
set ID=%~2
echo Installing %NAME%...
winget install %ID% --accept-source-agreements --accept-package-agreements >nul 2>&1
timeout /t 2 /nobreak >nul
set INSTALL_ERROR=%ERRORLEVEL%

if %INSTALL_ERROR% EQU 0 (
    echo [SUCCESS] %NAME% Installed or updated successfully!
) else if %INSTALL_ERROR% EQU -1978335189 (
    echo [INFO] %NAME% It's already installed and there are no updates available.
) else (
    echo [ERROR] Failed to install or update %NAME%. Code: %INSTALL_ERROR%
)
echo.
goto :eof