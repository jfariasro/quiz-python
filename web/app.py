"""
Aplicación web Flask para la plataforma de quizzes.
Servidor que permite a los participantes unirse y participar en quizzes.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import logging
from typing import Optional, Dict, Any

from utils.file_manager import FileManager
from utils.network_utils import NetworkUtils
from utils.quiz_logic import QuizManager, QuizState

logger = logging.getLogger(__name__)

# Instancias globales
quiz_manager = QuizManager()
file_manager = FileManager()
socketio = None

def create_app(config: Optional[Dict] = None) -> Flask:
    """
    Crear y configurar la aplicación Flask.
    
    Args:
        config: Configuración opcional de la aplicación
        
    Returns:
        Aplicación Flask configurada
    """
    global socketio
    
    # Configurar rutas de archivos estáticos
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_folder = os.path.join(os.path.dirname(current_dir), 'static')
    template_folder = os.path.join(current_dir, 'templates')
    
    app = Flask(__name__, 
                static_folder=static_folder,
                template_folder=template_folder)
    
    try:
        # Cargar configuración de red
        network_config = file_manager.load_network_config()
        
        # Configuración por defecto
        app.config.update({
            'SECRET_KEY': 'quiz-platform-secret-key-change-in-production',
            'DEBUG': True,
            'TESTING': False,
            'HOST': network_config.get('host', '0.0.0.0'),
            'PORT': network_config.get('port', 5000)
        })
    except Exception as e:
        logger.warning(f"Error al cargar configuración de red: {e}. Usando valores predeterminados.")
        # Usar configuración predeterminada en caso de error
        app.config.update({
            'SECRET_KEY': 'quiz-platform-secret-key-change-in-production',
            'DEBUG': True,
            'TESTING': False,
            'HOST': '0.0.0.0',
            'PORT': 5000
        })
    
    # Si hay configuración adicional, aplicarla
    if config:
        app.config.update(config)
    
    # Inicializar SocketIO
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        logger=False,
        engineio_logger=False
    )
    
    # Registrar rutas
    register_routes(app)
    register_socketio_events(socketio)
    
    logger.info("Aplicación Flask creada y configurada")
    return app

def register_routes(app: Flask):
    """Registrar rutas HTTP de la aplicación."""
    
    @app.route('/')
    def index():
        """Página principal para unirse a quiz."""
        # Verificar si hay sesión activa
        active_sessions = quiz_manager.get_active_sessions()
        
        if not active_sessions:
            return render_template('no_quiz.html')
        
        # Por simplicidad, usar la primera sesión activa
        session_id = active_sessions[0]
        session = quiz_manager.get_session(session_id)
        
        return render_template('index.html', 
                             session_id=session_id,
                             quiz_title=session.quiz_data.get('title', 'Quiz'),
                             can_join=session.state == QuizState.WAITING)
    
    @app.route('/join', methods=['POST'])
    def join_quiz():
        """Endpoint para unirse a un quiz."""
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Nombre requerido'}), 400
        
        name = data['name'].strip()
        if not name:
            return jsonify({'error': 'Nombre no puede estar vacío'}), 400
        
        # Obtener sesión activa
        active_sessions = quiz_manager.get_active_sessions()
        if not active_sessions:
            return jsonify({'error': 'No hay quiz activo'}), 404
        
        session_id = active_sessions[0]
        session = quiz_manager.get_session(session_id)
        
        # Generar ID único para participante
        import uuid
        participant_id = str(uuid.uuid4())
        
        # Agregar participante
        success = session.add_participant(participant_id, name)
        
        if not success:
            return jsonify({'error': 'No se pudo unir al quiz'}), 400
        
        return jsonify({
            'success': True,
            'participant_id': participant_id,
            'session_id': session_id,
            'redirect_url': url_for('lobby', participant_id=participant_id)
        })
    
    @app.route('/lobby/<participant_id>')
    def lobby(participant_id: str):
        """Sala de espera para participantes."""
        # Verificar que el participante existe
        active_sessions = quiz_manager.get_active_sessions()
        if not active_sessions:
            return redirect(url_for('index'))
        
        session = quiz_manager.get_session(active_sessions[0])
        if participant_id not in session.participants:
            return redirect(url_for('index'))
        
        participant = session.participants[participant_id]
        
        return render_template('lobby.html',
                             participant_id=participant_id,
                             participant_name=participant['name'],
                             session_id=session.session_id,
                             quiz_title=session.quiz_data.get('title', 'Quiz'))
    
    @app.route('/quiz/<participant_id>')
    def quiz_interface(participant_id: str):
        """Interfaz principal del quiz para participantes."""
        # Verificar participante
        active_sessions = quiz_manager.get_active_sessions()
        if not active_sessions:
            return redirect(url_for('index'))
        
        session = quiz_manager.get_session(active_sessions[0])
        if participant_id not in session.participants:
            return redirect(url_for('index'))
        
        participant = session.participants[participant_id]
        
        return render_template('quiz.html',
                             participant_id=participant_id,
                             participant_name=participant['name'],
                             session_id=session.session_id,
                             quiz_title=session.quiz_data.get('title', 'Quiz'))
    
    @app.route('/api/session/status')
    def session_status_general():
        """Obtener estado general de las sesiones activas."""
        active_sessions = quiz_manager.get_active_sessions()
        
        if not active_sessions:
            return jsonify({
                'active_session': None,
                'message': 'No hay quiz activo en este momento'
            })
        
        # Devolver la primera sesión activa
        session = active_sessions[0]
        return jsonify({
            'active_session': {
                'session_id': session.session_id,
                'state': session.state.value,
                'current_question': session.current_question_index,
                'total_questions': len(session.quiz_data.get('questions', [])),
                'participants_count': len(session.participants),
                'quiz_title': session.quiz_data.get('title', 'Quiz'),
                'time_per_question': session.quiz_data.get('question_time_limit', 30)
            }
        })
    
    @app.route('/api/session/<session_id>/status')
    def session_status(session_id: str):
        """Obtener estado actual de la sesión."""
        session = quiz_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Sesión no encontrada'}), 404
        
        return jsonify({
            'session_id': session_id,
            'state': session.state.value,
            'current_question': session.current_question_index,
            'total_questions': len(session.quiz_data.get('questions', [])),
            'participants_count': len(session.participants),
            'quiz_title': session.quiz_data.get('title', 'Quiz')
        })
    
    @app.route('/api/leaderboard/<session_id>')
    def get_leaderboard(session_id: str):
        """Obtener leaderboard de la sesión."""
        session = quiz_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Sesión no encontrada'}), 404
        
        leaderboard = session.get_leaderboard()
        return jsonify({'leaderboard': leaderboard})
    
    @app.route('/api/admin/start_session', methods=['POST'])
    def api_admin_start_session():
        """Endpoint para iniciar sesión de quiz desde la administración."""
        data = request.get_json()
        if not data or 'quiz_data' not in data:
            return jsonify({'error': 'Faltan datos del quiz'}), 400
        quiz_data = data['quiz_data']
        try:
            session_id = quiz_manager.create_session(quiz_data)
            setup_session_callbacks(session_id)
            logger.info(f"Sesión de quiz iniciada vía API admin: {session_id}")
            return jsonify({'success': True, 'session_id': session_id})
        except Exception as e:
            logger.error(f"Error al crear sesión desde admin: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Página de error 404."""
        return render_template('error.html', 
                             error_code=404,
                             error_message='Página no encontrada'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Página de error 500."""
        logger.error(f"Error interno: {error}")
        return render_template('error.html',
                             error_code=500,
                             error_message='Error interno del servidor'), 500

def register_socketio_events(socketio: SocketIO):
    """Registrar eventos de WebSocket."""
    
    @socketio.on('connect')
    def handle_connect():
        """Cliente conectado via WebSocket."""
        logger.debug(f"Cliente conectado: {request.sid}")
        emit('connected', {'status': 'connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Cliente desconectado via WebSocket."""
        logger.debug(f"Cliente desconectado: {request.sid}")
    
    @socketio.on('join_session')
    def handle_join_session(data):
        """Participante se une a una sesión via WebSocket."""
        session_id = data.get('session_id')
        participant_id = data.get('participant_id')
        
        if not session_id or not participant_id:
            emit('error', {'message': 'Datos faltantes'})
            return
        
        session = quiz_manager.get_session(session_id)
        if not session or participant_id not in session.participants:
            emit('error', {'message': 'Sesión o participante no válido'})
            return
        
        # Unir al room de la sesión
        join_room(session_id)
        
        # Enviar estado actual
        emit('session_state', {
            'state': session.state.value,
            'current_question': session.current_question_index,
            'total_questions': len(session.quiz_data.get('questions', []))
        })
        
        logger.debug(f"Participante {participant_id} unido a sesión {session_id}")
    
    @socketio.on('submit_answer')
    def handle_submit_answer(data):
        """Procesar respuesta de participante."""
        session_id = data.get('session_id')
        participant_id = data.get('participant_id')
        answer = data.get('answer')
        
        if not all([session_id, participant_id, answer is not None]):
            emit('error', {'message': 'Datos faltantes'})
            return
        
        session = quiz_manager.get_session(session_id)
        if not session:
            emit('error', {'message': 'Sesión no encontrada'})
            return
        
        # Enviar respuesta
        success = session.submit_answer(participant_id, answer)
        
        if success:
            emit('answer_submitted', {'success': True})
            # Notificar a admin que se recibió respuesta
            socketio.emit('participant_answered', {
                'participant_id': participant_id,
                'participant_name': session.participants[participant_id]['name']
            }, room=f"admin_{session_id}")
        else:
            emit('answer_submitted', {'success': False, 'message': 'Respuesta no aceptada'})
    
    @socketio.on('admin_join')
    def handle_admin_join(data):
        """Administrador se conecta para controlar sesión."""
        session_id = data.get('session_id')
        
        if not session_id:
            emit('error', {'message': 'ID de sesión requerido'})
            return
        
        # Unir al room de administración
        join_room(f"admin_{session_id}")
        
        session = quiz_manager.get_session(session_id)
        if session:
            # Enviar estado completo al admin
            emit('admin_session_state', {
                'state': session.state.value,
                'current_question': session.current_question_index,
                'participants': list(session.participants.values()),
                'quiz_data': session.quiz_data
            })
        
        logger.debug(f"Admin conectado a sesión {session_id}")

def setup_session_callbacks(session_id: str):
    """Configurar callbacks para eventos de la sesión."""
    session = quiz_manager.get_session(session_id)
    if not session:
        return
    
    def on_state_change(session_obj, event, data):
        """Callback para cambios de estado."""
        socketio.emit('state_change', {
            'state': session_obj.state.value,
            'data': data
        }, room=session_id)
        
        # Notificar también a admin
        socketio.emit('admin_state_change', {
            'state': session_obj.state.value,
            'data': data
        }, room=f"admin_{session_id}")
    
    def on_question_started(session_obj, event, data):
        """Callback para inicio de pregunta."""
        question_data = data['question']
        
        # Enviar pregunta a participantes (sin respuesta correcta)
        participant_data = {
            'question_index': data['question_index'],
            'question': question_data['question'],
            'options': question_data['options'],
            'time_limit': data['time_limit']
        }
        
        socketio.emit('question_started', participant_data, room=session_id)
        
        # Enviar datos completos a admin
        socketio.emit('admin_question_started', data, room=f"admin_{session_id}")
    
    def on_question_results(session_obj, event, data):
        """Callback para resultados de pregunta."""
        socketio.emit('question_results', data, room=session_id)
        socketio.emit('admin_question_results', data, room=f"admin_{session_id}")
    
    def on_quiz_finished(session_obj, event, data):
        """Callback para final del quiz."""
        socketio.emit('quiz_finished', data, room=session_id)
        socketio.emit('admin_quiz_finished', data, room=f"admin_{session_id}")
    
    def on_participant_join(session_obj, event, data):
        """Callback para nuevo participante."""
        socketio.emit('participant_joined', {
            'name': data['name'],
            'participant_count': len(session_obj.participants)
        }, room=session_id)
        
        socketio.emit('admin_participant_joined', data, room=f"admin_{session_id}")
    
    # Registrar callbacks
    session.add_event_callback('state_change', on_state_change)
    session.add_event_callback('question_started', on_question_started)
    session.add_event_callback('question_results', on_question_results)
    session.add_event_callback('quiz_finished', on_quiz_finished)
    session.add_event_callback('participant_join', on_participant_join)

# Funciones de utilidad para la aplicación de administración

def start_quiz_session(quiz_data: Dict[str, Any]) -> str:
    """
    Iniciar nueva sesión de quiz (llamada desde admin).
    
    Args:
        quiz_data: Datos del quiz a ejecutar
        
    Returns:
        ID de la sesión creada
    """
    session_id = quiz_manager.create_session(quiz_data)
    setup_session_callbacks(session_id)
    
    logger.info(f"Sesión de quiz iniciada desde admin: {session_id}")
    return session_id

def stop_quiz_session(session_id: str):
    """
    Detener sesión de quiz (llamada desde admin).
    
    Args:
        session_id: ID de la sesión a detener
    """
    session = quiz_manager.get_session(session_id)
    if session:
        # Notificar a todos los participantes
        socketio.emit('quiz_stopped', {
            'message': 'El quiz ha sido detenido por el administrador'
        }, room=session_id)
        
        quiz_manager.end_session(session_id)
        logger.info(f"Sesión de quiz detenida desde admin: {session_id}")

def get_session_info(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtener información de sesión (para admin).
    
    Args:
        session_id: ID de la sesión
        
    Returns:
        Información de la sesión o None si no existe
    """
    session = quiz_manager.get_session(session_id)
    if not session:
        return None
    
    return {
        'session_id': session_id,
        'state': session.state.value,
        'quiz_title': session.quiz_data.get('title', 'Quiz'),
        'current_question': session.current_question_index,
        'total_questions': len(session.quiz_data.get('questions', [])),
        'participants': list(session.participants.values()),
        'stats': session.stats
    }

# Función para obtener la aplicación (para importar desde main.py)
def get_app():
    """Obtener instancia de la aplicación Flask."""
    return create_app()

def run_server(host=None, port=None, debug=True):
    """
    Iniciar el servidor Flask con la configuración de red.
    
    Args:
        host: Host opcional (sobreescribe la configuración)
        port: Puerto opcional (sobreescribe la configuración)
        debug: Modo debug
    """
    app = create_app()
    
    try:
        network_config = file_manager.load_network_config()
        
        # Usar configuración proporcionada o valores por defecto del archivo de configuración
        server_host = host or network_config.get('host', '0.0.0.0')
        server_port = port or network_config.get('port', 5000)
    except Exception as e:
        logger.warning(f"Error al cargar configuración de red: {e}. Usando valores predeterminados.")
        server_host = host or '0.0.0.0'
        server_port = port or 5000
    
    socketio.run(app, 
                host=server_host, 
                port=server_port, 
                debug=debug,
                allow_unsafe_werkzeug=True)  # Necesario para permitir conexiones externas en modo debug

if __name__ == '__main__':
    # Para desarrollo directo
    run_server(debug=True)
