"""
Servidor de chat con sockets TCP.
Día 1: estructura de clase y métodos; implementaremos en Día 3.
"""

import socket
import threading
from typing import List, Tuple

class ChatServer:
    def __init__(self, host="127.0.0.1", port=0):
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None
        self._clients: List[Tuple[socket.socket, object, object]] = []  # (sock, rf, wf)
        self._lock = threading.RLock()
        self._running = threading.Event()
        self._accept_thread: threading.Thread | None = None

    @property
    def address(self) -> tuple[str, int]:
        """Devuelve (host, port) real en uso (útil para pruebas)."""
        if self._sock is None:
            return (self.host, self.port)
        return self._sock.getsockname()

    def start(self):
        """Inicia el socket y el hilo de aceptación de clientes."""
        # Día 3: implementar
        pass

    def stop(self):
        """Detiene el servidor y cierra clientes."""
        # Día 3: implementar
        pass

    def _accept_loop(self):
        """Bucle que acepta clientes y crea hilos por cliente."""
        # Día 3: implementar
        pass

    def _client_loop(self, client_sock: socket.socket):
        """Maneja un cliente: lectura por líneas, validación y broadcast."""
        # Día 3: implementar
        pass

    def broadcast(self, text: str):
        """Envía `text` a todos los clientes conectados."""
        # Día 3: implementar
        pass
