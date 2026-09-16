@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto run
where py >nul 2>nul
if errorlevel 1 (
  echo Install Python 3.12 or newer from https://www.python.org/downloads/ and try again.
  pause
  exit /b 1
)
py -3 -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
:run
if not exist ".env.local" if not defined OPENAI_API_KEY .venv\Scripts\python.exe setup_key.py
.venv\Scripts\python.exe launch.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Coursekin could not start. Read the message above for details.
pause
exit /b 1
