"""
Lógica central del sistema de quizzes.
Gestiona las reglas de juego, puntuación y flujo de las sesiones.
"""

import time
import threading
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class QuizState(Enum):
    """Estados posibles de un quiz."""
    WAITING = "waiting"          # Esperando participantes
    STARTING = "starting"        # Iniciando (countdown)
    QUESTION = "question"        # Mostrando pregunta
    COLLECTING = "collecting"    # Recolectando respuestas
    RESULTS = "results"          # Mostrando resultados de pregunta
    LEADERBOARD = "leaderboard"  # Mostrando ranking
    FINISHED = "finished"        # Quiz terminado
    PAUSED = "paused"           # Quiz pausado

class ParticipantStatus(Enum):
    """Estados de un participante."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ANSWERED = "answered"
    WAITING = "waiting"

class QuizSession:
    """Gestiona una sesión de quiz en vivo."""
    
    def __init__(self, quiz_data: Dict[str, Any], session_id: str):
        """
        Inicializar sesión de quiz.
        
        Args:
            quiz_data: Datos del quiz
            session_id: ID único de la sesión
        """
        self.quiz_data = quiz_data
        self.session_id = session_id
        self.state = QuizState.WAITING
        
        # Control de flujo
        self.current_question_index = -1
        self.question_start_time = None
        self.question_end_time = None
        
        # Participantes
        self.participants = {}  # {participant_id: ParticipantData}
        self.max_participants = 50
        
        # Respuestas de la pregunta actual
        self.current_answers = {}  # {participant_id: answer_data}
        
        # Configuración
        self.settings = {
            'question_time_limit': quiz_data.get('question_time_limit', 30),
            'show_results_time': quiz_data.get('show_results_time', 5),
            'allow_late_join': quiz_data.get('allow_late_join', True),
            'points_for_correct': quiz_data.get('points_for_correct', 100),
            'speed_bonus_enabled': quiz_data.get('speed_bonus_enabled', True),
            'max_speed_bonus': quiz_data.get('max_speed_bonus', 50)
        }
        
        # Callbacks para eventos
        self.event_callbacks = {}
        
        # Control de threading
        self.timer_thread = None
        self.timer_lock = threading.Lock()
        
        # Estadísticas
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_questions': len(quiz_data.get('questions', [])),
            'questions_completed': 0,
            'participants_joined': 0,
            'total_answers': 0
        }
        
        logger.info(f"Sesión de quiz creada: {session_id}")
    
    def add_event_callback(self, event: str, callback: Callable):
        """
        Agregar callback para eventos de la sesión.
        
        Args:
            event: Tipo de evento (state_change, participant_join, etc.)
            callback: Función a llamar
        """
        if event not in self.event_callbacks:
            self.event_callbacks[event] = []
        self.event_callbacks[event].append(callback)
    
    def _emit_event(self, event: str, data: Any = None):
        """Emitir evento a todos los callbacks registrados."""
        if event in self.event_callbacks:
            for callback in self.event_callbacks[event]:
                try:
                    callback(self, event, data)
                except Exception as e:
                    logger.error(f"Error en callback {event}: {e}")
    
    def add_participant(self, participant_id: str, name: str, **kwargs) -> bool:
        """
        Agregar participante a la sesión.
        
        Args:
            participant_id: ID único del participante
            name: Nombre del participante
            **kwargs: Datos adicionales del participante
            
        Returns:
            True si se agregó correctamente, False en caso contrario
        """
        # Verificar límites
        if len(self.participants) >= self.max_participants:
            logger.warning(f"Sesión llena: {len(self.participants)} participantes")
            return False
        
        # Verificar si ya está registrado
        if participant_id in self.participants:
            logger.warning(f"Participante ya registrado: {participant_id}")
            return False
        
        # Verificar si se permite unirse tarde
        if self.state not in [QuizState.WAITING, QuizState.STARTING]:
            if not self.settings['allow_late_join']:
                logger.warning(f"No se permite unirse tarde: {participant_id}")
                return False
        
        # Crear datos del participante
        participant_data = {
            'id': participant_id,
            'name': name,
            'status': ParticipantStatus.CONNECTED,
            'score': 0,
            'answers': [],  # Historial de respuestas
            'join_time': time.time(),
            'last_seen': time.time(),
            **kwargs
        }
        
        self.participants[participant_id] = participant_data
        self.stats['participants_joined'] += 1
        
        logger.info(f"Participante agregado: {name} ({participant_id})")
        self._emit_event('participant_join', participant_data)
        
        return True
    
    def remove_participant(self, participant_id: str):
        """Remover participante de la sesión."""
        if participant_id in self.participants:
            participant_data = self.participants[participant_id]
            participant_data['status'] = ParticipantStatus.DISCONNECTED
            
            logger.info(f"Participante desconectado: {participant_data['name']}")
            self._emit_event('participant_leave', participant_data)
    
    def start_quiz(self) -> bool:
        """
        Iniciar el quiz.
        
        Returns:
            True si se inició correctamente, False en caso contrario
        """
        if self.state != QuizState.WAITING:
            logger.warning(f"No se puede iniciar quiz en estado: {self.state}")
            return False
        
        if len(self.participants) == 0:
            logger.warning("No se puede iniciar quiz sin participantes")
            return False
        
        self.stats['start_time'] = time.time()
        self._change_state(QuizState.STARTING)
        
        # Iniciar countdown y primera pregunta
        self._start_countdown(3, self._start_first_question)
        
        logger.info(f"Quiz iniciado con {len(self.participants)} participantes")
        return True
    
    def next_question(self) -> bool:
        """
        Avanzar a la siguiente pregunta.
        
        Returns:
            True si hay siguiente pregunta, False si el quiz terminó
        """
        if self.state == QuizState.FINISHED:
            return False
        
        self.current_question_index += 1
        questions = self.quiz_data.get('questions', [])
        
        if self.current_question_index >= len(questions):
            self._finish_quiz()
            return False
        
        self._start_question()
        return True
    
    def submit_answer(self, participant_id: str, answer: Any) -> bool:
        """
        Enviar respuesta de un participante.
        
        Args:
            participant_id: ID del participante
            answer: Respuesta seleccionada
            
        Returns:
            True si se procesó correctamente, False en caso contrario
        """
        if self.state != QuizState.COLLECTING:
            logger.warning(f"No se aceptan respuestas en estado: {self.state}")
            return False
        
        if participant_id not in self.participants:
            logger.warning(f"Participante no encontrado: {participant_id}")
            return False
        
        if participant_id in self.current_answers:
            logger.warning(f"Participante ya respondió: {participant_id}")
            return False
        
        # Registrar respuesta
        answer_time = time.time()
        answer_data = {
            'participant_id': participant_id,
            'answer': answer,
            'timestamp': answer_time,
            'response_time': answer_time - self.question_start_time
        }
        
        self.current_answers[participant_id] = answer_data
        self.participants[participant_id]['status'] = ParticipantStatus.ANSWERED
        self.stats['total_answers'] += 1
        
        logger.debug(f"Respuesta recibida de {participant_id}: {answer}")
        self._emit_event('answer_received', answer_data)
        
        return True
    
    def _start_countdown(self, seconds: int, callback: Callable):
        """Iniciar countdown con callback al finalizar."""
        def countdown():
            for i in range(seconds, 0, -1):
                self._emit_event('countdown_tick', i)
                time.sleep(1)
            callback()
        
        threading.Thread(target=countdown, daemon=True).start()
    
    def _start_first_question(self):
        """Iniciar la primera pregunta."""
        self.current_question_index = 0
        self._start_question()
    
    def _start_question(self):
        """Iniciar pregunta actual."""
        if self.current_question_index >= len(self.quiz_data.get('questions', [])):
            self._finish_quiz()
            return
        
        # Limpiar respuestas anteriores
        self.current_answers.clear()
        
        # Resetear estado de participantes
        for participant in self.participants.values():
            participant['status'] = ParticipantStatus.WAITING
        
        # Cambiar estado y configurar timing
        self._change_state(QuizState.QUESTION)
        self.question_start_time = time.time()
        
        # Programar fin de pregunta
        question_time = self.settings['question_time_limit']
        with self.timer_lock:
            if self.timer_thread:
                # Cancelar timer anterior si existe
                pass
            
            self.timer_thread = threading.Timer(
                question_time,
                self._end_question_time
            )
            self.timer_thread.start()
        
        current_question = self.quiz_data['questions'][self.current_question_index]
        logger.info(f"Pregunta {self.current_question_index + 1} iniciada")
        
        # Cambiar a estado de recolección
        self._change_state(QuizState.COLLECTING)
        self._emit_event('question_started', {
            'question_index': self.current_question_index,
            'question': current_question,
            'time_limit': question_time
        })
    
    def _end_question_time(self):
        """Terminar tiempo de pregunta y mostrar resultados."""
        if self.state != QuizState.COLLECTING:
            return
        
        self.question_end_time = time.time()
        
        # Procesar resultados
        results = self._calculate_question_results()
        
        # Mostrar resultados
        self._change_state(QuizState.RESULTS)
        self._emit_event('question_results', results)
        
        # Programar siguiente pregunta o leaderboard
        self.stats['questions_completed'] += 1
        
        def show_next():
            time.sleep(self.settings['show_results_time'])
            
            # Mostrar leaderboard ocasionalmente
            if (self.current_question_index + 1) % 3 == 0:
                self._show_leaderboard()
            else:
                self.next_question()
        
        threading.Thread(target=show_next, daemon=True).start()
    
    def _calculate_question_results(self) -> Dict[str, Any]:
        """Calcular resultados de la pregunta actual."""
        current_question = self.quiz_data['questions'][self.current_question_index]
        correct_answer = current_question['correct_answer']
        
        results = {
            'question_index': self.current_question_index,
            'correct_answer': correct_answer,
            'total_participants': len(self.participants),
            'total_responses': len(self.current_answers),
            'correct_responses': 0,
            'incorrect_responses': 0,
            'answer_distribution': {},
            'participant_results': []
        }
        
        # Analizar respuestas
        for answer_data in self.current_answers.values():
            participant_id = answer_data['participant_id']
            participant = self.participants[participant_id]
            answer = answer_data['answer']
            response_time = answer_data['response_time']
            
            is_correct = answer == correct_answer
            points_earned = 0
            
            if is_correct:
                results['correct_responses'] += 1
                points_earned = self.settings['points_for_correct']
                
                # Bonus por velocidad
                if self.settings['speed_bonus_enabled']:
                    max_time = self.settings['question_time_limit']
                    time_factor = max(0, (max_time - response_time) / max_time)
                    speed_bonus = int(self.settings['max_speed_bonus'] * time_factor)
                    points_earned += speed_bonus
            else:
                results['incorrect_responses'] += 1
            
            # Actualizar puntuación del participante
            participant['score'] += points_earned
            
            # Agregar a historial de respuestas
            participant['answers'].append({
                'question_index': self.current_question_index,
                'answer': answer,
                'correct': is_correct,
                'points': points_earned,
                'response_time': response_time
            })
            
            # Agregar a resultados de la pregunta
            results['participant_results'].append({
                'participant_id': participant_id,
                'name': participant['name'],
                'answer': answer,
                'correct': is_correct,
                'points': points_earned,
                'response_time': response_time
            })
            
            # Actualizar distribución de respuestas
            if answer not in results['answer_distribution']:
                results['answer_distribution'][answer] = 0
            results['answer_distribution'][answer] += 1
        
        return results
    
    def _show_leaderboard(self):
        """Mostrar leaderboard temporal."""
        self._change_state(QuizState.LEADERBOARD)
        
        leaderboard = self.get_leaderboard()
        self._emit_event('leaderboard_show', leaderboard)
        
        # Continuar después de unos segundos
        def continue_quiz():
            time.sleep(5)
            self.next_question()
        
        threading.Thread(target=continue_quiz, daemon=True).start()
    
    def _finish_quiz(self):
        """Finalizar el quiz."""
        self._change_state(QuizState.FINISHED)
        self.stats['end_time'] = time.time()
        
        final_results = self.get_final_results()
        self._emit_event('quiz_finished', final_results)
        
        logger.info(f"Quiz finalizado: {self.session_id}")
    
    def _change_state(self, new_state: QuizState):
        """Cambiar estado del quiz."""
        old_state = self.state
        self.state = new_state
        
        logger.info(f"Estado cambiado: {old_state.value} -> {new_state.value}")
        self._emit_event('state_change', {
            'old_state': old_state,
            'new_state': new_state
        })
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener leaderboard actual.
        
        Args:
            limit: Número máximo de participantes a incluir
            
        Returns:
            Lista ordenada de participantes por puntuación
        """
        participants = [
            {
                'rank': 0,  # Se asignará después
                'participant_id': p['id'],
                'name': p['name'],
                'score': p['score'],
                'answers_count': len(p['answers']),
                'correct_answers': sum(1 for a in p['answers'] if a['correct'])
            }
            for p in self.participants.values()
            if p['status'] != ParticipantStatus.DISCONNECTED
        ]
        
        # Ordenar por puntuación (descendente)
        participants.sort(key=lambda x: x['score'], reverse=True)
        
        # Asignar rankings
        for i, participant in enumerate(participants[:limit]):
            participant['rank'] = i + 1
        
        return participants[:limit]
    
    def get_final_results(self) -> Dict[str, Any]:
        """Obtener resultados finales del quiz."""
        leaderboard = self.get_leaderboard(limit=len(self.participants))
        
        duration = 0
        if self.stats['start_time'] and self.stats['end_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
        
        return {
            'session_id': self.session_id,
            'quiz_title': self.quiz_data.get('title', 'Quiz sin título'),
            'leaderboard': leaderboard,
            'stats': {
                **self.stats,
                'duration': duration,
                'completion_rate': len(leaderboard) / max(1, self.stats['participants_joined'])
            },
            'timestamp': time.time()
        }
    
    def pause_quiz(self):
        """Pausar el quiz."""
        if self.state in [QuizState.QUESTION, QuizState.COLLECTING]:
            # Cancelar timer actual
            with self.timer_lock:
                if self.timer_thread:
                    self.timer_thread.cancel()
            
            self._change_state(QuizState.PAUSED)
            logger.info("Quiz pausado")
    
    def resume_quiz(self):
        """Reanudar el quiz."""
        if self.state == QuizState.PAUSED:
            # Reanudar desde donde se pausó
            self._change_state(QuizState.COLLECTING)
            
            # Recalcular tiempo restante (simplificado)
            remaining_time = self.settings['question_time_limit'] // 2
            
            with self.timer_lock:
                self.timer_thread = threading.Timer(
                    remaining_time,
                    self._end_question_time
                )
                self.timer_thread.start()
            
            logger.info("Quiz reanudado")
    
    def cleanup(self):
        """Limpiar recursos de la sesión."""
        with self.timer_lock:
            if self.timer_thread:
                self.timer_thread.cancel()
        
        self.event_callbacks.clear()
        logger.info(f"Sesión limpiada: {self.session_id}")


class QuizManager:
    """Gestor global de sesiones de quiz."""
    
    def __init__(self):
        """Inicializar gestor de quizzes."""
        self.active_sessions = {}  # {session_id: QuizSession}
        self.session_history = []
        
        logger.info("Gestor de quizzes inicializado")
    
    def generate_session_code(self, length=6) -> str:
        """
        Generar código de sesión fácil de recordar.
        
        Args:
            length: Longitud del código (por defecto 6)
            
        Returns:
            Código de sesión alfanumérico
        """
        # Caracteres permitidos (sin caracteres similares como 0/O, 1/I, etc.)
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        
        # Generar código aleatorio
        code = ''.join(random.choice(chars) for _ in range(length))
        
        # Asegurar que sea único
        while code in self.active_sessions:
            code = ''.join(random.choice(chars) for _ in range(length))
            
        return code
    
    def create_session(self, quiz_data: Dict[str, Any], session_id: Optional[str] = None) -> str:
        """
        Crear nueva sesión de quiz.
        
        Args:
            quiz_data: Datos del quiz
            session_id: ID opcional para la sesión
            
        Returns:
            ID de la sesión creada
        """
        if session_id is None:
            # Generar código fácil de recordar
            session_id = self.generate_session_code()
        
        if session_id in self.active_sessions:
            raise ValueError(f"Sesión ya existe: {session_id}")
        
        session = QuizSession(quiz_data, session_id)
        self.active_sessions[session_id] = session
        
        logger.info(f"Sesión creada: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[QuizSession]:
        """Obtener sesión por ID."""
        return self.active_sessions.get(session_id)
    
    def end_session(self, session_id: str):
        """Finalizar sesión."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Guardar en historial
            final_results = session.get_final_results()
            self.session_history.append(final_results)
            
            # Limpiar sesión
            session.cleanup()
            del self.active_sessions[session_id]
            
            logger.info(f"Sesión finalizada: {session_id}")
    
    def get_active_sessions(self) -> List[str]:
        """Obtener lista de sesiones activas."""
        return list(self.active_sessions.keys())
    
    def cleanup_finished_sessions(self):
        """Limpiar sesiones terminadas."""
        finished_sessions = [
            session_id for session_id, session in self.active_sessions.items()
            if session.state == QuizState.FINISHED
        ]
        
        for session_id in finished_sessions:
            self.end_session(session_id)
        
        if finished_sessions:
            logger.info(f"Limpiadas {len(finished_sessions)} sesiones terminadas")
