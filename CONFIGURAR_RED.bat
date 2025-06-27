@echo off
echo Configurando red para Quiz Platform...
echo.

:: Crear carpeta de configuración si no existe
if not exist "data\config\" mkdir "data\config\"

:: Generar archivo de configuración de red
echo {> "data\config\network_config.json"
echo     "host": "0.0.0.0",>> "data\config\network_config.json"
echo     "port": 5000,>> "data\config\network_config.json"
echo     "auto_detect_ip": true,>> "data\config\network_config.json"
echo     "allowed_origins": [>> "data\config\network_config.json"
echo         "*">> "data\config\network_config.json"
echo     ]>> "data\config\network_config.json"
echo }>> "data\config\network_config.json"

echo Configuración de red creada con éxito.
echo.

:: Mostrar IP local al usuario
echo Dirección IP de este equipo:
ipconfig | findstr /i "IPv4"
echo.
echo Para conectarte desde otros dispositivos, usa la dirección IPv4 y el puerto 5000.
echo Ejemplo: http://192.168.1.100:5000
echo.

echo Presiona cualquier tecla para salir...
pause > nul
