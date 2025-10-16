import threading
import time

def test_clients_bursts(server, connect_fn, recv_line_fn):
    addr = server.address
    n_clients = 4
    bursts_per_client = 3

    conns = [connect_fn(addr) for _ in range(n_clients)]
    try:
        time.sleep(0.05)

        def worker(i):
            s, r, w = conns[i]
            for j in range(bursts_per_client):
                w.write(f"c{i}-b{j}\n"); w.flush()
                # un mini delay reduce colisiones extremas
                time.sleep(0.01)

        threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(n_clients)]
        [t.start() for t in threads]
        [t.join(timeout=2.0) for t in threads]

        expected_total = n_clients * bursts_per_client
        expected_set = {f"c{i}-b{j}" for i in range(n_clients) for j in range(bursts_per_client)}

        # cada cliente debe recibir todos los mensajes
        for s, r, w in conns:
            got = []
            deadline = time.time() + 4.0
            while len(got) < expected_total and time.time() < deadline:
                line = recv_line_fn(r, total_timeout=0.2)
                if line is not None:
                    got.append(line)
            assert set(got) == expected_set, f"faltan: {expected_set - set(got)}"
    finally:
        for s, r, w in conns:
            try: r.close(); w.close(); s.close()
            except: pass
