import threading
import time
import itertools

import pytest

def _send_and_collect(wf, rf, msg, recv_line_fn):
    # enviar y luego leer una línea de vuelta para no perder eco
    wf.write(msg + "\n"); wf.flush()
    return recv_line_fn(rf)

def _recv_many(rf, recv_line_fn, expected_count, total_timeout=3.0):
    """
    Lee hasta expected_count mensajes (o agota tiempo).
    Devuelve la lista de recibidos (sin \n).
    """
    received = []
    deadline = time.time() + total_timeout
    while len(received) < expected_count and time.time() < deadline:
        line = recv_line_fn(rf, total_timeout=0.2)  # reutiliza tu fixture con retries
        if line is not None:
            received.append(line)
    return received

def test_many_clients_send_concurrently(server, connect_fn, recv_line_fn):
    """
    Conecta N clientes, todos envían 1 mensaje 'al mismo tiempo'.
    Verifica que cada cliente recibe N mensajes (incluye el suyo).
    """
    addr = server.address
    N = 6

    conns = [connect_fn(addr) for _ in range(N)]
    try:
        # pequeña pausa para que los hilos del server arranquen
        time.sleep(0.08)

        # barrera para disparar casi juntos
        barrier = threading.Barrier(N)
        msgs = [f"m{i}" for i in range(N)]

        def worker(i):
            s, r, w = conns[i]
            barrier.wait(timeout=1.0)
            w.write(msgs[i] + "\n"); w.flush()

        threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(N)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=1.5)

        # Cada cliente debería recibir N mensajes (orden por llegada al server)
        for s, r, w in conns:
            got = _recv_many(r, recv_line_fn, expected_count=N, total_timeout=3.0)
            # Aceptamos que el orden puede variar por carrera, pero el conjunto debe coincidir
            # 🔴 Descomenta la siguiente línea para forzar un fallo (TDD modo "RED")
            #assert got == msgs, f"orden esperado {msgs} pero recibí {got}"

            # 🟢 Línea original (modo "GREEN", test debería pasar)
            assert set(got) == set(msgs), f"esperaba {set(msgs)} pero recibí {got}"


    finally:
        for s, r, w in conns:
            try: r.close(); w.close(); s.close()
            except: pass
