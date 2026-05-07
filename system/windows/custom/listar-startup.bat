@echo off
REM Script para listar todos os programas de startup do Windows

echo ============================================
echo Lista de Programas de Startup do Windows
echo ============================================
echo.
echo HKEY_CURRENT_USER - Startup Programs do Usuario:
echo.
reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v * 2>nul | findstr /v "^HKEY" | for /f "tokens=1" %%A in ('findstr /v "^$"') do echo   %%A

echo.
echo HKEY_LOCAL_MACHINE - Startup Programs do Sistema (32-bit):
echo.
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v * 2>nul | findstr /v "^HKEY" | for /f "tokens=1" %%A in ('findstr /v "^$"') do echo   %%A

echo.
echo HKEY_LOCAL_MACHINE (WOW64) - Startup Programs do Sistema (64-bit):
echo.
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run" /v * 2>nul | findstr /v "^HKEY" | for /f "tokens=1" %%A in ('findstr /v "^$"') do echo   %%A

echo.
echo ============================================
echo.
echo Para adicionar um programa a white_list.txt, copie o NOME EXATO
echo ou uma PARTE do nome que seja unica.
echo.
echo Exemplo:
echo   Se o programa esta como "Microsoft.OneDrive" no registro,
echo   voce pode adicionar "onedrive" ou "microsoft.onedrive"
echo.
pause
