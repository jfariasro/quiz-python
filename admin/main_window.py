"""
Ventana principal de la aplicación de administración Tkinter.
Interfaz gráfica para gestionar quizzes y sesiones en vivo.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import threading
import json
import os
from pathlib import Path
import logging
from typing import Optional, Dict, Any, List

from utils.file_manager import FileManager
from utils.network_utils import NetworkUtils
from utils.quiz_logic import QuizManager, QuizState
from web.app import start_quiz_session, stop_quiz_session, get_session_info

logger = logging.getLogger(__name__)

class QuizAdminApp:
    """Aplicación principal de administración de quizzes."""
    
    def __init__(self):
        """Inicializar la aplicación de administración."""
        # Configurar tema de CustomTkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Crear ventana principal
        self.root = ctk.CTk()
        self.root.title("Plataforma de Quizzes - Administración")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Managers
        self.file_manager = FileManager()
        self.quiz_manager = QuizManager()
        
        # Variables de estado
        self.current_session_id = None
        self.web_server_running = False
        self.selected_quiz_id = None
        self.quiz_id_map = {}  # Mapeo de nombres de quizzes a IDs completos
        
        # Variables de UI
        self.server_status_var = tk.StringVar(value="Detenido")
        self.server_ip_var = tk.StringVar(value="No disponible")
        self.participants_var = tk.StringVar(value="0")
        self.quiz_state_var = tk.StringVar(value="Sin sesión")
        self.session_code_var = tk.StringVar(value="Código: ---")
        
        # Configurar interfaz
        self.setup_ui()
        
        # Cargar datos iniciales
        self.load_quizzes()
        self.update_network_info()
        
        logger.info("Aplicación de administración inicializada")
    
    def setup_ui(self):
        """Configurar la interfaz de usuario."""
        # Configurar grid principal
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Panel lateral
        self.setup_sidebar()
        
        # Área principal
        self.setup_main_area()
        
        # Barra de estado
        self.setup_status_bar()
    
    def setup_sidebar(self):
        """Configurar panel lateral de navegación."""
        self.sidebar = ctk.CTkFrame(self.root, width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.sidebar.grid_propagate(False)
        
        # Título
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="Quiz Admin",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Información del servidor
        server_frame = ctk.CTkFrame(self.sidebar)
        server_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(server_frame, text="Estado del Servidor", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.server_status_label = ctk.CTkLabel(
            server_frame,
            textvariable=self.server_status_var,
            font=ctk.CTkFont(size=12)
        )
        self.server_status_label.pack()
        
        self.server_ip_label = ctk.CTkLabel(
            server_frame,
            textvariable=self.server_ip_var,
            font=ctk.CTkFont(size=10)
        )
        self.server_ip_label.pack(pady=(0, 5))
        
        # Botones de control del servidor
        self.start_server_btn = ctk.CTkButton(
            server_frame,
            text="Iniciar Servidor",
            command=self.toggle_server
        )
        self.start_server_btn.pack(pady=5)
        
        # Información de la sesión
        session_frame = ctk.CTkFrame(self.sidebar)
        session_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(session_frame, text="Sesión Actual", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.quiz_state_label = ctk.CTkLabel(
            session_frame,
            textvariable=self.quiz_state_var,
            font=ctk.CTkFont(size=12)
        )
        self.quiz_state_label.pack()
        
        # Código de sesión (destacado) con marco
        code_frame = ctk.CTkFrame(session_frame)
        code_frame.pack(fill="x", padx=5, pady=5)
        
        self.session_code_label = ctk.CTkLabel(
            code_frame,
            textvariable=self.session_code_var,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3a86ff"  # Color destacado para el código
        )
        self.session_code_label.pack(side="left", padx=5, pady=5)
        
        # Botón para copiar el código
        self.copy_code_btn = ctk.CTkButton(
            code_frame,
            text="📋",
            width=30,
            height=30,
            command=self.copy_session_code,
            fg_color="#3a86ff", 
            hover_color="#4361ee"
        )
        self.copy_code_btn.pack(side="right", padx=5, pady=5)
        
        self.participants_label = ctk.CTkLabel(
            session_frame,
            text="Participantes: 0",
            font=ctk.CTkFont(size=10)
        )
        self.participants_label.pack(pady=(0, 5))
        
        # Navegación
        nav_frame = ctk.CTkFrame(self.sidebar)
        nav_frame.pack(fill="x", padx=10, pady=20)
        
        # Botones de navegación
        nav_buttons = [
            ("📚 Gestión de Quizzes", self.show_quiz_management),
            ("🎮 Control de Sesión", self.show_session_control),
            ("📊 Estadísticas", self.show_statistics),
            ("⚙️ Configuración", self.show_settings)
        ]
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                command=command,
                anchor="w"
            )
            btn.pack(fill="x", pady=2)
    
    def setup_main_area(self):
        """Configurar área principal de contenido."""
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Crear pestañas
        self.setup_quiz_management_tab()
        self.setup_session_control_tab()
        self.setup_statistics_tab()
        self.setup_settings_tab()
    
    def setup_quiz_management_tab(self):
        """Configurar pestaña de gestión de quizzes."""
        self.quiz_tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.quiz_tab, text="📚 Gestión de Quizzes")
        
        # Panel superior con botones
        top_frame = ctk.CTkFrame(self.quiz_tab)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            top_frame,
            text="➕ Crear Quiz",
            command=self.create_new_quiz
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            top_frame,
            text="📝 Editar Quiz",
            command=self.edit_selected_quiz
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            top_frame,
            text="🗑️ Eliminar Quiz",
            command=self.delete_selected_quiz
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            top_frame,
            text="📄 Importar Quiz",
            command=self.import_quiz
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            top_frame,
            text="💾 Exportar Quiz",
            command=self.export_quiz
        ).pack(side="right", padx=5)
        
        # Lista de quizzes
        list_frame = ctk.CTkFrame(self.quiz_tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview para lista de quizzes
        columns = ("ID", "Título", "Preguntas", "Creado", "Modificado")
        self.quiz_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            self.quiz_tree.heading(col, text=col)
            self.quiz_tree.column(col, width=150)
        
        # Scrollbar para la lista
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.quiz_tree.yview)
        self.quiz_tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar lista y scrollbar
        self.quiz_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind eventos
        self.quiz_tree.bind("<<TreeviewSelect>>", self.on_quiz_select)
        self.quiz_tree.bind("<Double-1>", self.on_quiz_double_click)
        
        # Panel de vista previa
        preview_frame = ctk.CTkFrame(self.quiz_tab)
        preview_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            preview_frame,
            text="Vista Previa del Quiz",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5)
        
        self.quiz_preview = tk.Text(
            preview_frame,
            height=6,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="#f0f0f0"
        )
        self.quiz_preview.pack(fill="x", padx=10, pady=5)
    
    def setup_session_control_tab(self):
        """Configurar pestaña de control de sesiones."""
        self.session_tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.session_tab, text="🎮 Control de Sesión")
        
        # Panel de selección de quiz
        quiz_selection_frame = ctk.CTkFrame(self.session_tab)
        quiz_selection_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            quiz_selection_frame,
            text="Quiz a Ejecutar",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5)
        
        self.selected_quiz_var = tk.StringVar()
        self.quiz_selector = ctk.CTkComboBox(
            quiz_selection_frame,
            variable=self.selected_quiz_var,
            state="readonly"
        )
        self.quiz_selector.pack(fill="x", padx=10, pady=5)
        
        # Botones de control
        control_frame = ctk.CTkFrame(self.session_tab)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_quiz_btn = ctk.CTkButton(
            control_frame,
            text="🚀 Iniciar Quiz",
            command=self.start_quiz_session,
            state="disabled"
        )
        self.start_quiz_btn.pack(side="left", padx=5)
        
        self.start_game_btn = ctk.CTkButton(
            control_frame,
            text="🎮 Iniciar Juego",
            command=self.start_game,
            state="disabled"
        )
        self.start_game_btn.pack(side="left", padx=5)
        
        self.stop_quiz_btn = ctk.CTkButton(
            control_frame,
            text="⏹️ Detener Quiz",
            command=self.stop_quiz_session,
            state="disabled"
        )
        self.stop_quiz_btn.pack(side="left", padx=5)
        
        self.next_question_btn = ctk.CTkButton(
            control_frame,
            text="⏭️ Siguiente Pregunta",
            command=self.next_question,
            state="disabled"
        )
        self.next_question_btn.pack(side="left", padx=5)
        
        # Panel de monitoreo
        monitor_frame = ctk.CTkFrame(self.session_tab)
        monitor_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            monitor_frame,
            text="Monitor de Participantes",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5)
        
        # Lista de participantes
        participants_columns = ("Nombre", "Estado", "Puntuación", "Última Actividad")
        self.participants_tree = ttk.Treeview(
            monitor_frame,
            columns=participants_columns,
            show="headings",
            height=10
        )
        
        for col in participants_columns:
            self.participants_tree.heading(col, text=col)
            self.participants_tree.column(col, width=120)
        
        self.participants_tree.pack(fill="both", expand=True, padx=10, pady=5)
    
    def setup_statistics_tab(self):
        """Configurar pestaña de estadísticas."""
        self.stats_tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.stats_tab, text="📊 Estadísticas")
        
        ctk.CTkLabel(
            self.stats_tab,
            text="Estadísticas y Reportes",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Panel de resumen
        summary_frame = ctk.CTkFrame(self.stats_tab)
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        # Estadísticas generales
        stats_grid = ctk.CTkFrame(summary_frame)
        stats_grid.pack(fill="x", padx=10, pady=10)
        
        stats_labels = [
            ("Total de Quizzes", "total_quizzes"),
            ("Sesiones Ejecutadas", "total_sessions"),
            ("Participantes Únicos", "unique_participants"),
            ("Tiempo Promedio", "avg_duration")
        ]
        
        for i, (label, key) in enumerate(stats_labels):
            frame = ctk.CTkFrame(stats_grid)
            frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(weight="bold")).pack()
            setattr(self, f"{key}_label", ctk.CTkLabel(frame, text="0"))
            getattr(self, f"{key}_label").pack()
        
        # Configurar grid
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
    
    def setup_settings_tab(self):
        """Configurar pestaña de configuración."""
        self.settings_tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.settings_tab, text="⚙️ Configuración")
        
        ctk.CTkLabel(
            self.settings_tab,
            text="Configuración del Sistema",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Panel de configuración de red
        network_frame = ctk.CTkFrame(self.settings_tab)
        network_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            network_frame,
            text="Configuración de Red",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5)
        
        # Configuración de puerto
        port_frame = ctk.CTkFrame(network_frame)
        port_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(port_frame, text="Puerto del servidor:").pack(side="left")
        self.port_entry = ctk.CTkEntry(port_frame, placeholder_text="5000")
        self.port_entry.pack(side="right", padx=5)
        
        # Configuración de quiz por defecto
        quiz_defaults_frame = ctk.CTkFrame(self.settings_tab)
        quiz_defaults_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            quiz_defaults_frame,
            text="Configuración de Quiz por Defecto",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5)
        
        # Tiempo por pregunta
        time_frame = ctk.CTkFrame(quiz_defaults_frame)
        time_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(time_frame, text="Tiempo por pregunta (segundos):").pack(side="left")
        self.question_time_entry = ctk.CTkEntry(time_frame, placeholder_text="30")
        self.question_time_entry.pack(side="right", padx=5)
        
        # Botón guardar configuración
        ctk.CTkButton(
            self.settings_tab,
            text="💾 Guardar Configuración",
            command=self.save_settings
        ).pack(pady=20)
    
    def setup_status_bar(self):
        """Configurar barra de estado inferior."""
        self.status_bar = ctk.CTkFrame(self.root, height=30)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Listo",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="left", padx=10)
        
        # Información de red en barra de estado
        self.network_info_label = ctk.CTkLabel(
            self.status_bar,
            text="Red: No disponible",
            font=ctk.CTkFont(size=10)
        )
        self.network_info_label.pack(side="right", padx=10)
    
    # Métodos de funcionalidad
    
    def load_quizzes(self):
        """Cargar lista de quizzes disponibles."""
        try:
            quizzes = self.file_manager.list_quizzes()
            
            # Limpiar lista actual
            for item in self.quiz_tree.get_children():
                self.quiz_tree.delete(item)
            
            # Crear mapeo de títulos a IDs completos
            self.quiz_id_map = {}
            
            # Agregar quizzes a la lista
            for quiz in quizzes:
                self.quiz_tree.insert("", "end", values=(
                    quiz['id'][:8],  # ID corto para mostrar
                    quiz['title'],
                    quiz['question_count'],
                    quiz.get('created_at', '')[:10],  # Solo fecha
                    quiz.get('updated_at', '')[:10]   # Solo fecha
                ))
                
                # Mapear título a ID completo
                display_text = f"{quiz['title']} (ID: {quiz['id'][:8]})"
                self.quiz_id_map[display_text] = quiz['id']
            
            # Actualizar selector de quizzes
            quiz_options = list(self.quiz_id_map.keys())
            self.quiz_selector.configure(values=quiz_options)
            
            self.status_label.configure(text=f"Cargados {len(quizzes)} quizzes")
            
        except Exception as e:
            logger.error(f"Error al cargar quizzes: {e}")
            messagebox.showerror("Error", f"Error al cargar quizzes: {e}")
    
    def update_network_info(self):
        """Actualizar información de red."""
        try:
            local_ip = NetworkUtils.get_local_ip()
            if local_ip:
                self.server_ip_var.set(f"IP: {local_ip}:5000")
                self.network_info_label.configure(text=f"Red: {local_ip}")
            else:
                self.server_ip_var.set("IP: No detectada")
                self.network_info_label.configure(text="Red: No disponible")
                
        except Exception as e:
            logger.error(f"Error al detectar IP: {e}")
            self.server_ip_var.set("IP: Error")
    
    def toggle_server(self):
        """Alternar estado del servidor web."""
        if self.web_server_running:
            self.stop_web_server()
        else:
            self.start_web_server()
    
    def start_web_server(self):
        """Iniciar servidor web."""
        try:
            # Crear thread para el servidor web
            from web.app import run_server
            
            def run_server_thread():
                try:
                    # Obtener IP local
                    local_ip = NetworkUtils.get_local_ip()
                    if not local_ip:
                        raise Exception("No se pudo detectar la IP local")
                        
                    # Actualizar UI con la IP
                    self.server_ip_var.set(f"IP: {local_ip}")
                    
                    # Iniciar servidor
                    run_server(debug=False)
                except Exception as e:
                    logger.error(f"Error en thread del servidor: {e}")
                    self.root.after(0, lambda: self.handle_server_error(str(e)))
            
            # Iniciar servidor en thread separado
            self.server_thread = threading.Thread(target=run_server_thread, daemon=True)
            self.server_thread.start()
            
            # Actualizar UI
            self.web_server_running = True
            self.server_status_var.set("Ejecutándose")
            self.start_server_btn.configure(text="Detener Servidor")
            self.start_quiz_btn.configure(state="normal")
            
            self.status_label.configure(text="Servidor web iniciado")
            logger.info("Servidor web iniciado")
            
        except Exception as e:
            logger.error(f"Error al iniciar servidor: {e}")
            messagebox.showerror("Error", f"Error al iniciar servidor: {e}")
            
    def handle_server_error(self, error_msg):
        """Manejar errores del servidor web."""
        messagebox.showerror("Error del Servidor", f"Error en el servidor web: {error_msg}")
        self.stop_web_server()
        
    def stop_web_server(self):
        """Detener servidor web."""
        try:
            # Detener sesión activa si existe
            if self.current_session_id:
                self.stop_quiz_session()
            
            # TODO: Implementar cierre más limpio del servidor
            if hasattr(self, 'server_thread'):
                # Por ahora el thread es daemon, se cerrará automáticamente
                self.server_thread = None
            
            self.web_server_running = False
            self.server_status_var.set("Detenido")
            self.server_ip_var.set("No disponible")
            self.start_server_btn.configure(text="Iniciar Servidor")
            self.start_quiz_btn.configure(state="disabled")
            
            self.status_label.configure(text="Servidor web detenido")
            logger.info("Servidor web detenido")
        except Exception as e:
            logger.error(f"Error al detener servidor: {e}")
            messagebox.showerror("Error", f"Error al detener servidor: {e}")
    
    def start_quiz_session(self):
        """Iniciar sesión de quiz."""
        try:
            selected = self.selected_quiz_var.get()
            if not selected:
                messagebox.showwarning("Advertencia", "Selecciona un quiz para iniciar")
                return
            
            # Obtener ID completo del mapeo
            quiz_id = self.quiz_id_map.get(selected)
            if not quiz_id:
                messagebox.showerror("Error", "No se pudo obtener el ID del quiz seleccionado")
                return
            
            # Cargar datos del quiz
            quiz_data = self.file_manager.load_quiz(quiz_id)
            if not quiz_data:
                messagebox.showerror("Error", "No se pudo cargar el quiz seleccionado")
                return
            
            # Iniciar sesión
            self.current_session_id = start_quiz_session(quiz_data)
            
            # Actualizar UI
            self.quiz_state_var.set("Esperando participantes")
            self.start_quiz_btn.configure(state="disabled")
            self.stop_quiz_btn.configure(state="normal")
            # Habilitar el botón de iniciar juego ahora que tenemos una sesión
            self.start_game_btn.configure(state="normal")
            
            # Mostrar código de sesión en una ventana emergente
            code_message = f"¡Quiz iniciado!\n\nCódigo de sesión: {self.current_session_id}\n\nComparte este código con los participantes para que puedan unirse al quiz."
            messagebox.showinfo("Código de Sesión", code_message)
            
            # Actualizar UI con el código de sesión
            if hasattr(self, 'session_code_var'):
                self.session_code_var.set(f"Código: {self.current_session_id}")
            
            self.status_label.configure(text=f"Quiz iniciado: {quiz_data['title']}")
            logger.info(f"Sesión de quiz iniciada: {self.current_session_id}")
            
        except Exception as e:
            logger.error(f"Error al iniciar quiz: {e}")
            messagebox.showerror("Error", f"Error al iniciar quiz: {e}")
    
    def stop_quiz_session(self):
        """Detener sesión de quiz."""
        try:
            if self.current_session_id:
                stop_quiz_session(self.current_session_id)
                self.current_session_id = None
            
            # Actualizar UI
            self.quiz_state_var.set("Sin sesión")
            self.participants_var.set("0")
            self.session_code_var.set("Código: ---")
            self.start_quiz_btn.configure(state="normal")
            self.stop_quiz_btn.configure(state="disabled")
            self.next_question_btn.configure(state="disabled")
            self.start_game_btn.configure(state="disabled")
            
            # Limpiar lista de participantes
            for item in self.participants_tree.get_children():
                self.participants_tree.delete(item)
            
            self.status_label.configure(text="Sesión de quiz detenida")
            logger.info("Sesión de quiz detenida")
            
        except Exception as e:
            logger.error(f"Error al detener quiz: {e}")
            messagebox.showerror("Error", f"Error al detener quiz: {e}")
    
    def next_question(self):
        """Avanzar a la siguiente pregunta."""
        try:
            if not self.current_session_id:
                return
            
            session = self.quiz_manager.get_session(self.current_session_id)
            if session:
                if not session.next_question():
                    # Quiz terminado
                    self.quiz_state_var.set("Finalizado")
                    self.next_question_btn.configure(state="disabled")
                
        except Exception as e:
            logger.error(f"Error al avanzar pregunta: {e}")
            messagebox.showerror("Error", f"Error al avanzar pregunta: {e}")
    
    def create_new_quiz(self):
        """Abrir ventana para crear nuevo quiz."""
        self.status_label.configure(text="Función de crear quiz en desarrollo")
    
    def edit_selected_quiz(self):
        """Editar quiz seleccionado."""
        selection = self.quiz_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un quiz para editar")
            return
        
        self.status_label.configure(text="Función de editar quiz en desarrollo")
    
    def delete_selected_quiz(self):
        """Eliminar quiz seleccionado."""
        selection = self.quiz_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un quiz para eliminar")
            return
        
        item = selection[0]
        quiz_id = self.quiz_tree.item(item)['values'][0]
        
        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este quiz?"):
            try:
                # TODO: Obtener ID completo del quiz
                # self.file_manager.delete_quiz(full_quiz_id)
                self.load_quizzes()
                self.status_label.configure(text="Quiz eliminado")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar quiz: {e}")
    
    def import_quiz(self):
        """Importar quiz desde archivo."""
        file_path = filedialog.askopenfilename(
            title="Importar Quiz",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    quiz_data = json.load(f)
                
                # Validar y guardar
                quiz_id = self.file_manager.save_quiz(quiz_data)
                self.load_quizzes()
                
                self.status_label.configure(text=f"Quiz importado: {quiz_id}")
                messagebox.showinfo("Éxito", "Quiz importado correctamente")
                
            except Exception as e:
                logger.error(f"Error al importar quiz: {e}")
                messagebox.showerror("Error", f"Error al importar quiz: {e}")
    
    def export_quiz(self):
        """Exportar quiz seleccionado."""
        selection = self.quiz_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un quiz para exportar")
            return
        
        self.status_label.configure(text="Función de exportar quiz en desarrollo")
    
    def save_settings(self):
        """Guardar configuración."""
        try:
            config = {
                'server_port': self.port_entry.get() or "5000",
                'default_question_time': self.question_time_entry.get() or "30"
            }
            
            self.file_manager.save_config('app_settings', config)
            self.status_label.configure(text="Configuración guardada")
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
            
        except Exception as e:
            logger.error(f"Error al guardar configuración: {e}")
            messagebox.showerror("Error", f"Error al guardar configuración: {e}")
    
    def setup_game_controls(self):
        """Configurar controles del juego."""
        pass  # TODO: Implementar configuración de controles del juego
    
    def start_game(self):
        """Iniciar el juego cuando los participantes están listos en el lobby."""
        try:
            if not self.current_session_id:
                messagebox.showwarning("Advertencia", "No hay una sesión de quiz activa")
                return
            
            # Obtener información de la sesión 
            session_info = get_session_info(self.current_session_id)
            if not session_info:
                messagebox.showerror("Error", "No se pudo obtener información de la sesión")
                return
            
            # Verificar que hay participantes
            participants_count = len(session_info.get('participants', []))
            if participants_count == 0:
                messagebox.showwarning("Advertencia", "No hay participantes en el lobby")
                return
            
            # Enviar comando para iniciar el juego
            import socketio
            sio = socketio.Client()
            
            try:
                # Conectar al servidor local
                sio.connect('http://localhost:5000')
                
                # Emitir evento para iniciar el juego
                sio.emit('admin_start_game', {'session_id': self.current_session_id})
                
                # Desconectar
                sio.disconnect()
                
                # Actualizar UI
                self.quiz_state_var.set("En juego")
                self.start_game_btn.configure(state="disabled")
                self.next_question_btn.configure(state="normal")
                
                messagebox.showinfo("Juego iniciado", f"El juego ha comenzado para {participants_count} participantes")
                
            except Exception as e:
                logger.error(f"Error al conectar con el servidor: {e}")
                messagebox.showerror("Error", f"Error al comunicarse con el servidor: {e}")
                
        except Exception as e:
            logger.error(f"Error al iniciar juego: {e}")
            messagebox.showerror("Error", f"Error al iniciar juego: {e}")
            
    def copy_session_code(self):
        """Copiar código de sesión al portapapeles."""
        if self.current_session_id:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_session_id)
            self.status_label.configure(text="Código copiado al portapapeles")

            # Cambiar el color del botón brevemente para dar feedback
            original_color = self.copy_code_btn.cget("fg_color")
            self.copy_code_btn.configure(fg_color="#06d6a0")  # Color de éxito

            # Restaurar el color original después de un breve tiempo
            def restore_color():
                self.copy_code_btn.configure(fg_color=original_color)
            self.root.after(800, restore_color)
    
    # Event handlers
    
    def on_quiz_select(self, event):
        """Manejar selección de quiz en la lista."""
        selection = self.quiz_tree.selection()
        if selection:
            item = selection[0]
            quiz_id = self.quiz_tree.item(item)['values'][0]
            
            # TODO: Cargar y mostrar vista previa del quiz
            self.quiz_preview.config(state=tk.NORMAL)
            self.quiz_preview.delete(1.0, tk.END)
            self.quiz_preview.insert(1.0, f"Vista previa del quiz ID: {quiz_id}\n\n(Funcionalidad en desarrollo)")
            self.quiz_preview.config(state=tk.DISABLED)
    
    def on_quiz_double_click(self, event):
        """Manejar doble click en quiz."""
        self.edit_selected_quiz()
    
    # Métodos de navegación
    
    def show_quiz_management(self):
        """Mostrar pestaña de gestión de quizzes."""
        self.notebook.select(0)
    
    def show_session_control(self):
        """Mostrar pestaña de control de sesión."""
        self.notebook.select(1)
    
    def show_statistics(self):
        """Mostrar pestaña de estadísticas."""
        self.notebook.select(2)
    
    def show_settings(self):
        """Mostrar pestaña de configuración."""
        self.notebook.select(3)
    
    def run(self):
        """Ejecutar la aplicación."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Aplicación interrumpida por el usuario")
        except Exception as e:
            logger.error(f"Error en la aplicación: {e}")
            messagebox.showerror("Error crítico", f"Error en la aplicación: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpiar recursos antes de cerrar."""
        try:
            if self.current_session_id:
                self.stop_quiz_session()
            
            if self.web_server_running:
                self.stop_web_server()
                
            logger.info("Aplicación de administración cerrada")
            
        except Exception as e:
            logger.error(f"Error en cleanup: {e}")

if __name__ == "__main__":
    app = QuizAdminApp()
    app.run()
