@echo off
chcp 65001 >nul
title Dola AI Video Studio - One Click Launcher
cd /d "%~dp0\core"

echo ======================================================================
echo             DOLA AI VIDEO STUDIO - ONE CLICK RUNNER
echo ======================================================================
echo.

set PY_EXE=.venv\Scripts\python.exe
if not exist "%PY_EXE%" (
    set PY_EXE=py.exe
)

:: 1. Kiem tra va hien thi danh sach tai khoan
echo [*] Danh sach tai khoan hien co trong he thong:
if exist "accounts" (
    dir /b /ad accounts 2>nul
) else (
    echo [!] Chua co thu muc accounts.
)
echo.

:: 2. Tu dong quet va nap cookie neu co file cookies.txt
if exist "cookies.txt" (
    echo [*] Tu dong nap va cap nhat cookie tu cookies.txt ...
    "%PY_EXE%" import_cookies.py
    echo.
)

:: 3. Mo giao dien Studio Web tren trinh duyet
echo [*] Dang mo giao dien Studio Tao Video...
start "" "http://127.0.0.1:8000/web"

:: 4. Khoi dong Server chay tat ca tai khoan dong thoi
echo [*] Dang khoi dong Server API dieu phoi da tai khoan...
echo - Link Dashboard Web: http://127.0.0.1:8000/web
echo - Link API Gateway:   http://127.0.0.1:8000
echo.
echo ======================================================================
echo  Server dang chay va quan ly toan bo tai khoan.
echo  De tat server, ban chi can dong cua so nay.
echo ======================================================================
echo.

"%PY_EXE%" -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload

pause
