# Plataforma de Quizzes Tipo Kahoot! - Proyecto Completo

## 🎯 Descripción General
Plataforma de administración y web para manejar quizzes interactivos tipo Kahoot!, con interfaz de escritorio en Tkinter para administración y servidor web para participantes que se conectan via WiFi.

## 🚀 Características Principales
- **Administración Desktop**: Interfaz Tkinter para crear, editar y gestionar quizzes
- **Servidor Web**: Interfaz web para que los participantes se conecten via WiFi
- **Sistema de Archivos**: Almacenamiento basado en archivos JSON (sin base de datos)
- **Tiempo Real**: Sistema de quizzes en vivo con múltiples participantes
- **Historial**: Registro de puntajes y estadísticas

## 📁 Estructura del Proyecto
```
quizzes/
├── README.md                     # Este archivo
├── INSTRUCTIVO.md               # Guía detallada del proyecto
├── requirements.txt             # Dependencias Python
├── main.py                     # Punto de entrada principal
├── admin/                      # Aplicación de administración
│   ├── __init__.py
│   ├── main_window.py          # Ventana principal Tkinter
│   ├── quiz_creator.py         # Creador de quizzes
│   ├── quiz_manager.py         # Gestor de quizzes
│   ├── history_viewer.py       # Visor de historial
│   └── settings.py             # Configuraciones
├── web/                        # Servidor web
│   ├── __init__.py
│   ├── app.py                  # Aplicación Flask/FastAPI
│   ├── routes.py               # Rutas web
│   ├── socketio_events.py      # Eventos WebSocket
│   └── templates/              # Templates HTML
│       ├── index.html          # Página principal
│       ├── lobby.html          # Sala de espera
│       ├── quiz.html           # Interfaz del quiz
│       └── results.html        # Resultados
├── data/                       # Almacenamiento de datos
│   ├── quizzes/               # Archivos de quizzes
│   ├── sessions/              # Sesiones de juego
│   ├── history/               # Historial de partidas
│   └── config/                # Configuraciones
├── static/                     # Archivos estáticos web
│   ├── css/
│   ├── js/
│   └── images/
├── utils/                      # Utilidades
│   ├── __init__.py
│   ├── file_manager.py         # Manejo de archivos
│   ├── network_utils.py        # Utilidades de red
│   └── quiz_logic.py           # Lógica del quiz
└── docs/                       # Documentación
    ├── ALCANCE.md              # Definición del alcance
    ├── ARQUITECTURA.md         # Documentación técnica
    └── MANUAL_USUARIO.md       # Manual de usuario
```

## 🔧 Tecnologías Utilizadas
- **Frontend Administración**: Tkinter
- **Backend Web**: Flask + SocketIO
- **Frontend Web**: HTML5, CSS3, JavaScript
- **Comunicación**: WebSockets para tiempo real
- **Almacenamiento**: Archivos JSON
- **Red**: WiFi local

## ⚡ Inicio Rápido
1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar aplicación: `python main.py`
3. Conectarse desde dispositivos: `http://[IP_LOCAL]:5000`

## 📖 Documentación Completa
Para información detallada, consulta:
- [INSTRUCTIVO.md](./INSTRUCTIVO.md) - Guía completa del proyecto
- [docs/ALCANCE.md](./docs/ALCANCE.md) - Definición del alcance
- [docs/ARQUITECTURA.md](./docs/ARQUITECTURA.md) - Documentación técnica
