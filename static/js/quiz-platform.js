/**
 * JavaScript principal para la Plataforma de Quizzes
 * Contiene funcionalidades comunes y utilidades para todas las páginas
 */

// ===== CONFIGURACIÓN GLOBAL =====
const QuizPlatform = {
    // Configuración
    config: {
        socketRetryAttempts: 5,
        socketRetryDelay: 3000,
        alertAutoHideDelay: 5000,
        animationDuration: 300
    },
    
    // Estado global
    state: {
        socket: null,
        connected: false,
        participantId: null,
        sessionId: null,
        currentQuestion: null
    },
    
    // Elementos del DOM
    elements: {},
    
    // Callbacks registrados
    callbacks: {
        onConnect: [],
        onDisconnect: [],
        onQuestionStart: [],
        onQuestionEnd: [],
        onStateChange: []
    }
};

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando Plataforma de Quizzes');
    
    // Inicializar componentes básicos
    QuizPlatform.init();
    
    // Configurar eventos globales
    QuizPlatform.setupGlobalEvents();
    
    // Inicializar Socket.IO si está disponible
    if (typeof io !== 'undefined') {
        QuizPlatform.initSocket();
    }
    
    console.log('✅ Plataforma inicializada correctamente');
});

// ===== MÉTODOS PRINCIPALES =====
QuizPlatform.init = function() {
    // Cachear elementos comunes del DOM
    this.cacheElements();
    
    // Configurar componentes interactivos
    this.setupInteractiveComponents();
    
    // Aplicar animaciones iniciales
    this.applyInitialAnimations();
    
    // Configurar accesibilidad
    this.setupAccessibility();
};

QuizPlatform.cacheElements = function() {
    this.elements = {
        body: document.body,
        alerts: document.getElementById('alerts-container') || this.createAlertsContainer(),
        loadingOverlay: document.getElementById('loading-overlay'),
        participantCount: document.getElementById('participantCount'),
        timerElement: document.getElementById('questionTimer'),
        progressBar: document.getElementById('progressBar')
    };
};

QuizPlatform.createAlertsContainer = function() {
    const container = document.createElement('div');
    container.id = 'alerts-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
};

// ===== GESTIÓN DE SOCKET.IO =====
QuizPlatform.initSocket = function() {
    console.log('🔌 Iniciando conexión Socket.IO...');
    
    this.state.socket = io({
        transports: ['websocket', 'polling'],
        timeout: 10000,
        retries: this.config.socketRetryAttempts
    });
    
    this.setupSocketEvents();
};

QuizPlatform.setupSocketEvents = function() {
    const socket = this.state.socket;
    
    // Eventos de conexión
    socket.on('connect', () => {
        console.log('✅ Conectado al servidor');
        this.state.connected = true;
        this.hideConnectionError();
        this.triggerCallbacks('onConnect', { socket });
    });
    
    socket.on('disconnect', (reason) => {
        console.log('❌ Desconectado del servidor:', reason);
        this.state.connected = false;
        this.showConnectionError();
        this.triggerCallbacks('onDisconnect', { reason });
    });
    
    socket.on('connect_error', (error) => {
        console.error('💥 Error de conexión:', error);
        this.showAlert('Error de conexión al servidor', 'danger');
    });
    
    // Eventos específicos del quiz
    socket.on('session_state', (data) => {
        console.log('📊 Estado de sesión actualizado:', data);
        this.updateSessionState(data);
    });
    
    socket.on('participant_joined', (data) => {
        console.log('👤 Nuevo participante:', data);
        this.updateParticipantCount(data.participant_count);
        this.showAlert(`${data.name} se unió al quiz`, 'success');
    });
    
    socket.on('question_started', (data) => {
        console.log('❓ Nueva pregunta iniciada:', data);
        this.triggerCallbacks('onQuestionStart', data);
    });
    
    socket.on('question_results', (data) => {
        console.log('📈 Resultados de pregunta:', data);
        this.triggerCallbacks('onQuestionEnd', data);
    });
    
    socket.on('state_change', (data) => {
        console.log('🔄 Cambio de estado:', data);
        this.triggerCallbacks('onStateChange', data);
    });
    
    socket.on('quiz_finished', (data) => {
        console.log('🏁 Quiz finalizado:', data);
        this.showAlert('¡Quiz finalizado! Mostrando resultados...', 'info');
    });
    
    socket.on('error', (data) => {
        console.error('❌ Error del servidor:', data);
        this.showAlert(data.message || 'Error del servidor', 'danger');
    });
};

