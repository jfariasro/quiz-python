/*
 * Utilidades para manejo de formularios en la plataforma
 * Validación, envío y formateo de datos
 */

class FormHandler {
    constructor() {
        this.forms = new Map();
        this.validators = new Map();
        this.initializeValidators();
        this.bindEvents();
    }
    
    initializeValidators() {
        // Validadores básicos
        this.validators.set('required', (value) => {
            return value && value.trim().length > 0;
        });
        
        this.validators.set('email', (value) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(value);
        });
        
        this.validators.set('minLength', (value, minLength) => {
            return value && value.length >= minLength;
        });
        
        this.validators.set('maxLength', (value, maxLength) => {
            return !value || value.length <= maxLength;
        });
        
        this.validators.set('numeric', (value) => {
            return !isNaN(value) && !isNaN(parseFloat(value));
        });
        
        this.validators.set('sessionId', (value) => {
            // ID de sesión debe ser alfanumérico de 6 caracteres
            const sessionIdRegex = /^[A-Z0-9]{6}$/;
            return sessionIdRegex.test(value);
        });
        
        this.validators.set('participantName', (value) => {
            // Nombre de participante: solo letras, números y espacios, 2-20 caracteres
            const nameRegex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]{2,20}$/;
            return nameRegex.test(value);
        });
    }
    
    bindEvents() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.classList.contains('validate-form')) {
                e.preventDefault();
                this.handleFormSubmit(form);
            }
        });
        
        // Validación en tiempo real
        document.addEventListener('input', (e) => {
            const input = e.target;
            if (input.hasAttribute('data-validate')) {
                this.validateField(input);
            }
        });
        
        // Formateo automático
        document.addEventListener('input', (e) => {
            const input = e.target;
            if (input.hasAttribute('data-format')) {
                this.formatField(input);
            }
        });
    }
    
    handleFormSubmit(form) {
        const formId = form.id || 'form-' + Date.now();
        
        // Validar todos los campos
        const isValid = this.validateForm(form);
        
        if (!isValid) {
            this.showFormError(form, 'Por favor, corrige los errores en el formulario');
            return;
        }
        
        // Obtener datos del formulario
        const formData = this.getFormData(form);
        
        // Mostrar loading
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            this.showLoading(submitButton);
        }
        
        // Determinar el tipo de formulario y procesar
        this.processForm(form, formData);
    }
    
    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('[data-validate]');
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    validateField(input) {
        const rules = input.getAttribute('data-validate').split('|');
        const value = input.value.trim();
        let isValid = true;
        let errorMessage = '';
        
        for (const rule of rules) {
            const [validatorName, ...params] = rule.split(':');
            const validator = this.validators.get(validatorName);
            
            if (validator) {
                const result = validator(value, ...params);
                if (!result) {
                    isValid = false;
                    errorMessage = this.getErrorMessage(validatorName, input, params);
                    break;
                }
            }
        }
        
        this.showFieldValidation(input, isValid, errorMessage);
        return isValid;
    }
    
    getErrorMessage(validatorName, input, params) {
        const fieldName = input.getAttribute('data-field-name') || input.name || 'Este campo';
        
        const messages = {
            'required': `${fieldName} es obligatorio`,
            'email': `${fieldName} debe ser un email válido`,
            'minLength': `${fieldName} debe tener al menos ${params[0]} caracteres`,
            'maxLength': `${fieldName} no puede tener más de ${params[0]} caracteres`,
            'numeric': `${fieldName} debe ser un número válido`,
            'sessionId': `${fieldName} debe tener 6 caracteres alfanuméricos`,
            'participantName': `${fieldName} debe tener entre 2 y 20 caracteres (solo letras, números y espacios)`
        };
        
        return messages[validatorName] || `${fieldName} no es válido`;
    }
    
    showFieldValidation(input, isValid, errorMessage) {
        // Remover clases anteriores
        input.classList.remove('is-valid', 'is-invalid');
        
        // Buscar o crear elemento de error
        let errorElement = input.parentNode.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            input.parentNode.appendChild(errorElement);
        }
        
        if (isValid) {
            input.classList.add('is-valid');
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        } else {
            input.classList.add('is-invalid');
            errorElement.textContent = errorMessage;
            errorElement.style.display = 'block';
        }
    }
    
    formatField(input) {
        const formatType = input.getAttribute('data-format');
        let value = input.value;
        
        switch (formatType) {
            case 'uppercase':
                input.value = value.toUpperCase();
                break;
            case 'lowercase':
                input.value = value.toLowerCase();
                break;
            case 'capitalize':
                input.value = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
                break;
            case 'session-id':
                // Formatear como ID de sesión: solo mayúsculas y números
                input.value = value.replace(/[^A-Z0-9]/g, '').substring(0, 6);
                break;
            case 'participant-name':
                // Formatear nombre: primera letra de cada palabra en mayúscula
                input.value = value.replace(/\b\w/g, l => l.toUpperCase()).substring(0, 20);
                break;
        }
    }
    
    getFormData(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }
    
    processForm(form, data) {
        const formType = form.getAttribute('data-form-type');
        
        switch (formType) {
            case 'join-session':
                this.processJoinSession(form, data);
                break;
            case 'create-quiz':
                this.processCreateQuiz(form, data);
                break;
            case 'settings':
                this.processSettings(form, data);
                break;
            default:
                this.processGenericForm(form, data);
        }
    }
    
    processJoinSession(form, data) {
        // Validaciones específicas para unirse a sesión
        if (!data.sessionId || !data.participantName) {
            this.showFormError(form, 'Por favor, completa todos los campos');
            this.hideLoading(form);
            return;
        }
        
        // Emitir evento para que el QuizClient lo maneje
        if (window.quizClient) {
            window.quizClient.joinSession();
        } else {
            // Fallback: enviar por fetch
            this.submitToServer(form, '/api/join-session', data);
        }
    }
    
    processCreateQuiz(form, data) {
        // Procesar creación de quiz
        this.submitToServer(form, '/api/admin/create-quiz', data);
    }
    
    processSettings(form, data) {
        // Procesar configuración
        this.submitToServer(form, '/api/admin/settings', data);
    }
    
    processGenericForm(form, data) {
        // Procesar formulario genérico
        const actionUrl = form.action || '/api/form-submit';
        this.submitToServer(form, actionUrl, data);
    }
    
    submitToServer(form, url, data) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            this.hideLoading(form);
            
            if (result.success) {
                this.showFormSuccess(form, result.message || 'Operación exitosa');
                
                // Redirigir si es necesario
                if (result.redirect) {
                    setTimeout(() => {
                        window.location.href = result.redirect;
                    }, 1500);
                }
                
                // Resetear formulario si es necesario
                if (result.reset !== false) {
                    form.reset();
                    this.clearValidation(form);
                }
            } else {
                this.showFormError(form, result.message || 'Error en el servidor');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.hideLoading(form);
            this.showFormError(form, 'Error de conexión. Inténtalo de nuevo.');
        });
    }
    
    showFormError(form, message) {
        let alertContainer = form.querySelector('.form-alerts');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.className = 'form-alerts';
            form.insertBefore(alertContainer, form.firstChild);
        }
        
        alertContainer.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }
    
    showFormSuccess(form, message) {
        let alertContainer = form.querySelector('.form-alerts');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.className = 'form-alerts';
            form.insertBefore(alertContainer, form.firstChild);
        }
        
        alertContainer.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <i class="fas fa-check-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }
    
    clearValidation(form) {
        const inputs = form.querySelectorAll('.is-valid, .is-invalid');
        inputs.forEach(input => {
            input.classList.remove('is-valid', 'is-invalid');
        });
        
        const errorElements = form.querySelectorAll('.invalid-feedback');
        errorElements.forEach(element => {
            element.style.display = 'none';
        });
        
        const alertContainer = form.querySelector('.form-alerts');
        if (alertContainer) {
            alertContainer.innerHTML = '';
        }
    }
    
    showLoading(button) {
        if (button) {
            button.disabled = true;
            button.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                Cargando...
            `;
        }
    }
    
    hideLoading(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = false;
            
            // Restaurar texto original
            const originalText = submitButton.getAttribute('data-original-text');
            if (originalText) {
                submitButton.innerHTML = originalText;
            } else {
                // Texto por defecto según el tipo de formulario
                const formType = form.getAttribute('data-form-type');
                const defaultTexts = {
                    'join-session': 'Unirse',
                    'create-quiz': 'Crear Quiz',
                    'settings': 'Guardar Configuración'
                };
                submitButton.innerHTML = defaultTexts[formType] || 'Enviar';
            }
        }
    }
    
    // Métodos públicos para uso externo
    static validateSessionId(sessionId) {
        return /^[A-Z0-9]{6}$/.test(sessionId);
    }
    
    static validateParticipantName(name) {
        return /^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]{2,20}$/.test(name);
    }
    
    static formatSessionId(value) {
        return value.replace(/[^A-Z0-9]/g, '').substring(0, 6);
    }
    
    static formatParticipantName(value) {
        return value.replace(/\b\w/g, l => l.toUpperCase()).substring(0, 20);
    }
}

// Inicializar manejador de formularios
document.addEventListener('DOMContentLoaded', () => {
    window.formHandler = new FormHandler();
    
    // Agregar texto original a botones de envío para restaurar después del loading
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.setAttribute('data-original-text', button.innerHTML);
    });
});

// Utilidades globales para formularios
window.FormUtils = {
    validateSessionId: FormHandler.validateSessionId,
    validateParticipantName: FormHandler.validateParticipantName,
    formatSessionId: FormHandler.formatSessionId,
    formatParticipantName: FormHandler.formatParticipantName
};
