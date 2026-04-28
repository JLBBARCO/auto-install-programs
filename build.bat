@echo off
echo Cleaning old builds...
rd /s /q dist build 2>nul
del /f /q "Auto Install Programs.spec" 2>nul

echo Installing required dependencies...
python -m pip install --upgrade pip
python -m pip install pyinstaller customtkinter psutil

echo Iniciando o Build com PyInstaller...
python -m PyInstaller --noconfirm --onedir --windowed ^
    --name "Auto Install Programs" ^
    --icon "src/assets/icon/icon.ico" ^
    --add-data "src;src" ^
    --add-data "install;install" ^
    --collect-all customtkinter ^
    --collect-all psutil ^
    --noupx ^
    "main.py"

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
echo O executavel esta em: dist/Auto Install Programs/
echo.
pause