// ===== GESTIÓN DE ALERTAS =====
QuizPlatform.showAlert = function(message, type = 'info', autoHide = true) {
    const alertId = 'alert-' + Date.now();
    const alertElement = document.createElement('div');
    
    alertElement.id = alertId;
    alertElement.className = `alert alert-${type} alert-dismissible fade show slide-in-right`;
    alertElement.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas ${this.getAlertIcon(type)} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    this.elements.alerts.appendChild(alertElement);
    
    // Auto-ocultar si está habilitado
    if (autoHide) {
        setTimeout(() => {
            this.hideAlert(alertId);
        }, this.config.alertAutoHideDelay);
    }
    
    return alertId;
};

QuizPlatform.hideAlert = function(alertId) {
    const alertElement = document.getElementById(alertId);
    if (alertElement) {
        alertElement.classList.add('fade-out');
        setTimeout(() => {
            if (alertElement.parentNode) {
                alertElement.parentNode.removeChild(alertElement);
            }
        }, this.config.animationDuration);
    }
};

QuizPlatform.getAlertIcon = function(type) {
    const icons = {
        success: 'fa-check-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle',
        danger: 'fa-times-circle'
    };
    return icons[type] || icons.info;
};

// ===== GESTIÓN DE ESTADO DE CONEXIÓN =====
QuizPlatform.showConnectionError = function() {
    this.showAlert(
        'Conexión perdida. Intentando reconectar...',
        'warning',
        false
    );
};

QuizPlatform.hideConnectionError = function() {
    // Ocultar alertas de conexión existentes
    const connectionAlerts = this.elements.alerts.querySelectorAll('.alert-warning');
    connectionAlerts.forEach(alert => {
        if (alert.textContent.includes('Conexión perdida')) {
            this.hideAlert(alert.id);
        }
    });
};

// ===== ACTUALIZACIÓN DE UI =====
QuizPlatform.updateParticipantCount = function(count) {
    if (this.elements.participantCount) {
        this.elements.participantCount.textContent = count;
        
        // Animación de actualización
        this.elements.participantCount.classList.add('pulse-animation');
        setTimeout(() => {
            this.elements.participantCount.classList.remove('pulse-animation');
        }, 1000);
    }
};

QuizPlatform.updateSessionState = function(data) {
    // Actualizar progreso si hay elementos disponibles
    if (data.current_question !== undefined && data.total_questions) {
        this.updateProgress(data.current_question + 1, data.total_questions);
    }
};

QuizPlatform.updateProgress = function(current, total) {
    if (this.elements.progressBar) {
        const percentage = (current / total) * 100;
        this.elements.progressBar.style.width = `${percentage}%`;
        
        // Actualizar texto de progreso
        const progressText = document.getElementById('currentQuestion');
        if (progressText) {
            progressText.textContent = current;
        }
        
        const totalText = document.getElementById('totalQuestions');
        if (totalText) {
            totalText.textContent = total;
        }
    }
};

// ===== TEMPORIZADOR =====
QuizPlatform.startTimer = function(duration, onTick, onComplete) {
    let timeLeft = duration;
    
    const updateTimer = () => {
        if (this.elements.timerElement) {
            this.elements.timerElement.textContent = timeLeft;
            
            // Cambiar color cuando quede poco tiempo
            if (timeLeft <= 10) {
                this.elements.timerElement.parentElement.classList.add('timer-warning');
            }
            if (timeLeft <= 5) {
                this.elements.timerElement.parentElement.classList.add('timer-danger');
            }
        }
        
        if (onTick) onTick(timeLeft);
        
        if (timeLeft <= 0) {
            if (onComplete) onComplete();
            return;
        }
        
        timeLeft--;
        setTimeout(updateTimer, 1000);
    };
    
    updateTimer();
};

