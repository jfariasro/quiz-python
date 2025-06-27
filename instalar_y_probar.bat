@echo off
echo ====================================================
echo    SISTEMA DE QUIZZES - INSTALACION Y PRUEBAS
echo ====================================================

echo.
echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo.
    echo Por favor instala Python desde: https://python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion
    echo.
    pause
    exit /b 1
)

echo Python encontrado.
python --version

echo.
echo Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo ====================================================
echo           EJECUTANDO PRUEBAS DEL SISTEMA
echo ====================================================
echo.

python test_system.py
if %errorlevel% neq 0 (
    echo.
    echo ====================================================
    echo   ALGUNAS PRUEBAS FALLARON - REVISA LOS ERRORES
    echo ====================================================
    pause
    exit /b 1
)

echo.
echo ====================================================
echo      TODAS LAS PRUEBAS PASARON EXITOSAMENTE!
echo ====================================================
echo.
echo El sistema esta listo para usar.
echo.
echo Comandos disponibles:
echo   python main.py          - Ejecutar aplicacion principal
echo   python test_system.py   - Ejecutar pruebas nuevamente
echo.
echo Para la interfaz de administracion, ejecuta:
echo   python -m admin.main_window
echo.
pause
