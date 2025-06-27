"""
Utilidades para el manejo de archivos del sistema de quizzes.
Gestiona el almacenamiento basado en archivos JSON.
"""

import json
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class FileManager:
    """Gestor de archivos para la plataforma de quizzes."""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Inicializar el gestor de archivos.
        
        Args:
            base_path: Ruta base del proyecto. Si no se especifica, usa la carpeta del archivo principal.
        """
        if base_path is None:
            # Obtener la ruta del proyecto (3 niveles arriba desde utils/file_manager.py)
            self.base_path = Path(__file__).parent.parent
        else:
            self.base_path = Path(base_path)
        
        self.data_path = self.base_path / 'data'
        self.quizzes_path = self.data_path / 'quizzes'
        self.sessions_path = self.data_path / 'sessions'
        self.history_path = self.data_path / 'history'
        self.config_path = self.data_path / 'config'
        
        # Crear directorios si no existen
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Asegurar que todos los directorios necesarios existen."""
        directories = [
            self.data_path,
            self.quizzes_path,
            self.sessions_path,
            self.history_path,
            self.config_path
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directorio verificado: {directory}")
    
    def _generate_id(self) -> str:
        """Generar un ID único."""
        return str(uuid.uuid4())
    
    def _get_timestamp(self) -> str:
        """Obtener timestamp actual en formato ISO."""
        return datetime.now().isoformat()
    
    # ===== GESTIÓN DE QUIZZES =====
    
    def save_quiz(self, quiz_data: Dict[str, Any]) -> str:
        """
        Guardar un quiz en el sistema de archivos.
        
        Args:
            quiz_data: Datos del quiz a guardar
            
        Returns:
            ID del quiz guardado
        """
        # Asignar ID si no existe
        if 'id' not in quiz_data:
            quiz_data['id'] = self._generate_id()
        
        # Asignar timestamps
        quiz_data['created_at'] = quiz_data.get('created_at', self._get_timestamp())
        quiz_data['updated_at'] = self._get_timestamp()
        
        # Validar estructura básica
        self._validate_quiz_structure(quiz_data)
        
        # Guardar archivo
        quiz_file = self.quizzes_path / f"{quiz_data['id']}.json"
        
        try:
            with open(quiz_file, 'w', encoding='utf-8') as f:
                json.dump(quiz_data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Quiz guardado: {quiz_data['id']} - {quiz_data['title']}")
            return quiz_data['id']
            
        except Exception as e:
            logger.error(f"Error al guardar quiz {quiz_data['id']}: {e}")
            raise
    
    def load_quiz(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """
        Cargar un quiz por su ID.
        
        Args:
            quiz_id: ID del quiz a cargar
            
        Returns:
            Datos del quiz o None si no existe
        """
        quiz_file = self.quizzes_path / f"{quiz_id}.json"
        
        if not quiz_file.exists():
            logger.warning(f"Quiz no encontrado: {quiz_id}")
            return None
        
        try:
            with open(quiz_file, 'r', encoding='utf-8') as f:
                quiz_data = json.load(f)
            
            logger.debug(f"Quiz cargado: {quiz_id}")
            return quiz_data
            
        except Exception as e:
            logger.error(f"Error al cargar quiz {quiz_id}: {e}")
            return None
    
    def list_quizzes(self) -> List[Dict[str, Any]]:
        """
        Listar todos los quizzes disponibles.
        
        Returns:
            Lista de metadatos de quizzes
        """
        quizzes = []
        
        for quiz_file in self.quizzes_path.glob("*.json"):
            try:
                with open(quiz_file, 'r', encoding='utf-8') as f:
                    quiz_data = json.load(f)
                
                # Extraer solo metadatos básicos
                quiz_metadata = {
                    'id': quiz_data['id'],
                    'title': quiz_data['title'],
                    'description': quiz_data.get('description', ''),
                    'question_count': len(quiz_data.get('questions', [])),
                    'created_at': quiz_data.get('created_at'),
                    'updated_at': quiz_data.get('updated_at')
                }
                
                quizzes.append(quiz_metadata)
                
            except Exception as e:
                logger.error(f"Error al leer quiz {quiz_file}: {e}")
                continue
        
        # Ordenar por fecha de actualización (más reciente primero)
        quizzes.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        logger.info(f"Encontrados {len(quizzes)} quizzes")
        return quizzes
    
    def delete_quiz(self, quiz_id: str) -> bool:
        """
        Eliminar un quiz del sistema.
        
        Args:
            quiz_id: ID del quiz a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        quiz_file = self.quizzes_path / f"{quiz_id}.json"
        
        if not quiz_file.exists():
            logger.warning(f"Quiz no encontrado para eliminar: {quiz_id}")
            return False
        
        try:
            quiz_file.unlink()
            logger.info(f"Quiz eliminado: {quiz_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar quiz {quiz_id}: {e}")
            return False
    
    def duplicate_quiz(self, quiz_id: str, new_title: Optional[str] = None) -> Optional[str]:
        """
        Duplicar un quiz existente.
        
        Args:
            quiz_id: ID del quiz a duplicar
            new_title: Nuevo título para el quiz duplicado
            
        Returns:
            ID del nuevo quiz duplicado o None si hay error
        """
        original_quiz = self.load_quiz(quiz_id)
        if not original_quiz:
            return None
        
        # Crear copia con nuevo ID
        new_quiz = original_quiz.copy()
        new_quiz['id'] = self._generate_id()
        new_quiz['title'] = new_title or f"{original_quiz['title']} (Copia)"
        
        # Limpiar timestamps para que se generen nuevos
        if 'created_at' in new_quiz:
            del new_quiz['created_at']
        if 'updated_at' in new_quiz:
            del new_quiz['updated_at']
        
        return self.save_quiz(new_quiz)
    
    def _validate_quiz_structure(self, quiz_data: Dict[str, Any]):
        """
        Validar que el quiz tenga la estructura requerida.
        
        Args:
            quiz_data: Datos del quiz a validar
            
        Raises:
            ValueError: Si la estructura no es válida
        """
        required_fields = ['id', 'title']
        
        for field in required_fields:
            if field not in quiz_data:
                raise ValueError(f"Campo requerido faltante: {field}")
        
        # Validar preguntas si existen
        if 'questions' in quiz_data:
            for i, question in enumerate(quiz_data['questions']):
                if 'question' not in question:
                    raise ValueError(f"Pregunta {i} sin texto")
                if 'options' not in question or len(question['options']) < 2:
                    raise ValueError(f"Pregunta {i} debe tener al menos 2 opciones")
                if 'correct_answer' not in question:
                    raise ValueError(f"Pregunta {i} sin respuesta correcta")
    
    # ===== GESTIÓN DE SESIONES =====
    
    def save_session(self, session_data: Dict[str, Any]) -> str:
        """
        Guardar una sesión de quiz.
        
        Args:
            session_data: Datos de la sesión
            
        Returns:
            ID de la sesión guardada
        """
        if 'id' not in session_data:
            session_data['id'] = self._generate_id()
        
        session_data['created_at'] = session_data.get('created_at', self._get_timestamp())
        session_data['updated_at'] = self._get_timestamp()
        
        session_file = self.sessions_path / f"{session_data['id']}.json"
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Sesión guardada: {session_data['id']}")
            return session_data['id']
            
        except Exception as e:
            logger.error(f"Error al guardar sesión {session_data['id']}: {e}")
            raise
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Cargar una sesión por su ID.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Datos de la sesión o None si no existe
        """
        session_file = self.sessions_path / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error al cargar sesión {session_id}: {e}")
            return None
    
    # ===== GESTIÓN DE HISTORIAL =====
    
    def save_history_record(self, history_data: Dict[str, Any]) -> str:
        """
        Guardar un registro en el historial.
        
        Args:
            history_data: Datos del registro de historial
            
        Returns:
            ID del registro guardado
        """
        if 'id' not in history_data:
            history_data['id'] = self._generate_id()
        
        history_data['timestamp'] = self._get_timestamp()
        
        # Organizar por fecha (año-mes)
        date_str = datetime.now().strftime("%Y-%m")
        date_dir = self.history_path / date_str
        date_dir.mkdir(exist_ok=True)
        
        history_file = date_dir / f"{history_data['id']}.json"
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Registro de historial guardado: {history_data['id']}")
            return history_data['id']
            
        except Exception as e:
            logger.error(f"Error al guardar historial {history_data['id']}: {e}")
            raise
    
    def load_history_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Cargar registros del historial.
        
        Args:
            limit: Número máximo de registros a cargar
            
        Returns:
            Lista de registros de historial
        """
        records = []
        
        # Buscar en todas las carpetas de fecha
        for date_dir in sorted(self.history_path.iterdir(), reverse=True):
            if not date_dir.is_dir():
                continue
            
            for history_file in sorted(date_dir.glob("*.json"), reverse=True):
                if len(records) >= limit:
                    break
                
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        record = json.load(f)
                    records.append(record)
                except Exception as e:
                    logger.error(f"Error al leer historial {history_file}: {e}")
                    continue
            
            if len(records) >= limit:
                break
        
        logger.info(f"Cargados {len(records)} registros de historial")
        return records
    
    # ===== GESTIÓN DE CONFIGURACIÓN =====
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """
        Cargar archivo de configuración.
        
        Args:
            config_name: Nombre del archivo de configuración (sin extensión)
            
        Returns:
            Diccionario de configuración
        """
        config_file = self.config_path / f"{config_name}.json"
        
        if not config_file.exists():
            logger.warning(f"Archivo de configuración no encontrado: {config_name}")
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error al cargar configuración {config_name}: {e}")
            return {}
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]):
        """
        Guardar archivo de configuración.
        
        Args:
            config_name: Nombre del archivo de configuración (sin extensión)
            config_data: Datos de configuración
        """
        config_file = self.config_path / f"{config_name}.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Configuración guardada: {config_name}")
            
        except Exception as e:
            logger.error(f"Error al guardar configuración {config_name}: {e}")
            raise
    
    def load_network_config(self) -> Dict[str, Any]:
        """
        Cargar la configuración de red desde el archivo network_config.json.
        
        Returns:
            Diccionario con la configuración de red
        """
        try:
            config_file = self.config_path / 'network_config.json'
            
            if not config_file.exists():
                # Crear configuración por defecto si no existe
                default_config = {
                    "host": "0.0.0.0",
                    "port": 5000,
                    "auto_detect_ip": True,
                    "allowed_origins": ["*"]
                }
                
                # Guardar configuración por defecto
                self.save_json(config_file, default_config)
                return default_config
            
            # Cargar configuración existente
            return self.load_json(config_file)
            
        except Exception as e:
            logger.error(f"Error al cargar configuración de red: {e}")
            # Retornar configuración por defecto en caso de error
            return {
                "host": "0.0.0.0",
                "port": 5000,
                "auto_detect_ip": True,
                "allowed_origins": ["*"]
            }
    
    def load_json(self, file_path: Path) -> Dict[str, Any]:
        """
        Cargar datos desde un archivo JSON.
        
        Args:
            file_path: Ruta al archivo JSON
            
        Returns:
            Diccionario con los datos del archivo
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error al cargar archivo JSON {file_path}: {e}")
            raise
    
    def save_json(self, file_path: Path, data: Dict[str, Any]):
        """
        Guardar datos en un archivo JSON.
        
        Args:
            file_path: Ruta donde guardar el archivo
            data: Datos a guardar
        """
        try:
            # Asegurar que el directorio existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar datos
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error al guardar archivo JSON {file_path}: {e}")
            raise
