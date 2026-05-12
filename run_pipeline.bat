@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo [1/4] Cistenie datasetu...
python -m src.load
if errorlevel 1 goto :error
echo [2/4] Vypocet ukazovatelov...
python -m src.ratios
if errorlevel 1 goto :error
echo [3/4] Odvetvove agregaty...
python -m src.benchmark
if errorlevel 1 goto :error
echo [4/4] Generovanie grafov...
python -m src.visualize
if errorlevel 1 goto :error
echo Hotovo.
pause
exit /b 0
:error
echo [CHYBA] Pipeline zlyhal.
pause
exit /b 1
