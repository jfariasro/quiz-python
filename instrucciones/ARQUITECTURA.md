# 🏗️ ARQUITECTURA TÉCNICA - PLATAFORMA DE QUIZZES

## 📐 VISIÓN GENERAL DE LA ARQUITECTURA

### 🎯 PRINCIPIOS DE DISEÑO
- **Simplicidad**: Arquitectura fácil de entender y mantener
- **Modularidad**: Componentes independientes y reutilizables
- **Escalabilidad Local**: Optimizado para red local con múltiples participantes
- **Mantenibilidad**: Código organizado y bien documentado
- **Performance**: Respuesta rápida en tiempo real

---

## 🧩 COMPONENTES PRINCIPALES

### 1. 🖥️ APLICACIÓN DE ADMINISTRACIÓN (Tkinter)

#### 📋 Responsabilidades
- Interface gráfica para gestión de quizzes
- Control del servidor web
- Monitoreo de sesiones en vivo
- Visualización de estadísticas

#### 🔧 Tecnologías
```python
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk  # UI moderna
```

#### 📁 Estructura de Módulos
```
admin/
├── main_window.py          # Ventana principal
├── quiz_creator.py         # Formulario de creación
├── quiz_manager.py         # Gestión de quizzes
├── session_controller.py   # Control de sesiones
├── history_viewer.py       # Visor de historial
├── settings_window.py      # Configuraciones
└── components/             # Componentes reutilizables
    ├── quiz_list.py       # Lista de quizzes
    ├── participant_panel.py # Panel participantes
    └── stats_charts.py    # Gráficos estadísticas
```

### 2. 🌐 SERVIDOR WEB (Flask + SocketIO)

#### 📋 Responsabilidades
- Servir páginas web a participantes
- API REST para operaciones CRUD
- WebSockets para comunicación tiempo real
- Gestión de sesiones de juego

#### 🔧 Tecnologías
```python
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import eventlet  # Para mejor performance con WebSockets
```

#### 📁 Estructura de Módulos
```
web/
├── app.py                  # Aplicación Flask principal
├── routes.py              # Rutas HTTP
├── socketio_events.py     # Eventos WebSocket
├── api/                   # API REST
│   ├── quiz_api.py       # Endpoints de quizzes
│   ├── session_api.py    # Endpoints de sesiones
│   └── participant_api.py # Endpoints participantes
└── middleware/            # Middlewares
    ├── cors.py           # Configuración CORS
    └── error_handler.py  # Manejo de errores
```

### 3. 💾 SISTEMA DE ARCHIVOS

#### 📋 Responsabilidades
- Almacenamiento persistente de datos
- Operaciones CRUD sobre archivos JSON
- Backup y recuperación de datos
- Validación de integridad

#### 🔧 Tecnologías
```python
import json
import os
from datetime import datetime
import shutil  # Para backups
```

#### 📁 Estructura de Datos
```
data/
├── quizzes/               # Definiciones de quizzes
│   ├── quiz_001.json
│   ├── quiz_002.json
│   └── ...
├── sessions/              # Sesiones activas
│   ├── session_active.json
│   └── session_backup.json
├── history/               # Historial de partidas
│   ├── 2025-06-26/       # Por fecha
│   │   ├── game_001.json
│   │   └── game_002.json
│   └── ...
└── config/                # Configuraciones
    ├── app_config.json
    └── network_config.json
```

---

## 🔄 FLUJO DE DATOS

### 📊 DIAGRAMA DE ARQUITECTURA
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TKINTER APP   │    │   FLASK SERVER  │    │  PARTICIPANT    │
│  (Administrador)│    │  (Coordinador)  │    │  (Navegador)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ 1. Crear Quiz         │                       │
         ├──────────────────────▶│                       │
         │                       │ 2. Guardar JSON       │
         │                       ├──────────────────────▶│
         │                       │                   ┌───▼───┐
         │ 3. Iniciar Sesión     │                   │ ARCHIVOS│
         ├──────────────────────▶│                   │  JSON   │
         │                       │ 4. Cargar Quiz    │         │
         │                       ├──────────────────▶│         │
         │                       │                   └───┬───┘
         │                       │ 5. Participante se conecta │
         │                       │◀──────────────────────┼────┘
         │ 6. Mostrar participantes                      │
         │◀──────────────────────┤                       │
         │                       │                       │
         │ 7. Iniciar Quiz       │                       │
         ├──────────────────────▶│ 8. Enviar Pregunta    │
         │                       ├──────────────────────▶│
         │                       │ 9. Recibir Respuesta  │
         │ 10. Ver Resultados    │◀──────────────────────┤
         │◀──────────────────────┤                       │
