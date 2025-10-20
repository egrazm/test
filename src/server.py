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
        self.sock: socket.socket | None = None
        self.clients: List[Client] = []
        self.lock = threading.RLock()
        self.running = threading.Event()
        self.accept_thread: threading.Thread | None = None

        # Cola de mensajes y thread broadcaster (orden global)
        self.msg_q: "queue.Queue[str | None]" = queue.Queue()
        self.bcast_thread: threading.Thread | None = None

    @property
    def address(self) -> tuple[str, int]:
        """Devuelve (host, port) real (útil para pruebas)."""
        if self.sock is None:
            return (self.host, self.port)
        return self.sock.getsockname()

    # -------- ciclo de vida --------

    def start(self):
        """Inicializa el socket y arranca los hilos de aceptación y broadcast."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(100)
        self.running.set()

        self.accept_thread = threading.Thread(
            target=self.accept_loop, name="accept-loop", daemon=True
        )
        self.accept_thread.start()

        # Hilo para difundir mensajes en orden global
        self.bcast_thread = threading.Thread(
            target=self.broadcast_loop, name="broadcast-loop", daemon=True
        )
        self.bcast_thread.start()

    def stop(self):
        """Detiene el servidor y cierra todos los clientes."""
        self.running.clear()
        try:
            if self.sock:
                # cerrar el listen socket para desbloquear accept()
                self.sock.close()
        except Exception:
            pass

        # Avisar al broadcaster que debe terminar (centinela)
        try:
            self.msg_q.put(None)
        except Exception:
            pass

        # Cerrar clientes
        with self.lock:
            for sock, rf, wf in list(self.clients):
                for closee in (rf, wf, sock):
                    try:
                        closee.close()
                    except Exception:
                        pass
            self.clients.clear()

        # Esperar fin de hilos
        if self.accept_thread:
            self.accept_thread.join(timeout=1.0)
            self.accept_thread = None

        if self.bcast_thread:
            self.bcast_thread.join(timeout=1.0)
            self.bcast_thread = None

    # -------- bucles internos --------

    def accept_loop(self):
        assert self.sock is not None
        while self.running.is_set():
            try:
                client_sock, _ = self.sock.accept()
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
            with self.lock:
                self.clients.append((client_sock, rf, wf))

            # Ahora sí, arrancamos el lector
            thread = threading.Thread(
                target=self.client_loop,
                args=(client_sock, rf, wf),
                daemon=True,
            )
            thread.start()

    def client_loop(self, client_sock: socket.socket, rf, wf):
        try:
            while self.running.is_set():
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
                self.msg_q.put(msg)

        except Exception:
            # errores por desconexión o EPIPE: ignoramos y limpiamos
            pass
        finally:
            # remover y cerrar recursos de este cliente
            with self.lock:
                try:
                    self.clients.remove((client_sock, rf, wf))
                except ValueError:
                    pass
            for closee in (rf, wf, client_sock):
                try:
                    closee.close()
                except Exception:
                    pass

    def broadcast_loop(self):
        """Toma mensajes de la cola y los difunde en un único hilo para preservar orden global."""
        while True:
            try:
                item = self.msg_q.get(timeout=0.1)
            except queue.Empty:
                if not self.running.is_set():
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
        with self.lock:
            clients_snapshot = list(self.clients)
        muertos: List[Client] = []
        for sock, rf, wf in clients_snapshot:
            try:
                send_line(wf, text)
            except Exception:
                muertos.append((sock, rf, wf))
        if muertos:
            with self.lock:
                for sock, rf, wf in muertos:
                    if (sock, rf, wf) in self.clients:
                        self.clients.remove((sock, rf, wf))
                    for c in (rf, wf, sock):
                        try:
                            c.close()
                        except:
                            pass
