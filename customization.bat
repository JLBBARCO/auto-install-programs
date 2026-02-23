@echo off
echo Starting update of all installed applications...
winget update --all >nul 2>&1
echo Update process completed.

echo Starting installation applications...

call :install "TranslucentTB" "9PF4KZ2VN4W9"
call :install "Rainmeter" "Rainmeter.Rainmeter"
call :install "Lively Wallpaper" "9NTM2QC6QWS7"

goto :eof

:install
set NAME=%~1
set ID=%~2
echo Installing %NAME%...
winget install %ID% --accept-source-agreements --accept-package-agreements >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCESSO] %NAME% Installed or updated successfully!
) else if %ERRORLEVEL% EQU -1978335189 (
    echo [INFO] %NAME% It's already installed and there are no updates available..
) else (
    echo [ERRO] Failed to install or update. %NAME%. Code: %ERRORLEVEL%
)
echo.
goto :eof