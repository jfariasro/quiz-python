/*
 * Funcionalidades JavaScript para la interfaz de administración web
 * Este archivo maneja la comunicación con la aplicación Tkinter via WebSockets
 */

class AdminInterface {
    constructor() {
        this.socket = null;
        this.currentSession = null;
        this.participants = [];
        this.sessionStatus = 'stopped';
        
        this.initializeSocket();
        this.bindEvents();
        this.loadInitialData();
    }
    
    initializeSocket() {
        this.socket = io('/admin');
        
        this.socket.on('connect', () => {
            console.log('Conectado al namespace de administración');
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Desconectado del servidor de admin');
            this.updateConnectionStatus(false);
        });
        
        // Eventos específicos de administración
        this.socket.on('session_created', (data) => {
            this.handleSessionCreated(data);
        });
        
        this.socket.on('session_started', (data) => {
            this.handleSessionStarted(data);
        });
        
        this.socket.on('session_stopped', (data) => {
            this.handleSessionStopped(data);
        });
        
        this.socket.on('participant_joined', (data) => {
            this.handleParticipantJoined(data);
        });
        
        this.socket.on('participant_left', (data) => {
            this.handleParticipantLeft(data);
        });
        
        this.socket.on('quiz_stats_updated', (data) => {
            this.updateQuizStats(data);
        });
        
        this.socket.on('error', (data) => {
            this.showAlert(data.message, 'danger');
        });
    }
    
