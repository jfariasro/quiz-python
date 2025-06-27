"""
Utilidades de red para la plataforma de quizzes.
Gestiona detección de IP, conectividad y comunicación de red.
"""

import socket
import threading
import time
import requests
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NetworkUtils:
    """Utilidades para gestión de red y conectividad."""
    
    @staticmethod
    def get_local_ip() -> Optional[str]:
        """
        Obtener la dirección IP local de la máquina.
        
        Returns:
            IP local o None si no se puede determinar
        """
        try:
            # Método más confiable: conectar a una dirección externa
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # No necesita conectarse realmente, solo determinar la ruta
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
            
            logger.info(f"IP local detectada: {local_ip}")
            return local_ip
            
        except Exception as e:
            logger.error(f"Error al detectar IP local: {e}")
            return None
    
    @staticmethod
    def get_all_network_interfaces() -> List[Dict[str, str]]:
        """
        Obtener todas las interfaces de red disponibles.
        
        Returns:
            Lista de interfaces con nombre e IP
        """
        interfaces = []
        
        try:
            import netifaces
            
            for interface in netifaces.interfaces():
                try:
                    addr_info = netifaces.ifaddresses(interface)
                    
                    if netifaces.AF_INET in addr_info:
                        for addr in addr_info[netifaces.AF_INET]:
                            ip = addr.get('addr')
                            if ip and ip != '127.0.0.1':  # Excluir localhost
                                interfaces.append({
                                    'interface': interface,
                                    'ip': ip,
                                    'netmask': addr.get('netmask', ''),
                                    'broadcast': addr.get('broadcast', '')
                                })
                                
                except Exception as e:
                    logger.debug(f"Error al leer interfaz {interface}: {e}")
                    continue
            
            logger.info(f"Encontradas {len(interfaces)} interfaces de red")
            return interfaces
            
        except ImportError:
            logger.warning("netifaces no disponible, usando método alternativo")
            
            # Método alternativo sin netifaces
            hostname = socket.gethostname()
            try:
                ip = socket.gethostbyname(hostname)
                if ip != '127.0.0.1':
                    interfaces.append({
                        'interface': 'default',
                        'ip': ip,
                        'netmask': '',
                        'broadcast': ''
                    })
            except Exception as e:
                logger.error(f"Error al obtener IP por hostname: {e}")
            
            return interfaces
        
        except Exception as e:
            logger.error(f"Error al enumerar interfaces: {e}")
            return []
    
    @staticmethod
    def check_port_available(port: int, host: str = 'localhost') -> bool:
        """
        Verificar si un puerto está disponible.
        
        Args:
            port: Puerto a verificar
            host: Host a verificar (por defecto localhost)
            
        Returns:
            True si el puerto está disponible, False en caso contrario
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                
                # Si connect_ex retorna 0, el puerto está ocupado
                available = result != 0
                
                if available:
                    logger.debug(f"Puerto {port} disponible en {host}")
                else:
                    logger.debug(f"Puerto {port} ocupado en {host}")
                
                return available
                
        except Exception as e:
            logger.error(f"Error al verificar puerto {port}: {e}")
            return False
    
    @staticmethod
    def find_available_port(start_port: int = 5000, end_port: int = 5100) -> Optional[int]:
        """
        Encontrar un puerto disponible en un rango.
        
        Args:
            start_port: Puerto inicial del rango
            end_port: Puerto final del rango
            
        Returns:
            Puerto disponible o None si no hay ninguno libre
        """
        for port in range(start_port, end_port + 1):
            if NetworkUtils.check_port_available(port):
                logger.info(f"Puerto disponible encontrado: {port}")
                return port
        
        logger.warning(f"No se encontró puerto disponible en rango {start_port}-{end_port}")
        return None
    
    @staticmethod
    def test_web_server_connectivity(host: str, port: int, timeout: int = 5) -> bool:
        """
        Probar conectividad con un servidor web.
        
        Args:
            host: Host del servidor
            port: Puerto del servidor
            timeout: Tiempo límite para la conexión
            
        Returns:
            True si el servidor responde, False en caso contrario
        """
        try:
            url = f"http://{host}:{port}"
            response = requests.get(url, timeout=timeout)
            
            success = response.status_code == 200
            
            if success:
                logger.debug(f"Servidor web accesible: {url}")
            else:
                logger.debug(f"Servidor web responde con código {response.status_code}: {url}")
            
            return success
            
        except requests.exceptions.ConnectionError:
            logger.debug(f"No se puede conectar al servidor: {host}:{port}")
            return False
        except requests.exceptions.Timeout:
            logger.debug(f"Timeout al conectar con servidor: {host}:{port}")
            return False
        except Exception as e:
            logger.error(f"Error al probar conectividad: {e}")
            return False
    
    @staticmethod
    def generate_connection_info(host: str, port: int) -> Dict[str, Any]:
        """
        Generar información de conexión para participantes.
        
        Args:
            host: Host del servidor
            port: Puerto del servidor
            
        Returns:
            Diccionario con información de conexión
        """
        info = {
            'host': host,
            'port': port,
            'url': f"http://{host}:{port}",
            'qr_data': f"http://{host}:{port}",
            'instructions': f"Conecta tu dispositivo a la red WiFi y ve a: {host}:{port}"
        }
        
        logger.info(f"Información de conexión generada: {info['url']}")
        return info


class ConnectionMonitor:
    """Monitor de conexiones para el servidor de quizzes."""
    
    def __init__(self, check_interval: int = 30):
        """
        Inicializar monitor de conexiones.
        
        Args:
            check_interval: Intervalo de verificación en segundos
        """
        self.check_interval = check_interval
        self.monitoring = False
        self.monitor_thread = None
        self.connection_callbacks = []
        
        # Estadísticas
        self.stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'last_check': None,
            'last_success': None,
            'last_failure': None
        }
    
    def add_connection_callback(self, callback):
        """
        Agregar callback para eventos de conexión.
        
        Args:
            callback: Función que recibe (success: bool, details: dict)
        """
        self.connection_callbacks.append(callback)
        logger.debug("Callback de conexión agregado")
    
    def remove_connection_callback(self, callback):
        """Remover callback de eventos de conexión."""
        if callback in self.connection_callbacks:
            self.connection_callbacks.remove(callback)
            logger.debug("Callback de conexión removido")
    
    def start_monitoring(self, host: str, port: int):
        """
        Iniciar monitoreo de conexión.
        
        Args:
            host: Host a monitorear
            port: Puerto a monitorear
        """
        if self.monitoring:
            logger.warning("Monitor ya está ejecutándose")
            return
        
        self.host = host
        self.port = port
        self.monitoring = True
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="ConnectionMonitor"
        )
        self.monitor_thread.start()
        
        logger.info(f"Monitor de conexión iniciado para {host}:{port}")
    
    def stop_monitoring(self):
        """Detener monitoreo de conexión."""
        if not self.monitoring:
            return
        
        self.monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        logger.info("Monitor de conexión detenido")
    
    def _monitor_loop(self):
        """Bucle principal del monitor."""
        while self.monitoring:
            try:
                # Realizar verificación
                success = NetworkUtils.test_web_server_connectivity(
                    self.host, self.port, timeout=3
                )
                
                # Actualizar estadísticas
                self.stats['total_checks'] += 1
                self.stats['last_check'] = time.time()
                
                if success:
                    self.stats['successful_checks'] += 1
                    self.stats['last_success'] = time.time()
                else:
                    self.stats['failed_checks'] += 1
                    self.stats['last_failure'] = time.time()
                
                # Notificar callbacks
                details = {
                    'host': self.host,
                    'port': self.port,
                    'timestamp': time.time(),
                    'stats': self.stats.copy()
                }
                
                for callback in self.connection_callbacks:
                    try:
                        callback(success, details)
                    except Exception as e:
                        logger.error(f"Error en callback de conexión: {e}")
                
                # Esperar antes del siguiente check
                if self.monitoring:
                    time.sleep(self.check_interval)
                    
            except Exception as e:
                logger.error(f"Error en monitor de conexión: {e}")
                time.sleep(5)  # Esperar un poco antes de reintentar
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del monitor.
        
        Returns:
            Diccionario con estadísticas
        """
        stats = self.stats.copy()
        
        # Agregar métricas calculadas
        if stats['total_checks'] > 0:
            stats['success_rate'] = stats['successful_checks'] / stats['total_checks']
            stats['failure_rate'] = stats['failed_checks'] / stats['total_checks']
        else:
            stats['success_rate'] = 0.0
            stats['failure_rate'] = 0.0
        
        stats['is_monitoring'] = self.monitoring
        
        return stats


# Función de utilidad para generar códigos QR (opcional)
def generate_qr_code(data: str, size: int = 200) -> Optional[bytes]:
    """
    Generar código QR para facilitar la conexión.
    
    Args:
        data: Datos a codificar (URL del servidor)
        size: Tamaño del código QR en píxeles
        
    Returns:
        Imagen del código QR en bytes o None si hay error
    """
    try:
        import qrcode
        from io import BytesIO
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Redimensionar si es necesario
        if size != img.size[0]:
            img = img.resize((size, size))
        
        # Convertir a bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        logger.info(f"Código QR generado para: {data}")
        return buffer.getvalue()
        
    except ImportError:
        logger.warning("qrcode no disponible - instala: pip install qrcode[pil]")
        return None
    except Exception as e:
        logger.error(f"Error al generar código QR: {e}")
        return None
