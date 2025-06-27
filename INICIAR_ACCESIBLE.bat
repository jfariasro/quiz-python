@echo off
echo Iniciando Quiz Platform en modo accesible desde red...
echo.

:: Ejecutar el servidor
cd "%~dp0"
py -m admin.main_window

echo.
pause
