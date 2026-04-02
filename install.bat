@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Instalujem baliky...
python --version >nul 2>&1
if errorlevel 1 (
    echo [CHYBA] Python nie je nainstalovany.
    pause
    exit /b 1
)
pip install -r requirements.txt
if errorlevel 1 (
    echo [CHYBA] Instalacia zlyhala.
    pause
    exit /b 1
)
echo Hotovo.
pause
