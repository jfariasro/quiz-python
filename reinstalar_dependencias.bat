@echo off
echo ================================================
echo LIMPIEZA Y REINSTALACION DE DEPENDENCIAS
echo ================================================
echo.

echo Desinstalando Pillow anterior...
py -m pip uninstall Pillow -y

echo.
echo Desinstalando matplotlib anterior...
py -m pip uninstall matplotlib -y

echo.
echo Limpiando cache de pip...
py -m pip cache purge

echo.
echo Actualizando pip...
py -m pip install --upgrade pip

echo.
echo Instalando dependencias con versiones actualizadas...
py -m pip install -r requirements.txt

echo.
echo ================================================
echo VERIFICANDO INSTALACION
echo ================================================

echo.
echo Verificando versiones instaladas:
py -c "import PIL; print(f'Pillow: {PIL.__version__}')"
py -c "import matplotlib; print(f'Matplotlib: {matplotlib.__version__}')"
py -c "import flask; print(f'Flask: {flask.__version__}')"

echo.
echo ================================================
echo PRUEBA RAPIDA DEL SISTEMA
echo ================================================

echo Ejecutando prueba rapida...
py test_system.py

echo.
echo ================================================
echo INSTALACION COMPLETADA
echo ================================================
echo.
echo Para iniciar el sistema:
echo 1. Doble clic en INICIAR_SISTEMA.bat
echo 2. Para administracion: ABRIR_ADMIN.bat
echo.
pause
