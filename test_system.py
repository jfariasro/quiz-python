#!/usr/bin/env python3
"""
Script de prueba para verificar el FileManager y la estructura de archivos.
Ejecuta pruebas básicas de todas las funcionalidades del sistema.
"""

import sys
import os
from pathlib import Path
import json
import logging

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from utils.file_manager import FileManager
    from utils.network_utils import NetworkUtils
    from utils.quiz_logic import QuizManager
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrate de que todos los archivos estén en su lugar.")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_file_manager():
    """Probar las funcionalidades del FileManager."""
    print("\n=== PRUEBAS DEL FILE MANAGER ===")
    
    try:
        # Inicializar FileManager
        fm = FileManager()
        print("✓ FileManager inicializado correctamente")
        
        # Verificar directorios
        print(f"✓ Directorio base: {fm.base_path}")
        print(f"✓ Directorio de datos: {fm.data_path}")
        print(f"✓ Directorio de quizzes: {fm.quizzes_path}")
        print(f"✓ Directorio de sesiones: {fm.sessions_path}")
        print(f"✓ Directorio de historial: {fm.history_path}")
        print(f"✓ Directorio de configuración: {fm.config_path}")
        
        # Verificar que los directorios existen
        directories = [fm.data_path, fm.quizzes_path, fm.sessions_path, 
                      fm.history_path, fm.config_path]
        
        for directory in directories:
            if directory.exists():
                print(f"✓ Directorio existe: {directory.name}")
            else:
                print(f"✗ Directorio no existe: {directory.name}")
                return False
        
        # Probar creación de quiz de prueba
        print("\n--- Probando gestión de quizzes ---")
        
        quiz_test = {
            "title": "Quiz de Prueba",
            "description": "Quiz para verificar funcionalidad",
            "category": "Test",
            "difficulty": "Fácil",
            "questions": [
                {
                    "question": "¿Cuál es la capital de España?",
                    "options": ["Madrid", "Barcelona", "Sevilla", "Valencia"],
                    "correct_answer": 0,
                    "explanation": "Madrid es la capital de España"
                },
                {
                    "question": "¿Cuánto es 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "correct_answer": 1,
                    "explanation": "2 + 2 = 4"
                }
            ]
        }
        
        # Guardar quiz
        quiz_id = fm.save_quiz(quiz_test)
        print(f"✓ Quiz guardado con ID: {quiz_id}")
        
        # Cargar quiz
        loaded_quiz = fm.load_quiz(quiz_id)
        if loaded_quiz:
            print("✓ Quiz cargado correctamente")
            print(f"  Título: {loaded_quiz['title']}")
            print(f"  Preguntas: {len(loaded_quiz['questions'])}")
        else:
            print("✗ Error al cargar quiz")
            return False
        
        # Listar quizzes
        quizzes = fm.list_quizzes()
        print(f"✓ Encontrados {len(quizzes)} quizzes")
        
        # Duplicar quiz
        new_quiz_id = fm.duplicate_quiz(quiz_id, "Quiz de Prueba - Copia")
        if new_quiz_id:
            print(f"✓ Quiz duplicado con ID: {new_quiz_id}")
        else:
            print("✗ Error al duplicar quiz")
        
        # Probar sesiones
        print("\n--- Probando gestión de sesiones ---")
        
        session_test = {
            "quiz_id": quiz_id,
            "name": "Sesión de Prueba",
            "status": "created",
            "participants": [],
            "settings": {
                "time_per_question": 30,
                "allow_late_join": False
            }
        }
        
        session_id = fm.save_session(session_test)
        print(f"✓ Sesión guardada con ID: {session_id}")
        
        loaded_session = fm.load_session(session_id)
        if loaded_session:
            print("✓ Sesión cargada correctamente")
        else:
            print("✗ Error al cargar sesión")
        
        # Probar configuración
        print("\n--- Probando gestión de configuración ---")
        
        config_test = {
            "server_host": "127.0.0.1",
            "server_port": 5000,
            "debug_mode": True,
            "max_participants": 50,
            "default_time_per_question": 30
        }
        
        fm.save_config("server", config_test)
        print("✓ Configuración guardada")
        
        loaded_config = fm.load_config("server")
        if loaded_config and loaded_config.get("server_port") == 5000:
            print("✓ Configuración cargada correctamente")
        else:
            print("✗ Error al cargar configuración")
        
        # Probar historial
        print("\n--- Probando gestión de historial ---")
        
        history_test = {
            "event_type": "quiz_completed",
            "session_id": session_id,
            "quiz_id": quiz_id,
            "participants_count": 5,
            "duration": 300,
            "average_score": 85.5
        }
        
        history_id = fm.save_history_record(history_test)
        print(f"✓ Registro de historial guardado con ID: {history_id}")
        
        history_records = fm.load_history_records(10)
        print(f"✓ Cargados {len(history_records)} registros de historial")
        
        print("\n✓ Todas las pruebas del FileManager completadas exitosamente")
        return True
        
    except Exception as e:
        print(f"✗ Error en pruebas del FileManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_network_utils():
    """Probar las utilidades de red."""
    print("\n=== PRUEBAS DE NETWORK UTILS ===")
    
    try:
        net_utils = NetworkUtils()
        print("✓ NetworkUtils inicializado correctamente")
        
        # Obtener IP local
        local_ip = net_utils.get_local_ip()
        print(f"✓ IP local: {local_ip}")
        
        # Verificar puerto disponible
        port = net_utils.find_available_port(5000)
        print(f"✓ Puerto disponible encontrado: {port}")
        
        # Generar código de sesión
        session_code = net_utils.generate_session_code()
        print(f"✓ Código de sesión generado: {session_code}")
        
        print("✓ Todas las pruebas de NetworkUtils completadas exitosamente")
        return True
        
    except Exception as e:
        print(f"✗ Error en pruebas de NetworkUtils: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quiz_manager():
    """Probar el QuizManager."""
    print("\n=== PRUEBAS DEL QUIZ MANAGER ===")
    
    try:
        quiz_manager = QuizManager()
        print("✓ QuizManager inicializado correctamente")
        
        # Crear una sesión de prueba
        session = quiz_manager.create_session("test-quiz-id", "Sesión de Prueba")
        if session:
            print(f"✓ Sesión creada: {session['id']}")
        else:
            print("✗ Error al crear sesión")
            return False
        
        # Agregar participante
        participant = quiz_manager.add_participant(session['id'], "Jugador de Prueba")
        if participant:
            print(f"✓ Participante agregado: {participant['name']}")
        else:
            print("✗ Error al agregar participante")
        
        # Obtener sesión
        retrieved_session = quiz_manager.get_session(session['id'])
        if retrieved_session:
            print("✓ Sesión recuperada correctamente")
            print(f"  Participantes: {len(retrieved_session['participants'])}")
        else:
            print("✗ Error al recuperar sesión")
        
        print("✓ Todas las pruebas del QuizManager completadas exitosamente")
        return True
        
    except Exception as e:
        print(f"✗ Error en pruebas del QuizManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Verificar la estructura de archivos del proyecto."""
    print("\n=== VERIFICACIÓN DE ESTRUCTURA DE ARCHIVOS ===")
    
    expected_structure = {
        "main.py": "archivo",
        "requirements.txt": "archivo",
        "utils/": "directorio",
        "utils/__init__.py": "archivo",
        "utils/file_manager.py": "archivo",
        "utils/network_utils.py": "archivo",
        "utils/quiz_logic.py": "archivo",
        "web/": "directorio",
        "web/__init__.py": "archivo", 
        "web/app.py": "archivo",
        "web/templates/": "directorio",
        "web/templates/base.html": "archivo",
        "web/templates/index.html": "archivo",
        "web/templates/lobby.html": "archivo",
        "web/templates/quiz.html": "archivo",
        "web/templates/error.html": "archivo",
        "web/templates/no_quiz.html": "archivo",
        "admin/": "directorio",
        "admin/__init__.py": "archivo",
        "admin/main_window.py": "archivo",
        "static/": "directorio",
        "static/css/": "directorio",
        "static/js/": "directorio",
        "static/images/": "directorio",
        "data/": "directorio",
        "docs/": "directorio",
        "instrucciones/": "directorio"
    }
    
    missing_files = []
    project_root = Path(__file__).parent
    
    for path, expected_type in expected_structure.items():
        full_path = project_root / path
        
        if expected_type == "archivo":
            if full_path.is_file():
                print(f"✓ {path}")
            else:
                print(f"✗ {path} (archivo faltante)")
                missing_files.append(path)
        elif expected_type == "directorio":
            if full_path.is_dir():
                print(f"✓ {path}")
            else:
                print(f"✗ {path} (directorio faltante)")
                missing_files.append(path)
    
    if missing_files:
        print(f"\n⚠️  Se encontraron {len(missing_files)} archivos/directorios faltantes:")
        for missing in missing_files:
            print(f"   - {missing}")
        return False
    else:
        print("\n✓ Estructura de archivos completa y correcta")
        return True

def test_json_files():
    """Verificar los archivos JSON de ejemplo."""
    print("\n=== VERIFICACIÓN DE ARCHIVOS JSON ===")
    
    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    
    # Verificar quizzes de ejemplo
    quizzes_dir = data_dir / "quizzes"
    if quizzes_dir.exists():
        quiz_files = list(quizzes_dir.glob("*.json"))
        print(f"✓ Encontrados {len(quiz_files)} archivos de quiz")
        
        for quiz_file in quiz_files:
            try:
                with open(quiz_file, 'r', encoding='utf-8') as f:
                    quiz_data = json.load(f)
                
                # Verificar estructura básica
                required_fields = ['id', 'title', 'questions']
                for field in required_fields:
                    if field not in quiz_data:
                        print(f"✗ {quiz_file.name}: falta campo '{field}'")
                        return False
                
                print(f"✓ {quiz_file.name}: estructura válida ({len(quiz_data['questions'])} preguntas)")
                
            except json.JSONDecodeError as e:
                print(f"✗ {quiz_file.name}: JSON inválido - {e}")
                return False
            except Exception as e:
                print(f"✗ {quiz_file.name}: error - {e}")
                return False
    else:
        print("⚠️  Directorio de quizzes no existe")
    
    print("✓ Archivos JSON verificados correctamente")
    return True

def main():
    """Ejecutar todas las pruebas."""
    print("INICIANDO VERIFICACIÓN DEL SISTEMA DE QUIZZES")
    print("=" * 50)
    
    tests = [
        ("Estructura de archivos", test_file_structure),
        ("Archivos JSON", test_json_files),
        ("FileManager", test_file_manager),
        ("NetworkUtils", test_network_utils),
        ("QuizManager", test_quiz_manager)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name.upper()}")
        print("-" * len(test_name))
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Error crítico en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASÓ" if result else "✗ FALLÓ"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"TOTAL: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("El sistema está listo para usar.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} pruebas fallaron.")
        print("Revisa los errores arriba y corrige los problemas.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
