@echo off
set CONFIG_COUNT=2
set ESPEAK=C:\Program_Files\eSpeak\command_line\espeak.exe
set PORT=7979
set SERVICE=%~dp0\example_service.bat
set START_CONFIG=1
set SUCCESS_MESSAGE=started successfully
call py3.bat "%~dp0\service_controller.py"