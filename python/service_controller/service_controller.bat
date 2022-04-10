@echo off
set CONFIG_COUNT=3
set START_CONFIG=2
set RETRIES=1
set ESPEAK=
rem C:\Program_Files\eSpeak\command_line\espeak.exe
set PORT=7977
set SERVICE=%~dp0\example_service.bat
set SERVICE_TIMEOUT=3
rem set START_CONFIG=0
set SUCCESS_MESSAGE=started successfully
call py3.bat "%~dp0\service_controller.py"