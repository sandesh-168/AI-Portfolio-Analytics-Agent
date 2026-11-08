@echo off
title AI Portfolio Analytics Dashboard
echo Launching Streamlit Portfolio Analytics Dashboard...
"%~dp0python_env\python.exe" -m streamlit run "%~dp0streamlit_app.py"
pause
