@echo off
setlocal enabledelayedexpansion

REM ========================================
REM  QuestDB EUR/USD Import - FULL RUN
REM ========================================

echo [QuestDB Import Launcher]
echo.

cd /d "C:\projecten\forexdata"

set "PYTHON=C:\Users\ronal\AppData\Roaming\kimi-desktop\daimon-share\daimon\runtime\python\.venv\Scripts\python.exe"
set "LOGDIR=logs"
if not exist %LOGDIR% mkdir %LOGDIR%

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set "LOG=%LOGDIR%\import_%mydate%_%mytime%.txt"

echo Python: %PYTHON%
echo Log:    %LOG%
echo.
echo ========================================
echo  START IMPORT --all (2004-2019)
echo  Druk Ctrl+C om te annuleren
echo ========================================
echo.

"%PYTHON%" questdb_import.py --all > "%LOG%" 2>&1

echo.
echo ========================================
echo  IMPORT AFGEROND
echo ========================================
echo Log: %LOG%
echo.

REM Toon laatste 20 regels van log
type "%LOG%" | tail -20

pause
