@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ======================================================================
echo           CÔNG CỤ ĐĂNG NHẬP / MỞ LẠI TÀI KHOẢN DOLA
echo ======================================================================
echo.
echo Danh sách tài khoản hiện có trong thư mục accounts:
dir /b /ad accounts 2>nul
echo.
set /p ACC_NAME="Nhập tên tài khoản bạn muốn mở đăng nhập (VD: acc1 hoặc acc5): "

if "%ACC_NAME%"=="" (
    set ACC_NAME=acc1
)

echo.
echo [*] Đang mở trình duyệt cho tài khoản [%ACC_NAME%]...
echo [*] Bạn chỉ cần đăng nhập Google/Dola trong cửa sổ hiện lên, tool sẽ tự lưu vĩnh viễn.
echo.

.\.venv\Scripts\python.exe add_account_manual.py %ACC_NAME%

echo.
pause
