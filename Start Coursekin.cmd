@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  .venv\Scripts\python.exe bootstrap.py
  if errorlevel 1 goto failed
  exit /b 0
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 bootstrap.py
  if errorlevel 1 goto failed
  exit /b 0
)
python bootstrap.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Coursekin could not start. Read the message above for details.
pause
exit /b 1
