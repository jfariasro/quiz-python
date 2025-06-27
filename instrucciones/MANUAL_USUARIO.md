# 📚 MANUAL DE USUARIO - PLATAFORMA DE QUIZZES

## 👋 INTRODUCCIÓN

### 🎯 ¿QUÉ ES ESTA PLATAFORMA?
Esta es una aplicación completa para crear y ejecutar quizzes interactivos tipo Kahoot! que permite:
- **Administradores**: Crear quizzes desde una aplicación de escritorio
- **Participantes**: Jugar desde cualquier navegador web conectándose via WiFi
- **Experiencia en tiempo real**: Todos ven preguntas y resultados simultáneamente

### 👥 USUARIOS DE LA PLATAFORMA
- **Administrador/Anfitrión**: Quien crea y controla los quizzes (usa la app de escritorio)
- **Participantes**: Quienes responden las preguntas (usan navegador web en celular/tablet/laptop)

---

## 🚀 INICIO RÁPIDO

### ⚡ PASOS PARA EMPEZAR
1. **Abrir la aplicación** de escritorio
2. **Crear un quiz** con preguntas y respuestas
3. **Iniciar el servidor** para que otros se conecten
4. **Compartir la dirección** que aparece en pantalla
5. **Los participantes** entran desde sus navegadores
6. **¡Jugar!** 🎮

---

## 🖥️ GUÍA PARA EL ADMINISTRADOR

### 📋 VENTANA PRINCIPAL

#### 🎮 Panel de Control
Al abrir la aplicación verás:
- **Lista de quizzes** disponibles
- **Botón "Nuevo Quiz"** para crear uno nuevo
- **Estado del servidor** (Detenido/Ejecutándose)
- **Dirección IP** para compartir con participantes
- **Panel de participantes** conectados

#### 🔧 CREAR UN NUEVO QUIZ

1. **Clic en "Nuevo Quiz"**
   - Se abre el formulario de creación

2. **Información Básica**
   ```
   Título: "Historia del Perú"
   Descripción: "Quiz sobre eventos históricos peruanos"
   Dificultad: Medio
   ```

3. **Agregar Preguntas**
   - Clic en "Agregar Pregunta"
   - Escribir la pregunta: "¿En qué año fue fundado Lima?"
   - Agregar opciones:
     * 1535 ✓ (correcta)
     * 1532
     * 1540
     * 1545
   - Establecer puntos: 100
   - Tiempo límite: 30 segundos

4. **Configuraciones del Quiz**
   - ☑️ Mezclar preguntas
   - ☑️ Mostrar respuesta correcta
   - ☑️ Puntos por velocidad
   - Tiempo entre preguntas: 5 segundos

5. **Guardar el Quiz**
   - Clic en "Guardar Quiz"
   - ¡Listo para usar!

#### 🎯 EJECUTAR UNA SESIÓN EN VIVO

1. **Seleccionar Quiz**
   - Hacer clic en un quiz de la lista
   - Ver vista previa de preguntas

2. **Iniciar Servidor**
   - Clic en "Iniciar Servidor"
   - Aparecerá la dirección IP: `http://192.168.1.100:5000`
   - Compartir esta dirección con los participantes

3. **Esperar Participantes**
   - Los participantes aparecerán en la lista
   - Ver nombres y estado de conexión

4. **Comenzar el Quiz**
   - Clic en "Iniciar Quiz"
   - Controlar el flujo:
     * "Siguiente Pregunta" (manual)
     * "Pausar/Reanudar"
     * "Terminar Quiz"

5. **Monitorear en Vivo**
   - Ver respuestas llegando en tiempo real
   - Ranking actualizado automáticamente
   - Estadísticas por pregunta

#### 📊 VER RESULTADOS E HISTORIAL

1. **Resultados de la Sesión Actual**
   - Al terminar, ver podio automáticamente
   - Estadísticas detalladas
   - Exportar resultados

2. **Historial de Sesiones**
   - Clic en "Historial"
   - Lista de partidas anteriores
   - Detalles por sesión:
     * Participantes y puntajes
     * Duración de la partida
     * Preguntas más difíciles

3. **Estadísticas Generales**
   - Promedio de participantes
   - Quizzes más populares
   - Rendimiento por pregunta

---

## 📱 GUÍA PARA PARTICIPANTES

### 🚪 UNIRSE A UN QUIZ

#### 📲 PASO 1: CONECTARSE
1. **Abrir navegador** en tu dispositivo (celular, tablet, laptop)
2. **Ir a la dirección** que te dio el administrador
   ```
   Ejemplo: http://192.168.1.100:5000
   ```
