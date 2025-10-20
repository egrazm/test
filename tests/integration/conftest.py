import pytest
import socket
import time
from src.server import ChatServer


@pytest.fixture(scope="function")
def server():
    srv = ChatServer(host="127.0.0.1", port=0)
    srv.start()
    try:
        yield srv
    finally:
        srv.stop()


@pytest.fixture
def connect_fn():
    def connect(addr: tuple[str, int], timeout: float = 1.0):
        s = socket.create_connection(addr, timeout=timeout)
        rf = s.makefile("r", encoding="utf-8", newline="\n")
        wf = s.makefile("w", encoding="utf-8", newline="\n")
        return s, rf, wf
    return connect


@pytest.fixture
def send_line_fn():
    def send(wf, text: str):
        wf.write(text.rstrip("\r\n") + "\n")
        wf.flush()
    return send


@pytest.fixture
def recv_line_fn():
    """
    Lee una línea con reintentos cortos hasta total_timeout.
    Devuelve str o None si no llega nada.
    """
    def recv(rf, total_timeout: float = 2.0, step: float = 0.02):
        deadline = time.time() + total_timeout
        while time.time() < deadline:
            try:
                rf.buffer.raw._sock.settimeout(step)  # type: ignore[attr-defined]
            except Exception:
                pass
            try:
                line = rf.readline()
                if line == "":
                    return None
                return line.rstrip("\n")
            except Exception:
                time.sleep(step)
        return None
    return recv
