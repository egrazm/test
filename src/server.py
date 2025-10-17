"""
Servidor de chat con sockets TCP (line-based).
- UTF-8
- Mensajes delimitados por '\n'
- Broadcast a todos (incluye emisor)
- Mensajes inválidos -> "ERR Invalid message"
"""

import socket
import threading
import queue
import time
from typing import List, Tuple

from src.validation import is_valid_message
from src.protocol import wrap, send_line, recv_line

Client = Tuple[socket.socket, object, object]  # (sock, rf, wf)


class ChatServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 0):
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None
        self._clients: List[Client] = []
        self._lock = threading.RLock()
        self._running = threading.Event()
        self._accept_thread: threading.Thread | None = None

        # Cola de mensajes y thread broadcaster (orden global)
        self._msg_q: "queue.Queue[str | None]" = queue.Queue()
        self._bcast_thread: threading.Thread | None = None

    @property
    def address(self) -> tuple[str, int]:
        """Devuelve (host, port) real (útil para pruebas)."""
        if self._sock is None:
            return (self.host, self.port)
        return self._sock.getsockname()

    # -------- ciclo de vida --------

    def start(self):
        """Inicializa el socket y arranca los hilos de aceptación y broadcast."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(100)
        self._running.set()

        self._accept_thread = threading.Thread(
            target=self._accept_loop, name="accept-loop", daemon=True
        )
        self._accept_thread.start()

        # Hilo para difundir mensajes en orden global
        self._bcast_thread = threading.Thread(
            target=self._broadcast_loop, name="broadcast-loop", daemon=True
        )
        self._bcast_thread.start()

    def stop(self):
        """Detiene el servidor y cierra todos los clientes."""
        self._running.clear()
        try:
            if self._sock:
                # cerrar el listen socket para desbloquear accept()
                self._sock.close()
        except Exception:
            pass

        # Avisar al broadcaster que debe terminar (centinela)
        try:
            self._msg_q.put(None)
        except Exception:
            pass

        # Cerrar clientes
        with self._lock:
            for sock, rf, wf in list(self._clients):
                for closee in (rf, wf, sock):
                    try:
                        closee.close()
                    except Exception:
                        pass
            self._clients.clear()

        # Esperar fin de hilos
        if self._accept_thread:
            self._accept_thread.join(timeout=1.0)
            self._accept_thread = None

        if self._bcast_thread:
            self._bcast_thread.join(timeout=1.0)
            self._bcast_thread = None

    # -------- bucles internos --------

    def _accept_loop(self):
        assert self._sock is not None
        while self._running.is_set():
            try:
                client_sock, _ = self._sock.accept()
            except OSError:
                # socket cerrado al hacer stop()
                break

            # Optimización de latencia
            try:
                client_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            except Exception:
                pass

            # *** REGISTRO INMEDIATO DEL CLIENTE ***
            rf, wf = wrap(client_sock)
            with self._lock:
                self._clients.append((client_sock, rf, wf))

            # Ahora sí, arrancamos el lector
            thread = threading.Thread(
                target=self._client_loop,
                args=(client_sock, rf, wf),
                daemon=True,
            )
            thread.start()

    def _client_loop(self, client_sock: socket.socket, rf, wf):
        try:
            while self._running.is_set():
                msg = recv_line(rf)
                if msg is None:  # EOF o timeout -> cliente se fue
                    break

                if not is_valid_message(msg):
                    # avisar solo al emisor
                    try:
                        send_line(wf, "ERR Invalid message")
                    except Exception:
                        pass
                    continue

                # Encolar para garantizar orden global de difusión
                self._msg_q.put(msg)

        except Exception:
            # errores por desconexión o EPIPE: ignoramos y limpiamos
            pass
        finally:
            # remover y cerrar recursos de este cliente
            with self._lock:
                try:
                    self._clients.remove((client_sock, rf, wf))
                except ValueError:
                    pass
            for closee in (rf, wf, client_sock):
                try:
                    closee.close()
                except Exception:
                    pass

    def _broadcast_loop(self):
        """Toma mensajes de la cola y los difunde en un único hilo para preservar orden global."""
        while True:
            try:
                item = self._msg_q.get(timeout=0.1)
            except queue.Empty:
                if not self._running.is_set():
                    break
                continue
            if item is None:  # centinela de stop()
                break

            # --- micro-batching para capturar clientes recién aceptados ---
            # Pequeña pausa para que el hilo de accept termine de registrar conexiones
            # concurrentes antes de este broadcast.
            time.sleep(0.005)

            self.broadcast(item)


    # -------- API --------

    def broadcast(self, text: str):
        with self._lock:
            clients_snapshot = list(self._clients)
        muertos: List[Client] = []
        for sock, rf, wf in clients_snapshot:
            try:
                send_line(wf, text)   # <- debe hacer flush por dentro
            except Exception:
                muertos.append((sock, rf, wf))
        if muertos:
            with self._lock:
                for sock, rf, wf in muertos:
                    if (sock, rf, wf) in self._clients:
                        self._clients.remove((sock, rf, wf))
                    for c in (rf, wf, sock):
                        try: c.close()
                        except: pass
