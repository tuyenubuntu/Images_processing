@echo off
chcp 65001 >nul
echo =======================================================
echo          BẮT ĐẦU CÀI ĐẶT HỆ THỐNG VISION SYSTEM
echo =======================================================

:: 1. Dò tìm đường dẫn Conda
set CONDA_PATH=
if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" set CONDA_PATH=%USERPROFILE%\miniconda3\Scripts\activate.bat
if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" set CONDA_PATH=%USERPROFILE%\anaconda3\Scripts\activate.bat
if exist "C:\ProgramData\miniconda3\Scripts\activate.bat" set CONDA_PATH=C:\ProgramData\miniconda3\Scripts\activate.bat
if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" set CONDA_PATH=C:\ProgramData\anaconda3\Scripts\activate.bat

if "%CONDA_PATH%"=="" (
    echo [LỖI] Không tìm thấy Conda trên máy! Vui lòng cài đặt Miniconda hoặc Anaconda trước.
    pause
    exit /b
)

echo [*] Đang nạp Conda từ: %CONDA_PATH%
call "%CONDA_PATH%" base

:: 2. Tạo môi trường yolo_env nếu chưa tồn tại
set ENV_NAME=yolo_env
echo [*] Đang kiểm tra môi trường Conda '%ENV_NAME%'...
conda env list | findstr /C:"%ENV_NAME%" >nul
if errorlevel 1 (
    echo [*] Môi trường chưa có, đang tạo mới với Python 3.10...
    call conda create -y -n %ENV_NAME% python=3.10
) else (
    echo [*] Môi trường '%ENV_NAME%' đã tồn tại.
)

:: 3. Kích hoạt môi trường yolo_env
call conda activate %ENV_NAME%

:: 4. Cài đặt PyTorch hỗ trợ GPU CUDA 12.1 và thư viện từ requirements.txt
echo [*] Đang cài đặt PyTorch với hỗ trợ GPU CUDA...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

echo [*] Đang cài đặt các thư viện từ requirements.txt...
pip install -r requirements.txt

:: 5. Tự động tạo file shortcut ra màn hình Desktop
echo [*] Đang tạo Shortcut trên Desktop...
set TARGET_BAT=%~dp0run_app.bat
set SHORTCUT_PATH=%USERPROFILE%\Desktop\Vision System.lnk
set WORKING_DIR=%~dp0

powershell "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%TARGET_BAT%'; $s.WorkingDirectory = '%WORKING_DIR%'; $s.Save()"

echo =======================================================
echo          CÀI ĐẶT THÀNH CÔNG!
echo Đã tạo shortcut "Vision System" trên Desktop.
echo =======================================================
pause
