@echo off
echo Starting update of all installed applications...
winget update --all >nul 2>&1
echo Update process completed.
echo.

echo Starting installation applications...
echo.

call :install "Xbox App" "Microsoft.XboxApp"
call :install "Steam" "Valve.Steam"
call :install "Discord" "XPDC2RH70K22MN"
call :install "Google Play Games" "Google.PlayGames"
call :install "Radmin VPN" "Famatech.RadminVPN"
call :install "CurseForge" "Overwolf.CurseForge"
call :install "Epic Games Launcher" "EpicGames.EpicGamesLauncher"

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