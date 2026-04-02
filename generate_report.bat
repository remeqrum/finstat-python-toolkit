@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo Priklady ICO: 31321828 (TESCO), 00010448 (Mincovna Kremnica)
set /p ICO="Zadajte ICO: "
if "%ICO%"=="" (echo Nezadali ste ICO. & pause & exit /b 1)
python -m src.report --ico %ICO%
if errorlevel 1 (echo [CHYBA] Report zlyhal. & pause & exit /b 1)
echo Hotovo - report v reports\output\
pause
