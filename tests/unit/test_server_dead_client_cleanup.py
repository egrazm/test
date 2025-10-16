import socket
import time
from server import ChatServer

def test_broadcast_removes_dead_clients_gracefully():
    srv = ChatServer(host="127.0.0.1", port=0)
    srv.start()
    try:
        addr = srv.address
        # conectamos un cliente y lo cerramos antes del broadcast
        s = socket.create_connection(addr, timeout=1.0)
        rf = s.makefile("r", encoding="utf-8", newline="\n")
        wf = s.makefile("w", encoding="utf-8", newline="\n")
        # cierre abrupto del lado cliente
        rf.close(); wf.close(); s.close()
        time.sleep(0.05)  # dar tiempo a que el hilo de cliente se inicie/limpie

        # Esto debe intentar enviar, fallar para ese cliente y limpiarlo sin explotar
        srv.broadcast("hola")

        # si había carreras, un segundo broadcast también debe ser seguro
        srv.broadcast("otra")
    finally:
        srv.stop()
