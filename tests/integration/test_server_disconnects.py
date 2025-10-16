import time

def test_abrupt_disconnect_others_continue(server, connect_fn, send_line_fn, recv_line_fn):
    addr = server.address
    s1, r1, w1 = connect_fn(addr)
    s2, r2, w2 = connect_fn(addr)
    try:
        time.sleep(0.05)
        send_line_fn(w1, "hola")
        assert recv_line_fn(r1) == "hola"
        assert recv_line_fn(r2) == "hola"

        # desconexión abrupta del c2
        r2.close(); w2.close(); s2.close()
        time.sleep(0.05)  # <- dar tiempo a limpiar el cliente caído

        send_line_fn(w1, "sigo")
        assert recv_line_fn(r1) == "sigo"
    finally:
        r1.close(); w1.close(); s1.close()
