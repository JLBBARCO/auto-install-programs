@echo off

echo Installing and configure Microsoft Office...
cd /
cd office
setup.exe/configure settings.xml
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install Microsoft Office. Please check the error message above.
) ELSE (
    echo Microsoft Office installed successfully.
)