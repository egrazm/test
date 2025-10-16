import time

def test_single_client_broadcasts_to_self(server, connect_fn, send_line_fn, recv_line_fn):
    addr = server.address
    s1, r1, w1 = connect_fn(addr)
    try:
        time.sleep(0.05)  # <- dar tiempo a que el hilo del cliente arranque
        send_line_fn(w1, "hola")
        assert recv_line_fn(r1) == "hola"
    finally:
        r1.close(); w1.close(); s1.close()

def test_invalid_message_returns_err(server, connect_fn, send_line_fn, recv_line_fn):
    addr = server.address
    s1, r1, w1 = connect_fn(addr)
    try:
        time.sleep(0.05)
        send_line_fn(w1, "   ")
        assert recv_line_fn(r1) == "ERR Invalid message"
    finally:
        r1.close(); w1.close(); s1.close()