```

### 🔁 CICLO DE VIDA DE UNA SESIÓN

#### 1. **Preparación**
```python
# Admin crea/selecciona quiz
quiz_data = load_quiz_from_file(quiz_id)
session = create_new_session(quiz_data)
server.start_session(session)
```

#### 2. **Lobby**
```python
# Participantes se conectan
participant = register_participant(name)
session.add_participant(participant)
broadcast_participant_list()
```

#### 3. **Ejecución**
```python
# Por cada pregunta:
question = session.get_current_question()
broadcast_question(question)
collect_answers(timeout=question.time_limit)
calculate_scores()
broadcast_results()
```

#### 4. **Finalización**
```python
# Al terminar:
final_results = calculate_final_scores()
save_session_to_history()
broadcast_final_results()
cleanup_session()
```

---

## 📡 COMUNICACIÓN EN TIEMPO REAL

### 🔌 WebSockets con SocketIO

#### 📤 EVENTOS DEL SERVIDOR → PARTICIPANTES
```python
# Eventos que el servidor envía
EVENTS_TO_PARTICIPANTS = {
    'participant_joined': 'Nuevo participante se unió',
    'participant_left': 'Participante se desconectó',
    'session_starting': 'La sesión está por comenzar',
    'question_sent': 'Nueva pregunta disponible',
    'question_results': 'Resultados de la pregunta',
    'session_ended': 'Sesión terminada',
    'final_results': 'Resultados finales'
}
```

#### 📥 EVENTOS DE PARTICIPANTES → SERVIDOR
```python
# Eventos que recibe el servidor
EVENTS_FROM_PARTICIPANTS = {
    'join_session': 'Unirse a sesión',
    'submit_answer': 'Enviar respuesta',
    'participant_ready': 'Participante listo',
    'disconnect': 'Desconectarse'
}
```

#### 🔄 EVENTOS ADMINISTRADOR ↔ SERVIDOR
```python
# Comunicación bidireccional admin
ADMIN_EVENTS = {
    'start_session': 'Iniciar sesión',
    'next_question': 'Siguiente pregunta',
    'pause_session': 'Pausar sesión',
    'end_session': 'Terminar sesión',
    'participant_update': 'Actualización participantes',
    'session_stats': 'Estadísticas en vivo'
}
```

### 📋 EJEMPLO DE IMPLEMENTACIÓN
```python
# socketio_events.py
@socketio.on('join_session')
def handle_join_session(data):
    participant_name = data['name']
    session_id = data['session_id']
    
    # Validar datos
    if not validate_participant_name(participant_name):
        emit('error', {'message': 'Nombre inválido'})
        return
    
    # Agregar participante
    participant = create_participant(participant_name)
    session = get_active_session()
    session.add_participant(participant)
    
    # Unir a sala de SocketIO
    join_room(session_id)
    
    # Notificar a todos
    emit('participant_joined', {
        'participant': participant.to_dict(),
        'total_participants': len(session.participants)
    }, room=session_id)
    
    # Notificar al admin
    emit('admin_participant_update', {
        'participants': [p.to_dict() for p in session.participants]
    }, room='admin')
```

---

## 💾 DISEÑO DE DATOS

### 📝 ESQUEMAS JSON

#### 🎯 Quiz Schema
```json
{
  "$schema": "quiz_schema",
  "id": "string (uuid)",
  "metadata": {
    "title": "string (required)",
    "description": "string (optional)",
    "created_date": "ISO date string",
    "last_modified": "ISO date string",
    "created_by": "string",
    "tags": ["array of strings"],
    "difficulty": "easy|medium|hard",
    "estimated_duration": "number (minutes)"
  },
  "settings": {
    "shuffle_questions": "boolean",
    "shuffle_options": "boolean",
    "show_correct_answer": "boolean",
    "time_between_questions": "number (seconds)",
    "allow_review": "boolean",
    "points_for_speed": "boolean"
  },
  "questions": [
    {
      "id": "number (sequential)",
      "type": "multiple_choice",
      "question": "string (required)",
      "options": ["array of strings (2-4 items)"],
      "correct_answer": "number (0-based index)",
      "points": "number (default: 100)",
      "time_limit": "number (seconds, default: 30)",
      "explanation": "string (optional)"
    }
  ]
}
```

#### 🎮 Session Schema
```json
{
  "$schema": "session_schema",
  "session_id": "string (uuid)",
  "quiz_id": "string (reference to quiz)",
  "status": "waiting|active|paused|finished",
  "created_at": "ISO date string",
  "started_at": "ISO date string",
  "ended_at": "ISO date string",
  "current_question_index": "number",
  "participants": [
    {
      "id": "string (uuid)",
      "name": "string",
      "joined_at": "ISO date string",
      "is_connected": "boolean",
      "current_score": "number",
      "answers": [
        {
          "question_id": "number",
          "selected_option": "number",
          "is_correct": "boolean",
          "points_earned": "number",
          "time_taken": "number (seconds)",
          "answered_at": "ISO date string"
        }
      ]
    }
  ],
  "question_stats": [
    {
      "question_id": "number",
      "total_responses": "number",
      "correct_responses": "number",
      "option_distribution": [0, 5, 3, 2],
      "average_time": "number (seconds)"
    }
  ]
}
```

#### 📊 History Schema
```json
{
  "$schema": "history_schema",
  "game_id": "string (uuid)",
  "quiz_metadata": {
    "quiz_id": "string",
    "title": "string",
    "total_questions": "number"
  },
  "session_info": {
    "date": "ISO date string",
    "duration": "string (HH:MM:SS)",
    "participants_count": "number"
  },
  "results": {
    "top_scores": [
      {
        "rank": "number",
        "participant_name": "string",
        "score": "number",
        "correct_answers": "number",
        "average_time": "number"
      }
    ],
    "quiz_statistics": {
      "completion_rate": "number (0-1)",
      "average_score": "number",
      "hardest_question": "number (question_id)",
      "easiest_question": "number (question_id)",
      "total_time": "number (seconds)"
    }
  }
}
```

---

## 🔧 CONFIGURACIÓN Y DEPLOYMENT

### ⚙️ Archivo de Configuración Principal
```python
# config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    # Servidor Web
    HOST: str = '0.0.0.0'
    PORT: int = 5000
    DEBUG: bool = True
    SECRET_KEY: str = 'dev-secret-key'
    
    # Rutas de Archivos
    DATA_DIR: str = './data'
    QUIZZES_DIR: str = './data/quizzes'
    SESSIONS_DIR: str = './data/sessions'
    HISTORY_DIR: str = './data/history'
    
    # Límites del Sistema
    MAX_PARTICIPANTS: int = 20
    MAX_QUESTIONS_PER_QUIZ: int = 50
    DEFAULT_QUESTION_TIME: int = 30
    SESSION_TIMEOUT: int = 3600  # 1 hora
    
    # UI Settings
    THEME: str = 'dark'
    FONT_SIZE: int = 12
    WINDOW_SIZE: tuple = (1200, 800)
