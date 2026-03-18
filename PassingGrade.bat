@echo off
IF EXIST "%~dp0dist\PassingGrade.exe" (
    start "" "%~dp0dist\PassingGrade.exe"
) ELSE (
    where python >nul 2>&1
    IF %ERRORLEVEL% EQU 0 (
        python "%~dp0main.py"
    ) ELSE (
        echo PassingGrade could not start.
        echo.
        echo To run from source: install Python 3.11+ from https://www.python.org
        echo   then run:  pip install -r requirements.txt
        echo.
        echo To use the standalone app: run build\build_windows.ps1 first
        echo   (requires Python and pip to be installed)
        pause
    )
)
