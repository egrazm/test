"""
Servidor de chat con sockets TCP (line-based).
- UTF-8
- Mensajes delimitados por '\n'
- Broadcast a todos (incluye emisor)
- Mensajes inválidos -> "ERR Invalid message"
"""

import socket
import threading
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

    @property
    def address(self) -> tuple[str, int]:
        """Devuelve (host, port) real (útil para pruebas)."""
        if self._sock is None:
            return (self.host, self.port)
        return self._sock.getsockname()

    # -------- ciclo de vida --------

    def start(self):
        """Inicializa el socket y arranca el hilo de aceptación."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(100)
        self._running.set()
        self._accept_thread = threading.Thread(
            target=self._accept_loop, name="accept-loop", daemon=True
        )
        self._accept_thread.start()

    def stop(self):
        """Detiene el servidor y cierra todos los clientes."""
        self._running.clear()
        try:
            if self._sock:
                # cerrar el listen socket para desbloquear accept()
                self._sock.close()
        except Exception:
            pass

        # cerrar clientes
        with self._lock:
            for sock, rf, wf in list(self._clients):
                try:
                    rf.close()
                except Exception:
                    pass
                try:
                    wf.close()
                except Exception:
                    pass
                try:
                    sock.close()
                except Exception:
                    pass
            self._clients.clear()

        # esperar fin del hilo de aceptación
        if self._accept_thread:
            self._accept_thread.join(timeout=1.0)
            self._accept_thread = None

    # -------- bucles internos --------

    def _accept_loop(self):
        assert self._sock is not None
        while self._running.is_set():
            try:
                client_sock, _ = self._sock.accept()
            except OSError:
                # socket cerrado al hacer stop()
                break
            thread = threading.Thread(
                target=self._client_loop, args=(client_sock,), daemon=True
            )
            thread.start()

    def _client_loop(self, client_sock: socket.socket):
        rf, wf = wrap(client_sock)
        with self._lock:
            self._clients.append((client_sock, rf, wf))

        try:
            while self._running.is_set():
                msg = recv_line(rf)
                if msg is None:  # EOF -> cliente se fue
                    break

                if not is_valid_message(msg):
                    # avisar solo al emisor
                    try:
                        send_line(wf, "ERR Invalid message")
                    except Exception:
                        pass
                    continue

                # retransmitir a todos (incluye emisor)
                self.broadcast(msg)

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
            try:
                rf.close()
            except Exception:
                pass
            try:
                wf.close()
            except Exception:
                pass
            try:
                client_sock.close()
            except Exception:
                pass

    # -------- API --------

    def broadcast(self, text: str):
        """Envía `text` a todos los clientes conectados."""
        muertos: List[Client] = []
        with self._lock:
            for sock, rf, wf in list(self._clients):  # <- iterar sobre copia
                try:
                    send_line(wf, text)
                except Exception:
                    muertos.append((sock, rf, wf))

            for sock, rf, wf in muertos:
                try:
                    self._clients.remove((sock, rf, wf))
                except ValueError:
                    pass
                for closee in (rf, wf, sock):
                    try:
                        closee.close()
                    except Exception:
                        pass
