@echo off
REM Kontrollera att Python är installerat
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python är inte installerat eller finns inte i PATH.
    echo Ladda ner och installera Python 3 från https://python.org
    pause
    exit /b 1
)

REM Aktivera venv om den finns, annars skapa den
IF EXIST venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) ELSE (
    echo Skapar virtuellt Python-miljö...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Installera beroenden
pip install --upgrade pip
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Fel vid installation av Python-paket.
    pause
    exit /b 1
)

REM Starta appen
python app.py
IF %ERRORLEVEL% NEQ 0 (
    echo Det gick inte att starta app.py. Kontrollera eventuella felmeddelanden ovan.
    pause
    exit /b 1
)

pause
