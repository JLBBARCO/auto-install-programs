@echo off
echo Limpando builds antigos...
rd /s /q dist build 2>nul
del /f /q "Auto Install Programs.spec" 2>nul

echo Instalando dependencias necessarias...
python -m pip install --upgrade pip
python -m pip install pyinstaller customtkinter

echo Iniciando o Build com PyInstaller...
python -m PyInstaller --noconfirm --onedir --windowed ^
    --name "Auto Install Programs" ^
    --icon "src/assets/icon/icon.ico" ^
    --add-data "src;src" ^
    --add-data "install;install" ^
    --collect-all customtkinter ^
    "main.py"

if errorlevel 1 (
    echo.
    echo ERRO: Build falhou!
    echo Verifique os erros acima.
    exit /b 1
)

echo.
echo ============================================
echo Build concluido com sucesso!
echo ============================================
echo.
echo O executavel esta em: dist/Auto Install Programs/
echo.
pause