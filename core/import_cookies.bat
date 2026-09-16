@echo off
cd /d "%~dp0"
echo Dang import cookies tu file cookies.txt ...
".venv\Scripts\python.exe" import_cookies.py
pause
