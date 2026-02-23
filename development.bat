@echo off
echo Starting update of all installed applications...
winget update --all >nul 2>&1
echo Update process completed.
echo.

echo Starting installation applications...
echo.

call :install "Visual Studio Code" "XP9KHM4BK9FZ7Q"
call :install "Visual Studio 2022 Community Edition" "Microsoft.VisualStudio.2022.Community"
call :install "Arduino IDE" "9NBLGGH4RSD8"
call :install "Microsoft Teams" "XP8BT8DW290MPQ"
call :install "Gimp" "9PNSJCLXDZ0V"
call :install "Git" "Git.Git"
call :install "GitHub Desktop" "GitHub.GitHubDesktop"
call :install "Python 3.12" "9NCVDN91XZQP"
call :install "Java Runtime Environment" "Oracle.JavaRuntimeEnvironment"
call :install "MySQL Workbench" "Oracle.MySQLWorkbench"
call :install "Node.js" "OpenJS.NodeJS"
call :install "XAMPP" "ApacheFriends.Xampp.8.1"
call :install "Docker Desktop" "XP8CBJ40XLBWKX"
call :install "VirtualBox" "Oracle.VirtualBox"

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