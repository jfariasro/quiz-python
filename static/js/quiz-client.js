/*
 * Cliente JavaScript para funcionalidades específicas del quiz
 * Maneja la lógica del lado cliente durante el juego
 */

class QuizClient {
    constructor() {
        this.socket = null;
        this.sessionId = null;
        this.participantId = null;
        this.currentQuestion = null;
        this.timer = null;
        this.scores = {};
        this.answered = false;
        
        this.initializeSocket();
        this.bindEvents();
    }
    
    initializeSocket() {
        this.socket = io();
        
        // Eventos de conexión
        this.socket.on('connect', () => {
            console.log('Conectado al servidor de quiz');
            this.showConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Desconectado del servidor');
            this.showConnectionStatus(false);
            this.showAlert('Conexión perdida. Intentando reconectar...', 'warning');
        });
        
        // Eventos del juego
        this.socket.on('session_started', (data) => {
            this.handleSessionStarted(data);
        });
        
        this.socket.on('question_started', (data) => {
            this.handleQuestionStarted(data);
        });
        
        this.socket.on('question_ended', (data) => {
            this.handleQuestionEnded(data);
        });
        
        this.socket.on('quiz_ended', (data) => {
            this.handleQuizEnded(data);
        });
        
        this.socket.on('participant_joined', (data) => {
            this.handleParticipantJoined(data);
        });
        
        this.socket.on('participant_left', (data) => {
            this.handleParticipantLeft(data);
        });
        
        this.socket.on('answer_submitted', (data) => {
            this.handleAnswerSubmitted(data);
        });
        
        this.socket.on('scores_updated', (data) => {
            this.handleScoresUpdated(data);
        });
        
        this.socket.on('error', (data) => {
            console.error('Error del servidor:', data);
            this.showAlert(data.message || 'Error de conexión', 'danger');
        });
    }
    
