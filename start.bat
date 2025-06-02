@echo off
cd /d %~dp0
echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo Iniciando SPECTRON...
start http://localhost:5000
python run.py
pause
