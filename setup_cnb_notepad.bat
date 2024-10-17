@echo off
:check_python_version
python --version 2>NUL
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3 (3.11.8 recommended^).
    exit /b 1
)
for /f "tokens=2 delims=." %%i in ('python -c "import sys; print(sys.version.split()[0])"') do set PYTHON_MINOR=%%i
if %PYTHON_MINOR% LSS 11 (
    echo Error: Python 3.11 or higher is required.
    echo Please install Python 3 (3.11.8 recommended^).
    exit /b 1
)
call :check_python_version
for /f "tokens=1 delims=." %%i in ('hostname') do set HOSTNAME=%%i
set VENV_PATH=.venv-%HOSTNAME%
set FORCE=false
if "%1"=="-f" set FORCE=true
if exist %VENV_PATH% (
    if "%FORCE%"=="false" (
        set /p REBUILD=Virtual environment already exists. Rebuild? (y/n): 
        if /i "%REBUILD%"=="y" (
            rmdir /s /q %VENV_PATH%
            python -m venv %VENV_PATH%
            call %VENV_PATH%\Scripts\activate.bat
            pip install -r requirements.txt
            call deactivate
        ) else (
            echo Skipping virtual environment setup.
        )
    ) else (
        rmdir /s /q %VENV_PATH%
        python -m venv %VENV_PATH%
        call %VENV_PATH%\Scripts\activate.bat
        pip install -r requirements.txt
        call deactivate
    )
) else (
    python -m venv %VENV_PATH%
    call %VENV_PATH%\Scripts\activate.bat
    pip install -r requirements.txt
    call deactivate
)
for /f "delims=" %%i in ('python -c "import json; print(json.load(open('cnb_notepad.rsc'))['launcher_bat'].replace('{HOSTNAME}', '%HOSTNAME%'))"') do set LAUNCHER_BAT=%%i
if exist CNB_Notepad.bat (
    if "%FORCE%"=="false" (
        set /p REBUILD_LAUNCHER=Launcher script already exists. Rebuild? (y/n): 
        if /i "%REBUILD_LAUNCHER%"=="y" (
            echo %LAUNCHER_BAT% > CNB_Notepad.bat
        ) else (
            echo Skipping launcher script creation.
        )
    ) else (
        echo %LAUNCHER_BAT% > CNB_Notepad.bat
    )
) else (
    echo %LAUNCHER_BAT% > CNB_Notepad.bat
)
echo Setup complete. To launch the app, run: CNB_Notepad.bat
