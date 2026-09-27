@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Dò tìm đường dẫn Conda
set CONDA_PATH=
if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" set CONDA_PATH=%USERPROFILE%\miniconda3\Scripts\activate.bat
if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" set CONDA_PATH=%USERPROFILE%\anaconda3\Scripts\activate.bat
if exist "C:\ProgramData\miniconda3\Scripts\activate.bat" set CONDA_PATH=C:\ProgramData\miniconda3\Scripts\activate.bat
if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" set CONDA_PATH=C:\ProgramData\anaconda3\Scripts\activate.bat

if "%CONDA_PATH%"=="" (
    echo [LỖI] Không tìm thấy Conda để khởi chạy ứng dụng!
    pause
    exit /b
)

:: Kích hoạt môi trường và chạy app.py
call "%CONDA_PATH%" yolo_env
python app.py

if errorlevel 1 (
    echo.
    echo Ứng dụng đã dừng lại do có lỗi xảy ra!
    pause
)
