@echo off
cd /d "%~dp0"
set /p acc="Nhap ten account (mac dinh: acc1): "
if "%acc%"=="" set acc=acc1

echo Dang khoi chay trinh duyet dang nhap cho tai khoan: %acc% ...
".venv\Scripts\python.exe" add_account_manual.py %acc%
pause
