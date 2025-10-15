import socket
from protocol import wrap, recv_line

def test_recv_line_respects_timeout_and_returns_none_on_eof():
    # socketpair existe en Windows desde Py3.8; en 3.13 OK
    s1, s2 = socket.socketpair()
    try:
        rf, wf = wrap(s1)
        # cerramos el peer para provocar EOF inmediato
        s2.close()
        # pasamos timeout != None para cubrir líneas 28-31
        out = recv_line(rf, timeout=0.05)
        assert out is None  # EOF -> None
    finally:
        try: rf.close()
        except: pass
        try: wf.close()
        except: pass
        try: s1.close()
        except: pass
