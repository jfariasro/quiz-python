/*
 * Utilidades generales para la plataforma de quizzes
 * Funciones helper y utilidades comunes
 */

// Namespace para utilidades
window.QuizUtils = {
    
    // ===== UTILIDADES DE FORMATO =====
    
    /**
     * Formatear tiempo en formato MM:SS
     */
    formatTime: function(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    },
    
    /**
     * Formatear número con separadores de miles
     */
    formatNumber: function(number) {
        return number.toLocaleString('es-ES');
    },
    
    /**
     * Formatear fecha en español
     */
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    /**
     * Formatear duración en texto legible
     */
    formatDuration: function(seconds) {
        if (seconds < 60) {
            return `${seconds} segundo${seconds !== 1 ? 's' : ''}`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            return `${minutes} minuto${minutes !== 1 ? 's' : ''}`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }
    },
    
    // ===== UTILIDADES DE VALIDACIÓN =====
    
    /**
     * Validar código de sesión
     */
    validateSessionCode: function(code) {
        return /^[A-Z0-9]{6}$/.test(code);
    },
    
    /**
     * Validar nombre de participante
     */
    validateParticipantName: function(name) {
        return /^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]{2,20}$/.test(name);
    },
    
    /**
     * Validar email
     */
    validateEmail: function(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },
    
    // ===== UTILIDADES DE ALMACENAMIENTO =====
    
    /**
     * Guardar en localStorage con manejo de errores
     */
    saveToStorage: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Error guardando en localStorage:', error);
            return false;
        }
    },
    
    /**
     * Cargar desde localStorage con manejo de errores
     */
    loadFromStorage: function(key, defaultValue = null) {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : defaultValue;
        } catch (error) {
            console.error('Error cargando desde localStorage:', error);
            return defaultValue;
        }
    },
    
    /**
     * Eliminar de localStorage
     */
    removeFromStorage: function(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Error eliminando de localStorage:', error);
            return false;
        }
    },
    
    // ===== UTILIDADES DE DOM =====
    
    /**
     * Crear elemento con clases y atributos
     */
    createElement: function(tag, classes = [], attributes = {}, content = '') {
        const element = document.createElement(tag);
        
        if (classes.length > 0) {
            element.classList.add(...classes);
        }
        
        Object.entries(attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });
        
        if (content) {
            element.innerHTML = content;
        }
        
        return element;
    },
    
    /**
     * Mostrar/ocultar elemento con animación
     */
    toggleElement: function(element, show, animationClass = 'fade-in') {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (!element) return;
        
        if (show) {
            element.style.display = 'block';
            element.classList.add(animationClass);
        } else {
            element.classList.remove(animationClass);
            setTimeout(() => {
                element.style.display = 'none';
            }, 300);
        }
    },
    
    /**
     * Animar elemento con una clase temporal
     */
    animateElement: function(element, animationClass, duration = 1000) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (!element) return;
        
        element.classList.add(animationClass);
        
        setTimeout(() => {
            element.classList.remove(animationClass);
        }, duration);
    },
    
    // ===== UTILIDADES DE AUDIO =====
    
    /**
     * Reproducir sonido de notificación
     */
    playNotificationSound: function() {
        // Crear contexto de audio si no existe
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        // Crear un tono simple
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.3);
    },
    
    /**
     * Reproducir sonido de éxito
     */
    playSuccessSound: function() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        // Acorde de éxito (C-E-G)
        const frequencies = [523.25, 659.25, 783.99];
        
        frequencies.forEach((freq, index) => {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.frequency.setValueAtTime(freq, this.audioContext.currentTime);
            gainNode.gain.setValueAtTime(0.2, this.audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.5);
            
            oscillator.start(this.audioContext.currentTime + index * 0.1);
            oscillator.stop(this.audioContext.currentTime + 0.5 + index * 0.1);
        });
    },
    
    /**
     * Reproducir sonido de error
     */
    playErrorSound: function() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(300, this.audioContext.currentTime);
        oscillator.frequency.setValueAtTime(200, this.audioContext.currentTime + 0.2);
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.4);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.4);
    },
    
    // ===== UTILIDADES DE COPIA =====
    
    /**
     * Copiar texto al portapapeles
     */
    copyToClipboard: function(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback para navegadores más antiguos
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.opacity = '0';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                document.execCommand('copy');
                document.body.removeChild(textArea);
                return Promise.resolve();
            } catch (error) {
                document.body.removeChild(textArea);
                return Promise.reject(error);
            }
        }
    },
    
    // ===== UTILIDADES DE DEBOUNCE/THROTTLE =====
    
    /**
     * Debounce - retrasar ejecución hasta que pasen X ms sin más llamadas
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Throttle - limitar ejecución a una vez cada X ms
     */
    throttle: function(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // ===== UTILIDADES DE CONEXIÓN =====
    
    /**
     * Verificar conectividad
     */
    checkConnectivity: function() {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = '/static/images/ping.png?' + Math.random();
        });
    },
    
    /**
     * Obtener información de la conexión
     */
    getConnectionInfo: function() {
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        
        if (connection) {
            return {
                effectiveType: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt,
                saveData: connection.saveData
            };
        }
        
        return null;
    },
    
    // ===== UTILIDADES DE RENDIMIENTO =====
    
    /**
     * Medir tiempo de ejecución
     */
    measurePerformance: function(name, func) {
        const start = performance.now();
        const result = func();
        const end = performance.now();
        console.log(`${name} tomó ${end - start} millisegundos`);
        return result;
    },
    
    /**
     * Lazy loading de imágenes
     */
    lazyLoadImages: function() {
        const images = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    },
    
    // ===== UTILIDADES DE ACCESIBILIDAD =====
    
    /**
     * Establecer foco en elemento
     */
    setFocus: function(element, delay = 0) {
        setTimeout(() => {
            if (typeof element === 'string') {
                element = document.getElementById(element);
            }
            if (element && element.focus) {
                element.focus();
            }
        }, delay);
    },
    
    /**
     * Anunciar mensaje para lectores de pantalla
     */
    announceMessage: function(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.style.position = 'absolute';
        announcement.style.left = '-10000px';
        announcement.style.width = '1px';
        announcement.style.height = '1px';
        announcement.style.overflow = 'hidden';
        
        document.body.appendChild(announcement);
        announcement.textContent = message;
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
};

// Inicializar utilidades cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Activar lazy loading de imágenes
    QuizUtils.lazyLoadImages();
    
    // Configurar manejo de errores global
    window.addEventListener('error', function(event) {
        console.error('Error global:', event.error);
    });
    
    // Configurar manejo de promesas rechazadas
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Promesa rechazada:', event.reason);
    });
});

// Hacer disponible globalmente
window.Utils = window.QuizUtils;
