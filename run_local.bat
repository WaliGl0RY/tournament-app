@echo off
setlocal
cd /d "%~dp0"

set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY goto :nopy

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creating virtual environment .venv ...
  %PY% -m venv .venv || goto :err
)

echo [2/3] Installing requirements ...
".venv\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check -r requirements.txt || goto :err

echo.
echo [3/3] Starting server ... open http://127.0.0.1:5000
echo     (press CTRL+C in this window to stop)
echo.
start "" http://127.0.0.1:5000
".venv\Scripts\python.exe" app.py
goto :end

:nopy
echo Python 3 was not found on this PC.
echo Install it from https://www.python.org/downloads/ (tick "Add python.exe to PATH").
pause
exit /b 1

:err
echo.
echo Something went wrong - see the message above.
pause
exit /b 1

:end
pause
