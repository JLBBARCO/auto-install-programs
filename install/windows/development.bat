@echo off
echo Starting update Microsoft App Installer for correctly all future errors...
winget update Microsoft.AppInstaller --accept-source-agreements --accept-package-agreements >nul 2>&1
timeout /t 2 /nobreak >nul
set UPDATE_ERROR=%ERRORLEVEL%
echo Update process completed.
echo.

echo Starting installation applications...
echo.

call :install "Arduino IDE" "ArduinoSA.IDE.stable"
call :install "Blender" "BlenderFoundation.Blender"
call :install "Docker Desktop" "Docker.DockerDesktop"
call :install "Figma" "Figma.Figma"
call :install "Gimp" "GIMP.GIMP.3"
call :install "Git" "Git.Git"
call :install "GitHub Desktop" "GitHub.GitHubDesktop"
call :install "Java Runtime Environment" "Oracle.JavaRuntimeEnvironment"
call :install "Microsoft Teams" "Microsoft.Teams"
call :install "MySQL Workbench" "Oracle.MySQLWorkbench"
call :install "Node.js" "OpenJS.NodeJS"
call :install "Visual Studio Code" "Microsoft.VisualStudioCode"
call :install "Python 3.12" "Python.Python.3.12"
call :install "Raspberry Pi" "RaspberryPi.RaspberryPiImager"
call :install "Rufus" "Rufus.Rufus"
call :install "Ventoy" "Ventoy.Ventoy"
call :install "VirtualBox" "Oracle.VirtualBox"
call :install "XAMPP" "ApacheFriends.Xampp.8.1"
call :install "Winget Create" "wingetcreate"

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