    bindEvents() {
        // Botón crear sesión
        const createSessionBtn = document.getElementById('create-session-btn');
        if (createSessionBtn) {
            createSessionBtn.addEventListener('click', () => this.createSession());
        }
        
        // Botón iniciar sesión
        const startSessionBtn = document.getElementById('start-session-btn');
        if (startSessionBtn) {
            startSessionBtn.addEventListener('click', () => this.startSession());
        }
        
        // Botón detener sesión
        const stopSessionBtn = document.getElementById('stop-session-btn');
        if (stopSessionBtn) {
            stopSessionBtn.addEventListener('click', () => this.stopSession());
        }
        
        // Botón siguiente pregunta
        const nextQuestionBtn = document.getElementById('next-question-btn');
        if (nextQuestionBtn) {
            nextQuestionBtn.addEventListener('click', () => this.nextQuestion());
        }
        
        // Selector de quiz
        const quizSelector = document.getElementById('quiz-selector');
        if (quizSelector) {
            quizSelector.addEventListener('change', () => this.loadQuizPreview());
        }
        
        // Configuración de tiempo
        const timeConfigInputs = document.querySelectorAll('.time-config');
        timeConfigInputs.forEach(input => {
            input.addEventListener('change', () => this.updateTimeConfig());
        });
        
        // Botones de exportar
        const exportButtons = document.querySelectorAll('.export-btn');
        exportButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const format = e.target.dataset.format;
                this.exportResults(format);
            });
        });
    }
    
    loadInitialData() {
        // Cargar lista de quizzes disponibles
        this.loadAvailableQuizzes();
        
        // Cargar configuración actual
        this.loadCurrentConfig();
        
        // Verificar estado del servidor
        this.checkServerStatus();
    }
    
    loadAvailableQuizzes() {
        fetch('/api/admin/quizzes')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.populateQuizSelector(data.quizzes);
                } else {
                    this.showAlert('Error al cargar quizzes: ' + data.message, 'warning');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.showAlert('Error de conexión al cargar quizzes', 'danger');
            });
    }
    
    populateQuizSelector(quizzes) {
        const selector = document.getElementById('quiz-selector');
        if (!selector) return;
        
        selector.innerHTML = '<option value="">Seleccionar quiz...</option>';
        
        quizzes.forEach(quiz => {
            const option = document.createElement('option');
            option.value = quiz.id;
            option.textContent = `${quiz.title} (${quiz.questions.length} preguntas)`;
            selector.appendChild(option);
        });
    }
    
    loadQuizPreview() {
        const selector = document.getElementById('quiz-selector');
        const quizId = selector.value;
        
        if (!quizId) {
            this.clearQuizPreview();
            return;
        }
        
        fetch(`/api/admin/quiz/${quizId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.displayQuizPreview(data.quiz);
                } else {
                    this.showAlert('Error al cargar vista previa: ' + data.message, 'warning');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.showAlert('Error al cargar vista previa', 'danger');
            });
    }
    
    displayQuizPreview(quiz) {
        const previewContainer = document.getElementById('quiz-preview');
        if (!previewContainer) return;
        
        const html = `
            <div class="quiz-preview-card">
                <h4>${quiz.title}</h4>
                <p class="text-muted">${quiz.description}</p>
                <div class="quiz-info">
                    <div class="info-item">
                        <strong>Preguntas:</strong> ${quiz.questions.length}
                    </div>
                    <div class="info-item">
                        <strong>Tiempo por pregunta:</strong> ${quiz.time_per_question || 30}s
                    </div>
                    <div class="info-item">
                        <strong>Categoría:</strong> ${quiz.category || 'General'}
                    </div>
                    <div class="info-item">
                        <strong>Dificultad:</strong> ${quiz.difficulty || 'Media'}
                    </div>
                </div>
                <div class="questions-preview">
                    <h5>Preguntas:</h5>
                    <div class="questions-list">
                        ${quiz.questions.slice(0, 3).map((q, index) => `
                            <div class="question-preview-item">
                                <strong>${index + 1}.</strong> ${q.text}
                                <small class="text-muted">(${q.options.length} opciones)</small>
                            </div>
                        `).join('')}
                        ${quiz.questions.length > 3 ? `
                            <div class="question-preview-item text-muted">
                                ... y ${quiz.questions.length - 3} preguntas más
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        previewContainer.innerHTML = html;
    }
    
    clearQuizPreview() {
        const previewContainer = document.getElementById('quiz-preview');
        if (previewContainer) {
            previewContainer.innerHTML = '<p class="text-muted">Selecciona un quiz para ver la vista previa</p>';
        }
    }
    
    createSession() {
        const quizSelector = document.getElementById('quiz-selector');
        const sessionNameInput = document.getElementById('session-name');
        
        if (!quizSelector.value) {
            this.showAlert('Por favor selecciona un quiz', 'warning');
            return;
        }
        
        const sessionData = {
            quiz_id: quizSelector.value,
            session_name: sessionNameInput.value || 'Sesión de Quiz',
            settings: this.getSessionSettings()
        };
        
        this.socket.emit('create_session', sessionData);
        this.showLoading('create-session-btn');
    }
    
    startSession() {
        if (!this.currentSession) {
            this.showAlert('No hay sesión activa para iniciar', 'warning');
            return;
        }
        
        this.socket.emit('start_session', {
            session_id: this.currentSession.id
        });
        
        this.showLoading('start-session-btn');
    }
    
    stopSession() {
        if (!this.currentSession) {
            this.showAlert('No hay sesión activa para detener', 'warning');
            return;
        }
        
        this.socket.emit('stop_session', {
            session_id: this.currentSession.id
        });
        
        this.showLoading('stop-session-btn');
    }
    
    nextQuestion() {
        if (!this.currentSession || this.sessionStatus !== 'active') {
            this.showAlert('No hay sesión activa', 'warning');
            return;
        }
        
        this.socket.emit('next_question', {
            session_id: this.currentSession.id
        });
    }
    
    getSessionSettings() {
        return {
            time_per_question: parseInt(document.getElementById('time-per-question')?.value) || 30,
            show_correct_answer: document.getElementById('show-correct-answer')?.checked || true,
            allow_late_join: document.getElementById('allow-late-join')?.checked || false,
            shuffle_questions: document.getElementById('shuffle-questions')?.checked || false,
            shuffle_answers: document.getElementById('shuffle-answers')?.checked || false
        };
    }
    
    handleSessionCreated(data) {
        console.log('Sesión creada:', data);
        this.currentSession = data.session;
        this.sessionStatus = 'created';
        
        this.updateSessionDisplay();
        this.hideLoading('create-session-btn');
        this.showAlert(`Sesión creada: ${data.session.id}`, 'success');
    }
    
    handleSessionStarted(data) {
        console.log('Sesión iniciada:', data);
        this.sessionStatus = 'active';
        
        this.updateSessionDisplay();
        this.hideLoading('start-session-btn');
        this.showAlert('Sesión iniciada correctamente', 'success');
    }
    
    handleSessionStopped(data) {
        console.log('Sesión detenida:', data);
        this.sessionStatus = 'stopped';
        
        this.updateSessionDisplay();
        this.hideLoading('stop-session-btn');
        this.showAlert('Sesión detenida', 'info');
    }
    
    handleParticipantJoined(data) {
        console.log('Participante unido:', data);
        this.participants = data.participants;
        this.updateParticipantsDisplay();
        this.showAlert(`${data.participant.name} se unió a la sesión`, 'info');
    }
    
    handleParticipantLeft(data) {
        console.log('Participante salió:', data);
        this.participants = data.participants;
        this.updateParticipantsDisplay();
        this.showAlert(`${data.participant.name} salió de la sesión`, 'warning');
    }
    
    updateSessionDisplay() {
        const sessionInfo = document.getElementById('session-info');
        const sessionControls = document.getElementById('session-controls');
        
        if (!this.currentSession) {
            if (sessionInfo) {
                sessionInfo.innerHTML = '<p class="text-muted">No hay sesión activa</p>';
            }
            return;
        }
        
        if (sessionInfo) {
            sessionInfo.innerHTML = `
                <div class="session-card">
                    <h5>Sesión Activa</h5>
                    <div class="session-details">
                        <div><strong>ID:</strong> ${this.currentSession.id}</div>
                        <div><strong>Quiz:</strong> ${this.currentSession.quiz_title}</div>
                        <div><strong>Estado:</strong> 
                            <span class="badge bg-${this.getStatusColor()}">${this.getStatusText()}</span>
                        </div>
                        <div><strong>Participantes:</strong> ${this.participants.length}</div>
                    </div>
                </div>
            `;
        }
        
        // Actualizar botones de control
        this.updateControlButtons();
    }
    
    updateControlButtons() {
        const createBtn = document.getElementById('create-session-btn');
        const startBtn = document.getElementById('start-session-btn');
        const stopBtn = document.getElementById('stop-session-btn');
        const nextBtn = document.getElementById('next-question-btn');
        
        if (createBtn) createBtn.disabled = this.sessionStatus !== 'stopped';
        if (startBtn) startBtn.disabled = this.sessionStatus !== 'created';
        if (stopBtn) stopBtn.disabled = this.sessionStatus === 'stopped';
        if (nextBtn) nextBtn.disabled = this.sessionStatus !== 'active';
    }
    
    updateParticipantsDisplay() {
        const participantsContainer = document.getElementById('participants-display');
        if (!participantsContainer) return;
        
        if (this.participants.length === 0) {
            participantsContainer.innerHTML = '<p class="text-muted">No hay participantes conectados</p>';
            return;
        }
        
        const html = `
            <div class="participants-grid">
                ${this.participants.map(participant => `
                    <div class="participant-card">
                        <div class="participant-info">
                            <i class="fas fa-user"></i>
                            <span class="participant-name">${participant.name}</span>
                        </div>
                        <div class="participant-stats">
                            <small>Puntos: ${participant.score || 0}</small>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        participantsContainer.innerHTML = html;
    }
    
    updateQuizStats(data) {
        const statsContainer = document.getElementById('quiz-stats');
        if (!statsContainer) return;
        
        const html = `
            <div class="stats-grid">
                <div class="stat-card">
                    <h6>Pregunta Actual</h6>
                    <div class="stat-value">${data.current_question || 'N/A'}</div>
                </div>
                <div class="stat-card">
                    <h6>Respuestas Recibidas</h6>
                    <div class="stat-value">${data.answers_received || 0}</div>
                </div>
                <div class="stat-card">
                    <h6>Tiempo Restante</h6>
                    <div class="stat-value">${data.time_remaining || 0}s</div>
                </div>
                <div class="stat-card">
                    <h6>Participantes Activos</h6>
                    <div class="stat-value">${this.participants.length}</div>
                </div>
            </div>
        `;
        
        statsContainer.innerHTML = html;
    }
    
    exportResults(format) {
        if (!this.currentSession) {
            this.showAlert('No hay sesión para exportar', 'warning');
            return;
        }
        
        const url = `/api/admin/export/${this.currentSession.id}?format=${format}`;
        
        // Crear enlace de descarga
        const link = document.createElement('a');
        link.href = url;
        link.download = `quiz-results-${this.currentSession.id}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showAlert(`Exportando resultados en formato ${format.toUpperCase()}`, 'info');
    }
    
    loadCurrentConfig() {
        fetch('/api/admin/config')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.populateConfigForm(data.config);
                }
            })
            .catch(error => {
                console.error('Error al cargar configuración:', error);
            });
    }
    
    populateConfigForm(config) {
        // Poblar formulario de configuración
        Object.keys(config).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = config[key];
                } else {
                    element.value = config[key];
                }
            }
        });
    }
    
    updateTimeConfig() {
        const config = this.getSessionSettings();
        
        fetch('/api/admin/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showAlert('Configuración actualizada', 'success');
            } else {
                this.showAlert('Error al actualizar configuración', 'warning');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    
    checkServerStatus() {
        fetch('/api/admin/status')
            .then(response => response.json())
            .then(data => {
                this.updateServerStatus(data.status);
            })
            .catch(error => {
                this.updateServerStatus('error');
            });
    }
    
    updateServerStatus(status) {
        const statusElement = document.getElementById('server-status');
        if (!statusElement) return;
        
        const statusMap = {
            'running': { text: 'Funcionando', class: 'bg-success' },
            'stopped': { text: 'Detenido', class: 'bg-danger' },
            'error': { text: 'Error', class: 'bg-warning' }
        };
        
        const statusInfo = statusMap[status] || statusMap['error'];
        statusElement.innerHTML = `<span class="badge ${statusInfo.class}">${statusInfo.text}</span>`;
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (!statusElement) return;
        
        statusElement.className = connected ? 'text-success' : 'text-danger';
        statusElement.innerHTML = connected ? 
            '<i class="fas fa-circle"></i> Conectado' : 
            '<i class="fas fa-circle"></i> Desconectado';
    }
    
    getStatusColor() {
        const colorMap = {
            'created': 'warning',
            'active': 'success',
            'stopped': 'secondary'
        };
        return colorMap[this.sessionStatus] || 'secondary';
    }
    
    getStatusText() {
        const textMap = {
            'created': 'Creada',
            'active': 'Activa',
            'stopped': 'Detenida'
        };
        return textMap[this.sessionStatus] || 'Desconocido';
    }
    
    // Métodos de utilidad
    showAlert(message, type = 'info') {
        if (typeof window.showAlert === 'function') {
            window.showAlert(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    showLoading(buttonId) {
        const button = document.getElementById(buttonId);
        if (button && typeof window.showLoading === 'function') {
            window.showLoading(button, true);
        }
    }
    
    hideLoading(buttonId) {
        const button = document.getElementById(buttonId);
        if (button && typeof window.showLoading === 'function') {
            window.showLoading(button, false);
        }
    }
}

// Inicializar interfaz de administración
document.addEventListener('DOMContentLoaded', () => {
    if (document.body.classList.contains('admin-page')) {
        window.adminInterface = new AdminInterface();
    }
});
