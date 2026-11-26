@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
  if errorlevel 1 python -m venv .venv
  if errorlevel 1 goto failed
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
.venv\Scripts\python.exe run_pipeline.py
if errorlevel 1 goto failed
.venv\Scripts\python.exe build_preview.py
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m streamlit run app.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Setup failed. Read README.md or open dashboard_preview.html for the included snapshot.
pause
exit /b 1
