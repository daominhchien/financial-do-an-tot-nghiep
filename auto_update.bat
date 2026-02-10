@echo off
REM ============================================================
REM Auto Update Script - ETL + MySQL Import
REM Chạy tự động bằng Windows Task Scheduler
REM ============================================================

echo ============================================================
echo  AUTO UPDATE: Financial Data ETL + MySQL Import
echo  Time: %date% %time%
echo ============================================================

REM Chuyển đến thư mục ETL pipeline
cd /d "C:\Users\admin\Downloads\doantotnghiep\financial-etl-pipeline"

REM Kích hoạt virtual environment (nếu có)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Cài mysql-connector nếu chưa có
pip install mysql-connector-python -q

REM Chạy auto import (ETL + MySQL)
REM Thay đổi --symbols hoặc --sector tùy nhu cầu
python auto_import_mysql.py --symbols VNM FPT VIC HPG

REM Ghi log
echo [%date% %time%] Update completed >> update_log.txt

echo ============================================================
echo  DONE! Check update_log.txt for history
echo ============================================================
pause
