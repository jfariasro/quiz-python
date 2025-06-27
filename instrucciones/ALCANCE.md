# 🎯 ALCANCE DEL PROYECTO - PLATAFORMA DE QUIZZES KAHOOT!

## 📋 DEFINICIÓN DEL ALCANCE

### 🎪 ¿QUÉ ES EL PROYECTO?
Una plataforma completa para crear y ejecutar quizzes interactivos tipo Kahoot!, compuesta por:
- **Aplicación de escritorio** (Tkinter) para administración
- **Servidor web local** para participantes que se conectan via WiFi
- **Sistema de archivos** para almacenamiento (sin base de datos)

---

## ✅ FUNCIONALIDADES INCLUIDAS EN EL ALCANCE

### 🖥️ APLICACIÓN DE ADMINISTRACIÓN (Tkinter)

#### 📝 Gestión de Quizzes
- **Crear quizzes nuevos**
  - Título, descripción, configuraciones
  - Agregar preguntas una por una
  - Configurar opciones de respuesta (2-4 opciones)
  - Establecer respuesta correcta
  - Definir puntos y tiempo límite por pregunta

- **Editar quizzes existentes**
  - Modificar información general
  - Agregar/eliminar/editar preguntas
  - Reordenar preguntas
  - Cambiar configuraciones

- **Gestionar biblioteca de quizzes**
  - Ver lista de quizzes disponibles
  - Buscar y filtrar quizzes
  - Eliminar quizzes obsoletos
  - Duplicar quizzes existentes

#### 🎮 Control de Sesiones en Vivo
- **Inicio/parada del servidor web**
  - Activar/desactivar servidor con un clic
  - Mostrar IP local y puerto para participantes
  - Verificar estado de conexión

- **Control del flujo del quiz**
  - Iniciar quiz cuando estén listos los participantes
  - Controlar timing de preguntas
  - Avanzar manualmente entre preguntas
  - Pausar/reanudar sesión

- **Monitoreo en tiempo real**
  - Ver participantes conectados
  - Observar respuestas en vivo
  - Mostrar ranking actualizado
  - Estadísticas de progreso

#### 📊 Historial y Reportes
- **Historial de sesiones**
  - Lista de partidas anteriores
  - Detalles de cada sesión
  - Participantes y puntajes
  - Duración y fecha

- **Estadísticas**
  - Rendimiento por quiz
  - Preguntas más difíciles/fáciles
  - Promedio de participantes
  - Tiempo promedio de respuesta

### 🌐 PLATAFORMA WEB PARA PARTICIPANTES

#### 🚪 Acceso y Lobby
- **Ingreso a la sesión**
  - Página de entrada con código/nombre
  - Validación de nombre de usuario
  - Entrada a sala de espera

- **Sala de espera (Lobby)**
  - Lista de participantes conectados
  - Cuenta regresiva para inicio
  - Instrucciones del quiz
  - Estado del administrador

#### 🎯 Interfaz de Juego
- **Visualización de preguntas**
  - Pregunta clara y legible
  - Opciones de respuesta destacadas
  - Timer visual por pregunta
  - Número de pregunta actual

- **Interacción del participante**
  - Selección de respuesta intuitiva
  - Feedback inmediato (correcto/incorrecto)
  - Puntos ganados por respuesta
  - Posición actual en ranking

#### 🏆 Resultados y Rankings
- **Resultados por pregunta**
  - Respuesta correcta mostrada
  - Distribución de respuestas
  - Puntaje individual acumulado
  - Ranking actualizado

- **Resultados finales**
  - Podio con top 3 participantes
  - Puntaje final personal
  - Estadísticas de la sesión
  - Opción para nueva partida

### 💾 SISTEMA DE ALMACENAMIENTO

#### 📁 Estructura de Archivos JSON
- **Quizzes** (`/data/quizzes/`)
  - Un archivo JSON por quiz
  - Metadatos y configuraciones
  - Array de preguntas completas
  - Configuraciones de juego

- **Sesiones activas** (`/data/sessions/`)
  - Estado actual de juegos en curso
  - Participantes conectados
  - Progreso de preguntas
  - Respuestas temporales

- **Historial** (`/data/history/`)
  - Sesiones completadas
  - Resultados finales
  - Estadísticas de participación
  - Datos para reportes

#### 🔧 Gestión de Archivos
- **Lectura/escritura automática**
  - Carga de datos al iniciar
  - Guardado automático de cambios
  - Respaldo de seguridad
  - Validación de integridad

---

## ❌ FUNCIONALIDADES EXCLUIDAS DEL ALCANCE

### 🚫 NO INCLUIDO EN ESTE PROYECTO

#### 💽 Base de Datos
- **Sin MySQL, PostgreSQL, SQLite**
  - Todo se maneja con archivos JSON
  - No hay configuración de DB
  - No hay migraciones de esquema

#### 🔐 Autenticación Compleja
- **Sin sistema de usuarios avanzado**
  - No hay registro de cuentas
  - No hay passwords
  - No hay roles de usuario
  - Solo nombres simples para participantes

#### 🌍 Conectividad Externa
- **Solo red local WiFi**
  - No conexión a internet externa
  - No modo cloud/online
  - No sincronización entre redes
  - No acceso remoto via internet

