"""
Utilidades de protocolo: envolver sockets en interfaces de texto por línea.
"""

import socket

def wrap(sock: socket.socket):
    """
    Devuelve (rf, wf) estilo archivo:
      - rf.readline() lee una línea UTF-8 terminada en '\n'
      - wf.write('texto\\n'); wf.flush() envía una línea
    """
    rf = sock.makefile("r", encoding="utf-8", newline="\n")
    wf = sock.makefile("w", encoding="utf-8", newline="\n")
    return rf, wf

def send_line(wf, text: str):
    """Envía una línea garantizando un único '\\n' final."""
    wf.write(text.rstrip("\r\n") + "\n")
    wf.flush()

def recv_line(rf, timeout=None) -> str | None:
    """
    Lee una línea. Si hay EOF, retorna None.
    (El manejo fino de timeout lo añadiremos más adelante si hace falta.)
    """
    if timeout is not None:
        try:
            rf.buffer.raw._sock.settimeout(timeout)
        except Exception:
            pass
    line = rf.readline()
    if line == "":
        return None
    return line.rstrip("\n")
