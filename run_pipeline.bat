@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo [1/3] Cistenie datasetu...
python -m src.load
if errorlevel 1 goto :error
echo [2/3] Vypocet ukazovatelov...
python -m src.ratios
if errorlevel 1 goto :error
echo [3/3] Generovanie grafov...
python -m src.visualize
if errorlevel 1 goto :error
echo Hotovo.
pause
exit /b 0
:error
echo [CHYBA] Pipeline zlyhal.
pause
exit /b 1
