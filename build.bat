@echo off
echo Cleaning old builds...
rd /s /q dist build 2>nul
del /f /q "Programs Manager.spec" 2>nul

echo Installing required dependencies...
python -m pip install --upgrade pip
python -m pip install pyinstaller customtkinter psutil

echo Iniciando o Build com PyInstaller...

echo Adding install directory to bundle...
python -m PyInstaller --noconfirm --onedir --windowed ^
    --name "Programs Manager" ^
    --icon "src/assets/icon/icon.ico" ^
    --add-data "program/lib;lib" ^
    --collect-all customtkinter ^
    --collect-all psutil ^
    --noupx ^
    "program/main.py"

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the errors above.
    exit /b 1
)

echo.
echo Build completed successfully!
echo %%%%
echo.
echo O executavel esta em: dist/Programs Manager/
echo.
pause