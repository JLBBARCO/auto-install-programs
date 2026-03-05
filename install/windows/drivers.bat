@echo off
setlocal enabledelayedexpansion

echo Verificando Placa de Video...
for /f "tokens=2 delims==" %%i in ('wmic path win32_VideoController get name /value') do set GPU_NAME=%%i
echo GPU Detectada: %GPU_NAME%

echo.
echo %GPU_NAME% | findstr /I "NVIDIA" >nul
if %ERRORLEVEL% EQU 0 (
    echo Instalando Drivers NVIDIA...
    winget install Nvidia.GeForceExperience --accept-source-agreements --accept-package-agreements
    goto :end
)

echo %GPU_NAME% | findstr /I "AMD" >nul
if %ERRORLEVEL% EQU 0 (
    echo Instalando Drivers AMD Radeon...
    winget install AMD.RadeonSoftware --accept-source-agreements --accept-package-agreements
    goto :end
)

echo %GPU_NAME% | findstr /I "Intel" >nul
if %ERRORLEVEL% EQU 0 (
    echo Instalando Drivers Intel Graphics...
    winget install Intel.GraphicsDriver Assistant --accept-source-agreements --accept-package-agreements
    goto :end
)

:end
echo Processo finalizado. Verifique se o instalador abriu na barra de tarefas.
pause