3. **Asegurarte** de estar en la misma red WiFi

#### 👤 PASO 2: INGRESAR NOMBRE
1. **Escribir tu nombre** en el campo
   - Usar nombre único (no repetido)
   - Máximo 20 caracteres
   - Sin caracteres especiales

2. **Clic en "Unirse"**
   - Si el nombre está disponible, entrarás al lobby
   - Si está ocupado, deberás cambiar el nombre

#### ⏳ PASO 3: SALA DE ESPERA (LOBBY)
- **Ver otros participantes** que ya se conectaron
- **Esperar** a que el administrador inicie el quiz
- **Leer las instrucciones** que aparecen en pantalla

### 🎮 DURANTE EL QUIZ

#### 🎯 RESPONDER PREGUNTAS

1. **Leer la pregunta** que aparece en pantalla
2. **Ver las opciones** disponibles (generalmente 4)
3. **Tocar/hacer clic** en tu respuesta
4. **Esperar confirmación**:
   - ✅ Verde = Correcto
   - ❌ Rojo = Incorrecto
   - Se muestra la respuesta correcta

#### ⚡ SISTEMA DE PUNTAJES
- **Respuesta correcta**: Puntos base (ej: 100 puntos)
- **Bonus por velocidad**: Más puntos si respondes rápido
- **Respuesta incorrecta**: 0 puntos
- **Sin respuesta**: 0 puntos

#### 📊 VER TU PROGRESO
- **Puntaje actual** visible en todo momento
- **Posición en el ranking** actualizada después de cada pregunta
- **Número de pregunta actual** (ej: "3 de 10")

### 🏆 RESULTADOS FINALES

#### 🥇 PODIO
Al finalizar el quiz verás:
- **Top 3 participantes** con sus puntajes
- **Tu posición final** destacada
- **Tu puntaje total** y porcentaje de aciertos

#### 📈 ESTADÍSTICAS PERSONALES
- Número de respuestas correctas
- Tiempo promedio de respuesta
- Mejor racha de respuestas consecutivas
- Comparación con el promedio del grupo

---

## 🔧 CONFIGURACIÓN Y AJUSTES

### ⚙️ CONFIGURACIONES DEL SISTEMA

#### 🌐 CONFIGURACIÓN DE RED
- **IP Automática**: El sistema detecta tu IP local automáticamente
- **Puerto**: Por defecto usa el puerto 5000
- **Firewall**: Asegúrate de que el puerto esté abierto

#### 🎨 PREFERENCIAS DE INTERFAZ
- **Tema**: Claro u oscuro
- **Tamaño de fuente**: Pequeño, mediano, grande
- **Sonidos**: Activar/desactivar efectos de sonido

#### 📊 CONFIGURACIONES DE QUIZ
- **Tiempo por defecto**: 30 segundos por pregunta
- **Puntos por defecto**: 100 puntos por respuesta correcta
- **Máximo participantes**: 20 (configurable)

### 📁 GESTIÓN DE ARCHIVOS

#### 💾 RESPALDOS AUTOMÁTICOS
- Los quizzes se guardan automáticamente
- Historial se mantiene por fecha
- Respaldo de seguridad cada 24 horas

#### 📤 EXPORTAR/IMPORTAR
- **Exportar quiz**: Guardar como archivo .json
- **Importar quiz**: Cargar quiz desde archivo
- **Exportar resultados**: Guardar como .csv o .pdf

---

## ❓ SOLUCIÓN DE PROBLEMAS

### 🔌 PROBLEMAS DE CONEXIÓN

#### "No puedo conectarme al quiz"
**Posibles causas y soluciones:**

1. **Diferente red WiFi**
   - ✅ Verificar que estés en la misma red que el administrador
   - ✅ Preguntar el nombre de la red WiFi correcta

2. **Dirección IP incorrecta**
   - ✅ Verificar que hayas escrito bien la dirección
   - ✅ Incluir el puerto `:5000` al final
   - ✅ Ejemplo correcto: `http://192.168.1.100:5000`

3. **Servidor no iniciado**
   - ✅ El administrador debe haber iniciado el servidor
   - ✅ Verificar que aparezca "Servidor: Ejecutándose"

4. **Firewall bloqueando**
   - ✅ El administrador debe permitir el puerto 5000 en su firewall
   - ✅ En Windows: Panel de Control > Sistema y Seguridad > Firewall

#### "La página web no carga"
1. **Limpiar caché del navegador**
   - Chrome: Ctrl+Shift+R
   - Safari: Cmd+R
   - Firefox: Ctrl+F5