```

### 🏗️ Inicialización del Sistema
```python
# main.py
import sys
import threading
from admin.main_window import AdminApp
from web.app import create_web_app
from utils.file_manager import initialize_data_structure

def main():
    # Inicializar estructura de datos
    initialize_data_structure()
    
    # Crear aplicación web en hilo separado
    web_app = create_web_app()
    web_thread = threading.Thread(
        target=lambda: web_app.run(host='0.0.0.0', port=5000),
        daemon=True
    )
    web_thread.start()
    
    # Iniciar aplicación Tkinter (hilo principal)
    admin_app = AdminApp()
    admin_app.run()

if __name__ == '__main__':
    main()
```

---

## 🛡️ MANEJO DE ERRORES Y SEGURIDAD

### ⚠️ ESTRATEGIAS DE MANEJO DE ERRORES

#### 🔧 En la Aplicación Tkinter
```python
# error_handler.py
import logging
from tkinter import messagebox

class ErrorHandler:
    @staticmethod
    def handle_file_error(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError:
                messagebox.showerror("Error", "Archivo no encontrado")
            except PermissionError:
                messagebox.showerror("Error", "Sin permisos para acceder al archivo")
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Archivo corrupto")
        return wrapper
```

#### 🌐 En el Servidor Web
```python
# web/error_handler.py
from flask import jsonify

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

@socketio.on_error()
def error_handler(e):
    logging.error(f'SocketIO Error: {e}')
    emit('error', {'message': 'Error de conexión'})
```

### 🔒 CONSIDERACIONES DE SEGURIDAD

#### ✅ MEDIDAS IMPLEMENTADAS
- **Validación de entrada**: Sanitización de nombres de usuario
- **Límites de rate**: Prevenir spam de requests
- **Timeout de sesiones**: Limpiar sesiones inactivas
- **Validación de archivos**: Verificar integridad de JSON

#### ⚠️ LIMITACIONES CONOCIDAS
- Sin autenticación real (solo nombres)
- Sin cifrado de comunicación
- Red local únicamente
- Sin protección DDoS avanzada

---

## 📈 OPTIMIZACIÓN Y PERFORMANCE

### 🚀 ESTRATEGIAS DE OPTIMIZACIÓN

#### ⚡ Frontend Web
```javascript
// Optimizaciones del cliente
const optimizations = {
    // Debounce para eventos frecuentes
    debounceAnswers: 500, // ms
    
    // Cache de elementos DOM
    cacheSelectors: true,
    
    // Lazy loading de imágenes
    lazyLoad: true,
    
    // Minificación de requests
    batchUpdates: true
};
```

#### 🔧 Backend Performance
```python
# Optimizaciones del servidor
from functools import lru_cache

class PerformanceOptimizer:
    @lru_cache(maxsize=100)
    def load_quiz(self, quiz_id):
        # Cache de quizzes en memoria
        return self._load_quiz_from_file(quiz_id)
    
    def batch_socket_emissions(self, events):
        # Agrupar emisiones WebSocket
        for room, event_batch in events.items():
            socketio.emit('batch_update', event_batch, room=room)
```

### 📊 MÉTRICAS DE RENDIMIENTO

#### 🎯 OBJETIVOS DE PERFORMANCE
- **Latencia WebSocket**: < 100ms en red local
- **Tiempo de carga**: < 3 segundos para página web
- **Uso de memoria**: < 500MB con 20 participantes
- **CPU**: < 30% de uso en operación normal

---

**Esta arquitectura técnica proporciona la base sólida para desarrollar tu plataforma de quizzes de manera escalable y mantenible.** 🏗️