#### 📱 Aplicaciones Móviles Nativas
- **Solo navegador web**
  - No app para iOS/Android
  - No instalación en dispositivos
  - No notificaciones push
  - No modo offline

#### 🔗 Integraciones Externas
- **Sin APIs de terceros**
  - No integración con Google Classroom
  - No exportación a LMS
  - No login con redes sociales
  - No pagos o suscripciones

#### 🎨 Funcionalidades Avanzadas
- **Características complejas no incluidas**
  - No soporte para imágenes/videos en preguntas
  - No preguntas de múltiple respuesta
  - No preguntas abiertas/texto libre
  - No sistema de equipos/colaborativo
  - No modo torneo/eliminación

---

## 🎯 CRITERIOS DE ÉXITO

### ✅ OBJETIVOS PRINCIPALES

#### 🎪 Funcionalidad Core
1. **Crear un quiz completo desde Tkinter** ✓
2. **Mínimo 5 participantes simultáneos via web** ✓
3. **Experiencia fluida en tiempo real** ✓
4. **Resultados precisos y confiables** ✓
5. **Historial persistente en archivos** ✓

#### 📊 Métricas de Rendimiento
- **Latencia**: Máximo 2 segundos entre pregunta y respuesta
- **Capacidad**: Soportar 10-15 participantes simultáneos
- **Estabilidad**: Funcionar 2+ horas sin errores
- **Compatibilidad**: Trabajar en Chrome, Firefox, Safari
- **Red**: Funcionar en WiFi doméstica estándar

#### 🎮 Experiencia de Usuario
- **Administrador**: Interface intuitiva, sin necesidad de manual
- **Participantes**: Acceso simple con solo nombre
- **Fluidez**: Transiciones suaves entre preguntas
- **Feedback**: Respuesta visual inmediata a acciones

### 📏 LIMITACIONES ACEPTADAS

#### 👥 Capacidad
- **Participantes**: Máximo 20 simultáneos
- **Preguntas**: Máximo 50 por quiz
- **Sesiones**: Una activa a la vez
- **Quizzes**: Sin límite, depende del almacenamiento

#### 🌐 Conectividad
- **Red local únicamente**: Mismo WiFi/LAN
- **Sin persistencia de sesión**: Si se cierra, se pierde progreso
- **Sin recuperación automática**: Reconexión manual si se desconecta

#### 💾 Almacenamiento
- **Solo archivos locales**: No hay backup automático
- **Sin versionado**: No historial de cambios en quizzes
- **Sin sincronización**: No hay múltiples administradores

---

## 🚀 FASES DE IMPLEMENTACIÓN

### 📅 CRONOGRAMA SUGERIDO

#### **Fase 1: MVP Básico** (2 semanas)
- [ ] Estructura de proyecto y archivos
- [ ] Ventana Tkinter básica
- [ ] Servidor Flask mínimo
- [ ] CRUD básico de quizzes
- [ ] Página web simple para participantes

#### **Fase 2: Funcionalidad Core** (2 semanas)
- [ ] Sistema de sesiones en vivo
- [ ] WebSockets para tiempo real
- [ ] Control completo desde Tkinter
- [ ] Interfaz participante completa
- [ ] Sistema de puntajes

#### **Fase 3: Refinamiento** (1 semana)
- [ ] Historial y estadísticas
- [ ] Mejoras de UI/UX
- [ ] Manejo de errores
- [ ] Optimización de rendimiento
- [ ] Testing y debugging

### 🎯 ENTREGABLES POR FASE

#### **MVP (Fase 1)**
- Aplicación Tkinter funcional para crear quizzes
- Servidor web que sirve páginas básicas
- Participantes pueden unirse y responder
- Datos se guardan en archivos JSON

#### **Versión Completa (Fase 2)**
- Control total del flujo desde administración
- Experiencia tiempo real para participantes
- Ranking y puntajes precisos
- Interfaz pulida y profesional

#### **Versión Final (Fase 3)**
- Sistema de historial completo
- Reportes y estadísticas
- Documentación completa
- Producto listo para uso

---

## 📋 CHECKLIST DE VALIDACIÓN

### ✅ CRITERIOS DE ACEPTACIÓN FINAL

#### 🎯 Funcionalidad
- [ ] Crear quiz con 10+ preguntas desde Tkinter
- [ ] 10 participantes pueden jugar simultáneamente
- [ ] Resultados son precisos y consistentes
- [ ] Historial se guarda correctamente
- [ ] Sistema es estable durante 1+ hora

#### 🎨 Usabilidad
- [ ] Administrador puede usar sin capacitación
- [ ] Participantes entienden interfaz inmediatamente
- [ ] No hay errores confusos o críticos
- [ ] Experiencia es fluida y entretenida

#### 🔧 Técnico
- [ ] Código está documentado y organizado
- [ ] Manejo de errores implementado
- [ ] Configuración es simple
- [ ] Performance es aceptable en hardware estándar

---

**Este alcance define claramente qué se incluye y qué no en tu proyecto de plataforma de quizzes, asegurando expectativas realistas y un desarrollo enfocado.** 🎯