2. **Probar otro navegador**
   - Chrome, Firefox, Safari son compatibles
   - Evitar navegadores muy antiguos

3. **Verificar JavaScript**
   - El navegador debe tener JavaScript activado
   - Configuración > Privacidad > JavaScript

### 🎮 PROBLEMAS DURANTE EL JUEGO

#### "No aparecen las preguntas"
1. **Conexión perdida**
   - ✅ Recargar la página (F5)
   - ✅ Verificar conexión WiFi
   - ✅ Volver a ingresar tu nombre

2. **JavaScript deshabilitado**
   - ✅ Activar JavaScript en el navegador
   - ✅ Recargar la página

#### "Mis respuestas no se registran"
1. **Verificar conexión**
   - ✅ Ícono de WiFi debe estar conectado
   - ✅ Intentar abrir otra página web

2. **Timeout de pregunta**
   - ✅ Responder antes de que se acabe el tiempo
   - ✅ Tocar claramente en la opción elegida

### 🖥️ PROBLEMAS EN LA APLICACIÓN DE ADMINISTRACIÓN

#### "No puedo crear un quiz"
1. **Permisos de archivo**
   - ✅ Ejecutar como administrador
   - ✅ Verificar permisos de la carpeta

2. **Espacio en disco**
   - ✅ Liberar espacio en el disco duro
   - ✅ Mínimo 100MB disponibles

#### "El servidor no inicia"
1. **Puerto ocupado**
   - ✅ Cerrar otras aplicaciones que usen el puerto 5000
   - ✅ Reiniciar la aplicación

2. **Antivirus bloqueando**
   - ✅ Agregar excepción en el antivirus
   - ✅ Permitir acceso a la red

---

## 💡 CONSEJOS Y BUENAS PRÁCTICAS

### 🎯 PARA ADMINISTRADORES

#### 📝 CREANDO QUIZZES EFECTIVOS
- **Preguntas claras**: Usar lenguaje simple y directo
- **Opciones balanceadas**: Evitar opciones obviamente incorrectas
- **Tiempo apropiado**: 30 segundos para preguntas de conocimiento, 45-60 para cálculos
- **Progresión de dificultad**: Empezar fácil, aumentar gradualmente

#### 🎮 DIRIGIENDO SESIONES
- **Explicar las reglas** antes de empezar
- **Dar tiempo** para que todos se conecten
- **Mantener el ritmo** sin prisa pero sin pausa
- **Comentar resultados** interesantes entre preguntas

#### 📊 ANÁLISIS POST-JUEGO
- **Revisar estadísticas** para mejorar preguntas
- **Identificar preguntas problemáticas** (muy fáciles/difíciles)
- **Guardar feedback** de participantes
- **Actualizar quizzes** basado en la experiencia

### 🏆 PARA PARTICIPANTES

#### ⚡ ESTRATEGIAS DE JUEGO
- **Leer completamente** la pregunta antes de responder
- **No cambiar** respuestas ya seleccionadas
- **Mantener la calma** aunque vayas perdiendo
- **Aprender de errores** para mejorar en siguiente ronda

#### 📱 OPTIMIZAR EXPERIENCIA
- **Buena conexión WiFi**: Estar cerca del router
- **Pantalla adecuada**: Tamaño suficiente para leer cómodamente
- **Batería cargada**: Especialmente en dispositivos móviles
- **Ambiente tranquilo**: Sin distracciones durante el juego

---

## 🆘 CONTACTO Y SOPORTE

### 📞 ¿NECESITAS AYUDA?

#### 🔍 AUTODIAGNÓSTICO
1. **Revisar esta guía** - La mayoría de problemas están cubiertos aquí
2. **Verificar requisitos** - Sistema, red, navegador
3. **Reintentar** - A veces una recarga soluciona el problema

#### 💬 REPORTAR PROBLEMAS
Si el problema persiste, anota:
- **Qué estabas haciendo** cuando ocurrió el error
- **Mensaje de error** exacto (captura de pantalla)
- **Dispositivo y navegador** que estás usando
- **Número de participantes** en la sesión

#### 🔄 ACTUALIZACIONES
- Verificar periódicamente si hay **nuevas versiones**
- Leer **notas de lanzamiento** para nuevas características
- Hacer **respaldo de quizzes** antes de actualizar

---

**¡Con esta guía tienes todo lo necesario para usar exitosamente la plataforma de quizzes! 🎉 ¡A crear y jugar!** 🚀
