@echo off
REM QuestDB EUR/USD Import - Full Batch Run
REM Dit script start de import van ALLE 2004-2019 data naar QuestDB

echo ========================================
echo  QuestDB EUR/USD Import - Full Run
echo ========================================
echo Start: %date% %time%
echo.

cd /d "C:\projecten\forexdata"

set PYTHON="C:\Users\ronal\AppData\Roaming\kimi-desktop\daimon-share\daimon\runtime\python\.venv\Scripts\python.exe"
set LOG=import_log_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%.txt
set LOG=%LOG: =0%

echo Python: %PYTHON%
echo Log: %LOG%
echo.

%PYTHON% questdb_import.py --all > %LOG% 2>&1

echo.
echo ========================================
echo  Import afgerond
echo ========================================
echo Einde: %date% %time%
echo Log: %LOG%
pause