    bindEvents() {
        // Botones de respuesta
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('answer-btn')) {
                this.submitAnswer(e.target);
            }
        });
        
        // Formulario de unirse a sesión
        const joinForm = document.getElementById('join-form');
        if (joinForm) {
            joinForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.joinSession();
            });
        }
        
        // Botón de salir
        const leaveBtn = document.getElementById('leave-btn');
        if (leaveBtn) {
            leaveBtn.addEventListener('click', () => {
                this.leaveSession();
            });
        }
    }
    
    joinSession() {
        const sessionIdInput = document.getElementById('session-id');
        const participantNameInput = document.getElementById('participant-name');
        
        if (!sessionIdInput || !participantNameInput) {
            this.showAlert('Por favor, completa todos los campos', 'warning');
            return;
        }
        
        const sessionId = sessionIdInput.value.trim();
        const participantName = participantNameInput.value.trim();
        
        if (!sessionId || !participantName) {
            this.showAlert('Por favor, completa todos los campos', 'warning');
            return;
        }
        
        this.sessionId = sessionId;
        this.socket.emit('join_session', {
            session_id: sessionId,
            participant_name: participantName
        });
        
        this.showLoading(document.getElementById('join-btn'));
    }
    
    leaveSession() {
        if (this.sessionId) {
            this.socket.emit('leave_session', {
                session_id: this.sessionId
            });
            
            // Limpiar estado local
            this.sessionId = null;
            this.participantId = null;
            this.currentQuestion = null;
            this.clearTimer();
            
            // Redirigir a la página principal
            window.location.href = '/';
        }
    }
    
    submitAnswer(button) {
        if (this.answered || !this.currentQuestion) {
            return;
        }
        
        const answerIndex = parseInt(button.dataset.answer);
        
        this.socket.emit('submit_answer', {
            session_id: this.sessionId,
            question_id: this.currentQuestion.id,
            answer_index: answerIndex,
            time_taken: this.getTimeTaken()
        });
        
        this.answered = true;
        this.disableAnswerButtons();
        this.highlightSelectedAnswer(button);
        
        this.showAlert('Respuesta enviada', 'success');
    }
    
    handleSessionStarted(data) {
        console.log('Sesión iniciada:', data);
        this.showAlert('¡El quiz ha comenzado!', 'success');
        
        // Ocultar lobby y mostrar área de juego
        this.hideElement('lobby-area');
        this.showElement('game-area');
    }
    
    handleQuestionStarted(data) {
        console.log('Nueva pregunta:', data);
        this.currentQuestion = data.question;
        this.answered = false;
        
        this.displayQuestion(data.question);
        this.startTimer(data.time_limit);
        this.enableAnswerButtons();
        
        // Actualizar contador de preguntas
        this.updateQuestionCounter(data.question_number, data.total_questions);
    }
    
    handleQuestionEnded(data) {
        console.log('Pregunta terminada:', data);
        this.clearTimer();
        this.disableAnswerButtons();
        
        // Mostrar respuesta correcta
        this.highlightCorrectAnswer(data.correct_answer);
        
        // Mostrar estadísticas de la pregunta
        this.showQuestionStats(data.stats);
        
        // Programar siguiente pregunta
        setTimeout(() => {
            this.hideElement('question-stats');
        }, 3000);
    }
    
    handleQuizEnded(data) {
        console.log('Quiz terminado:', data);
        this.clearTimer();
        
        // Mostrar resultados finales
        this.showFinalResults(data.final_scores);
        
        // Ocultar área de juego
        this.hideElement('game-area');
        this.showElement('results-area');
    }
    
    handleParticipantJoined(data) {
        console.log('Nuevo participante:', data);
        this.updateParticipantsList(data.participants);
        this.showAlert(`${data.participant.name} se ha unido`, 'info');
    }
    
    handleParticipantLeft(data) {
        console.log('Participante salió:', data);
        this.updateParticipantsList(data.participants);
        this.showAlert(`${data.participant.name} ha salido`, 'warning');
    }
    
    handleAnswerSubmitted(data) {
        // Actualizar contador de respuestas
        this.updateAnswerCounter(data.answers_count, data.total_participants);
    }
    
    handleScoresUpdated(data) {
        console.log('Puntuaciones actualizadas:', data);
        this.scores = data.scores;
        this.updateScoreboard(data.scores);
    }
    
    displayQuestion(question) {
        const questionContainer = document.getElementById('question-container');
        if (!questionContainer) return;
        
        const html = `
            <div class="question-card fade-in">
                <h3 class="question-text">${question.text}</h3>
                <div class="answers-grid">
                    ${question.options.map((option, index) => `
                        <button class="answer-btn" data-answer="${index}">
                            <span class="answer-letter">${String.fromCharCode(65 + index)}</span>
                            <span class="answer-text">${option}</span>
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
        
        questionContainer.innerHTML = html;
    }
    
    startTimer(timeLimit) {
        this.clearTimer();
        
        const timerElement = document.getElementById('timer');
        if (!timerElement) return;
        
        let timeLeft = timeLimit;
        this.updateTimerDisplay(timeLeft);
        
        this.timer = setInterval(() => {
            timeLeft--;
            this.updateTimerDisplay(timeLeft);
            
            if (timeLeft <= 0) {
                this.clearTimer();
                if (!this.answered) {
                    this.showAlert('¡Tiempo agotado!', 'warning');
                    this.disableAnswerButtons();
                }
            }
        }, 1000);
    }
    
    clearTimer() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }
    
    updateTimerDisplay(timeLeft) {
        const timerElement = document.getElementById('timer');
        if (!timerElement) return;
        
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Cambiar color según el tiempo restante
        timerElement.className = 'timer';
        if (timeLeft <= 10) {
            timerElement.classList.add('timer-danger');
        } else if (timeLeft <= 30) {
            timerElement.classList.add('timer-warning');
        }
    }
    
    getTimeTaken() {
        // Calcular tiempo tomado basado en el timer actual
        const timerElement = document.getElementById('timer');
        if (!timerElement) return 0;
        
        const timeDisplay = timerElement.textContent;
        const [minutes, seconds] = timeDisplay.split(':').map(Number);
        const timeLeft = minutes * 60 + seconds;
        
        // Asumir que el tiempo total era el tiempo límite de la pregunta
        return Math.max(0, (this.currentQuestion?.time_limit || 30) - timeLeft);
    }
    
    enableAnswerButtons() {
        document.querySelectorAll('.answer-btn').forEach(btn => {
            btn.disabled = false;
            btn.classList.remove('selected', 'correct', 'incorrect');
        });
    }
    
    disableAnswerButtons() {
        document.querySelectorAll('.answer-btn').forEach(btn => {
            btn.disabled = true;
        });
    }
    
    highlightSelectedAnswer(button) {
        button.classList.add('selected');
    }
    
    highlightCorrectAnswer(correctIndex) {
        document.querySelectorAll('.answer-btn').forEach((btn, index) => {
            if (index === correctIndex) {
                btn.classList.add('correct');
            } else if (btn.classList.contains('selected')) {
                btn.classList.add('incorrect');
            }
        });
    }
    
    showQuestionStats(stats) {
        const statsContainer = document.getElementById('question-stats');
        if (!statsContainer) return;
        
        const html = `
            <div class="stats-card">
                <h4>Estadísticas de la pregunta</h4>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-label">Respuestas correctas:</span>
                        <span class="stat-value">${stats.correct_answers}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Respuestas totales:</span>
                        <span class="stat-value">${stats.total_answers}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Tiempo promedio:</span>
                        <span class="stat-value">${stats.average_time}s</span>
                    </div>
                </div>
            </div>
        `;
        
        statsContainer.innerHTML = html;
        this.showElement('question-stats');
    }
    
    showFinalResults(finalScores) {
        const resultsContainer = document.getElementById('final-results');
        if (!resultsContainer) return;
        
        const sortedScores = Object.entries(finalScores)
            .sort(([,a], [,b]) => b.score - a.score);
        
        const html = `
            <div class="results-card">
                <h2>¡Quiz Completado!</h2>
                <div class="final-scores">
                    <h3>Resultados Finales</h3>
                    <div class="scoreboard">
                        ${sortedScores.map(([participantId, data], index) => `
                            <div class="score-item ${index === 0 ? 'winner' : ''}">
                                <span class="position">${index + 1}</span>
                                <span class="name">${data.name}</span>
                                <span class="score">${data.score} pts</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <button class="btn btn-primary" onclick="window.location.href='/'">
                    Jugar Nuevamente
                </button>
            </div>
        `;
        
        resultsContainer.innerHTML = html;
    }
    
    updateParticipantsList(participants) {
        const participantsContainer = document.getElementById('participants-list');
        if (!participantsContainer) return;
        
        const html = participants.map(participant => `
            <div class="participant-item">
                <i class="fas fa-user"></i>
                <span>${participant.name}</span>
            </div>
        `).join('');
        
        participantsContainer.innerHTML = html;
        
        // Actualizar contador
        const countElement = document.getElementById('participants-count');
        if (countElement) {
            countElement.textContent = participants.length;
        }
    }
    
    updateScoreboard(scores) {
        const scoreboardContainer = document.getElementById('live-scoreboard');
        if (!scoreboardContainer) return;
        
        const sortedScores = Object.entries(scores)
            .sort(([,a], [,b]) => b.score - a.score)
            .slice(0, 5); // Mostrar solo los top 5
        
        const html = `
            <h4>Puntuaciones</h4>
            <div class="scoreboard-mini">
                ${sortedScores.map(([participantId, data], index) => `
                    <div class="score-mini-item">
                        <span class="position">${index + 1}</span>
                        <span class="name">${data.name}</span>
                        <span class="score">${data.score}</span>
                    </div>
                `).join('')}
            </div>
        `;
        
        scoreboardContainer.innerHTML = html;
    }
    
    updateQuestionCounter(current, total) {
        const counterElement = document.getElementById('question-counter');
        if (counterElement) {
            counterElement.textContent = `Pregunta ${current} de ${total}`;
        }
    }
    
    updateAnswerCounter(answered, total) {
        const counterElement = document.getElementById('answer-counter');
        if (counterElement) {
            counterElement.textContent = `Respuestas: ${answered}/${total}`;
        }
    }
    
    showConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (!statusElement) return;
        
        statusElement.className = connected ? 'status-connected' : 'status-disconnected';
        statusElement.innerHTML = connected ? 
            '<i class="fas fa-wifi"></i> Conectado' : 
            '<i class="fas fa-wifi"></i> Desconectado';
    }
    
    // Métodos de utilidad
    showElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'block';
            element.classList.add('fade-in');
        }
    }
    
    hideElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
            element.classList.remove('fade-in');
        }
    }
    
    showAlert(message, type = 'info') {
        // Usar la función global showAlert si está disponible
        if (typeof window.showAlert === 'function') {
            window.showAlert(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    showLoading(element, show = true) {
        if (typeof window.showLoading === 'function') {
            window.showLoading(element, show);
        } else {
            element.disabled = show;
        }
    }
}

// Inicializar cliente cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    if (document.body.classList.contains('quiz-page')) {
        window.quizClient = new QuizClient();
    }
});
