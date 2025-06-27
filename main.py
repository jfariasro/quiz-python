"""
Plataforma de Quizzes Tipo Kahoot!
Punto de entrada principal de la aplicación.

Este archivo inicializa tanto la aplicación de administración (Tkinter)
como el servidor web (Flask + SocketIO) en hilos separados.
"""

import os
import sys
import threading
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_project_structure():
    """Crear la estructura de carpetas necesaria para el proyecto."""
    base_dir = Path(__file__).parent
    
    directories = [
        'data',
        'data/quizzes',
        'data/sessions', 
        'data/history',
        'data/config',
        'admin',
        'web',
        'web/templates',
        'static',
        'static/css',
        'static/js',
        'static/images',
        'utils',
        'logs'
    ]
    
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Crear archivos __init__.py en packages Python
        if directory in ['admin', 'web', 'utils']:
            init_file = dir_path / '__init__.py'
            if not init_file.exists():
                init_file.write_text('')
    
    logger.info("Estructura de proyecto creada/verificada")

def create_config_files():
    """Crear archivos de configuración básicos si no existen."""
    base_dir = Path(__file__).parent
    config_dir = base_dir / 'data' / 'config'
    
    # Configuración de la aplicación
    app_config = {
        "app_name": "Plataforma de Quizzes Kahoot!",
        "version": "1.0.0",
        "debug": True,
        "max_participants": 20,
        "default_question_time": 30,
        "default_points": 100
    }
    
    # Configuración de red
    network_config = {
        "host": "0.0.0.0",
        "port": 5000,
        "auto_detect_ip": True,
        "allowed_origins": ["*"]
    }
    
    # Escribir configuraciones si no existen
    import json
    
    app_config_file = config_dir / 'app_config.json'
    if not app_config_file.exists():
        with open(app_config_file, 'w', encoding='utf-8') as f:
            json.dump(app_config, f, indent=4, ensure_ascii=False)
    
    network_config_file = config_dir / 'network_config.json'
    if not network_config_file.exists():
        with open(network_config_file, 'w', encoding='utf-8') as f:
            json.dump(network_config, f, indent=4, ensure_ascii=False)
    
    logger.info("Archivos de configuración creados/verificados")

def check_dependencies():
    """Verificar que las dependencias necesarias estén instaladas."""
    required_packages = [
        'flask',
        'flask_socketio',
        'customtkinter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Paquetes faltantes: {', '.join(missing_packages)}")
        logger.error("Ejecuta: pip install -r requirements.txt")
        return False
    
    logger.info("Todas las dependencias están instaladas")
    return True

def start_web_server():
    """Iniciar el servidor web en un hilo separado."""
    try:
        # Importar aquí para evitar errores de importación circular
        from web.app import create_app
        
        app = create_app()
        logger.info("Iniciando servidor web en puerto 5000...")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        
    except ImportError as e:
        logger.error(f"Error al importar módulo web: {e}")
        logger.error("Asegúrate de que el módulo web esté implementado")
    except Exception as e:
        logger.error(f"Error al iniciar servidor web: {e}")

def start_admin_app():
    """Iniciar la aplicación de administración Tkinter."""
    try:
        # Importar aquí para evitar errores de importación circular
        from admin.main_window import QuizAdminApp
        
        logger.info("Iniciando aplicación de administración...")
        app = QuizAdminApp()
        app.run()
        
    except ImportError as e:
        logger.error(f"Error al importar módulo admin: {e}")
        logger.error("Asegúrate de que el módulo admin esté implementado")
    except Exception as e:
        logger.error(f"Error al iniciar aplicación de administración: {e}")

def main():
    """Función principal que coordina el inicio de toda la aplicación."""
    logger.info("=== INICIANDO PLATAFORMA DE QUIZZES KAHOOT! ===")
    
    try:
        # 1. Verificar dependencias
        if not check_dependencies():
            print("\n❌ Error: Dependencias faltantes")
            print("Ejecuta: pip install -r requirements.txt")
            sys.exit(1)
        
        # 2. Configurar estructura del proyecto
        setup_project_structure()
        
        # 3. Crear archivos de configuración
        create_config_files()
        
        # 4. Iniciar servidor web en hilo separado
        web_thread = threading.Thread(
            target=start_web_server,
            daemon=True,  # Se cierra cuando termina el programa principal
            name="WebServerThread"
        )
        web_thread.start()
        
        # Dar tiempo al servidor para iniciar
        logger.info("Esperando a que inicie el servidor web...")
        time.sleep(3)
        
        # 5. Iniciar aplicación de administración en hilo principal
        # (Tkinter debe ejecutarse en el hilo principal)
        start_admin_app()
        
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("=== CERRANDO PLATAFORMA DE QUIZZES ===")

if __name__ == '__main__':
    main()