// ===== LOADING Y SPINNERS =====
QuizPlatform.showLoading = function(element, text = 'Cargando...') {
    if (element) {
        element.disabled = true;
        element.innerHTML = `
            <span class="loading-spinner me-2"></span>
            ${text}
        `;
    }
};

QuizPlatform.hideLoading = function(element, originalText) {
    if (element) {
        element.disabled = false;
        element.innerHTML = originalText;
    }
};

QuizPlatform.showGlobalLoading = function() {
    if (!this.elements.loadingOverlay) {
        this.elements.loadingOverlay = document.createElement('div');
        this.elements.loadingOverlay.id = 'loading-overlay';
        this.elements.loadingOverlay.className = 'loading-overlay';
        this.elements.loadingOverlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner-large"></div>
                <p>Cargando...</p>
            </div>
        `;
        document.body.appendChild(this.elements.loadingOverlay);
    }
    
    this.elements.loadingOverlay.style.display = 'flex';
};

QuizPlatform.hideGlobalLoading = function() {
    if (this.elements.loadingOverlay) {
        this.elements.loadingOverlay.style.display = 'none';
    }
};

// ===== ANIMACIONES =====
QuizPlatform.applyInitialAnimations = function() {
    // Animar elementos al cargar
    const animatedElements = document.querySelectorAll('[data-animate]');
    
    animatedElements.forEach((element, index) => {
        const animationType = element.getAttribute('data-animate');
        const delay = index * 100; // Escalonar animaciones
        
        setTimeout(() => {
            element.classList.add(animationType);
        }, delay);
    });
};

QuizPlatform.animateElement = function(element, animation) {
    if (element) {
        element.classList.add(animation);
        
        // Limpiar clase después de la animación
        setTimeout(() => {
            element.classList.remove(animation);
        }, this.config.animationDuration * 2);
    }
};

// ===== UTILIDADES =====
QuizPlatform.formatTime = function(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

QuizPlatform.debounce = function(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

QuizPlatform.throttle = function(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

// ===== GESTIÓN DE CALLBACKS =====
QuizPlatform.onConnect = function(callback) {
    this.callbacks.onConnect.push(callback);
};

QuizPlatform.onDisconnect = function(callback) {
    this.callbacks.onDisconnect.push(callback);
};

QuizPlatform.onQuestionStart = function(callback) {
    this.callbacks.onQuestionStart.push(callback);
};

QuizPlatform.onQuestionEnd = function(callback) {
    this.callbacks.onQuestionEnd.push(callback);
};

QuizPlatform.onStateChange = function(callback) {
    this.callbacks.onStateChange.push(callback);
};

QuizPlatform.triggerCallbacks = function(event, data) {
    this.callbacks[event].forEach(callback => {
        try {
            callback(data);
        } catch (error) {
            console.error(`Error in ${event} callback:`, error);
        }
    });
};

// ===== EVENTOS GLOBALES =====
QuizPlatform.setupGlobalEvents = function() {
    // Detectar pérdida de conexión a internet
    window.addEventListener('online', () => {
        this.showAlert('Conexión a internet restaurada', 'success');
    });
    
    window.addEventListener('offline', () => {
        this.showAlert('Sin conexión a internet', 'warning', false);
    });
    
    // Prevenir envío accidental de formularios
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.target.tagName !== 'BUTTON' && e.target.type !== 'submit') {
            // Permitir Enter solo en elementos específicos
            if (!e.target.matches('input[type="text"], input[type="email"], textarea')) {
                e.preventDefault();
            }
        }
    });
    
    // Gestión de visibilidad de página
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            console.log('📱 Página oculta');
        } else {
            console.log('👁️ Página visible');
            // Reconectar socket si es necesario
            if (this.state.socket && !this.state.connected) {
                this.state.socket.connect();
            }
        }
    });
};

// ===== COMPONENTES INTERACTIVOS =====
QuizPlatform.setupInteractiveComponents = function() {
    // Botones de opciones de quiz
    this.setupQuizOptions();
    
    // Formularios
    this.setupForms();
    
    // Elementos con efectos hover
    this.setupHoverEffects();
};

QuizPlatform.setupQuizOptions = function() {
    const optionButtons = document.querySelectorAll('.option-button');
    
    optionButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            // Remover selección anterior
            optionButtons.forEach(btn => btn.classList.remove('selected'));
            
            // Seleccionar opción actual
            button.classList.add('selected');
            
            // Efecto visual
            this.animateElement(button, 'pulse-animation');
            
            // Emitir evento personalizado
            const event = new CustomEvent('optionSelected', {
                detail: {
                    button: button,
                    value: button.getAttribute('data-value'),
                    text: button.textContent.trim()
                }
            });
            document.dispatchEvent(event);
        });
    });
};

QuizPlatform.setupForms = function() {
    // Validación en tiempo real
    const inputs = document.querySelectorAll('input[required], textarea[required]');
    
    inputs.forEach(input => {
        input.addEventListener('input', this.debounce(() => {
            this.validateInput(input);
        }, 300));
        
        input.addEventListener('blur', () => {
            this.validateInput(input);
        });
    });
};

QuizPlatform.validateInput = function(input) {
    const isValid = input.checkValidity();
    
    if (isValid) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-valid');
    }
    
    return isValid;
};

QuizPlatform.setupHoverEffects = function() {
    // Efectos de hover suaves para elementos interactivos
    const interactiveElements = document.querySelectorAll('.btn, .card, .option-button');
    
    interactiveElements.forEach(element => {
        element.addEventListener('mouseenter', () => {
            element.classList.add('interactive-element');
        });
        
        element.addEventListener('mouseleave', () => {
            element.classList.remove('interactive-element');
        });
    });
};

// ===== ACCESIBILIDAD =====
QuizPlatform.setupAccessibility = function() {
    // Navegación por teclado para opciones de quiz
    const optionButtons = document.querySelectorAll('.option-button');
    
    optionButtons.forEach((button, index) => {
        button.setAttribute('tabindex', '0');
        
        button.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    button.click();
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    const nextButton = optionButtons[index + 1];
                    if (nextButton) nextButton.focus();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    const prevButton = optionButtons[index - 1];
                    if (prevButton) prevButton.focus();
                    break;
            }
        });
    });
    
    // Anunciar cambios importantes a lectores de pantalla
    this.setupScreenReaderAnnouncements();
};

QuizPlatform.setupScreenReaderAnnouncements = function() {
    // Crear elemento para anuncios
    const announcer = document.createElement('div');
    announcer.setAttribute('aria-live', 'polite');
    announcer.setAttribute('aria-atomic', 'true');
    announcer.className = 'sr-only';
    announcer.id = 'screen-reader-announcer';
    document.body.appendChild(announcer);
    
    this.elements.announcer = announcer;
};

QuizPlatform.announceToScreenReader = function(message) {
    if (this.elements.announcer) {
        this.elements.announcer.textContent = message;
        
        // Limpiar después de un momento
        setTimeout(() => {
            this.elements.announcer.textContent = '';
        }, 1000);
    }
};

// ===== FUNCIONES DE UTILIDAD ESPECÍFICAS DEL QUIZ =====
QuizPlatform.joinSession = function(sessionId, participantId) {
    if (this.state.socket) {
        this.state.sessionId = sessionId;
        this.state.participantId = participantId;
        
        this.state.socket.emit('join_session', {
            session_id: sessionId,
            participant_id: participantId
        });
        
        console.log(`📡 Uniéndose a sesión: ${sessionId}`);
    }
};

QuizPlatform.submitAnswer = function(answer) {
    if (this.state.socket && this.state.sessionId && this.state.participantId) {
        this.state.socket.emit('submit_answer', {
            session_id: this.state.sessionId,
            participant_id: this.state.participantId,
            answer: answer
        });
        
        console.log(`📝 Respuesta enviada: ${answer}`);
        this.announceToScreenReader('Respuesta enviada correctamente');
    }
};

// ===== EXPORTAR PARA USO GLOBAL =====
window.QuizPlatform = QuizPlatform;

// Alias para funciones comunes
window.showAlert = QuizPlatform.showAlert.bind(QuizPlatform);
window.showLoading = QuizPlatform.showLoading.bind(QuizPlatform);
window.hideLoading = QuizPlatform.hideLoading.bind(QuizPlatform);

console.log('🎯 Quiz Platform JavaScript cargado correctamente');
