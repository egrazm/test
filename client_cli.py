import socket
import sys
import threading

def recv_loop(rf, stop_event):
    try:
        while not stop_event.is_set():
            line = rf.readline()
            if line == "":
                print("\n[client] servidor cerró la conexión.")
                stop_event.set()
                break
            print(f"\r[recv] {line.rstrip()}\n> ", end="", flush=True)
    except Exception:
        # Cierre o error: salimos del loop
        stop_event.set()

def main():
    if len(sys.argv) != 3:
        print("Uso: python client_cli.py <host> <port>")
        sys.exit(1)

    host, port = sys.argv[1], int(sys.argv[2])
    s = socket.create_connection((host, port))
    rf = s.makefile("r", encoding="utf-8", newline="\n")
    wf = s.makefile("w", encoding="utf-8", newline="\n")

    stop_event = threading.Event()
    t = threading.Thread(target=recv_loop, args=(rf, stop_event), daemon=True)
    t.start()

    print(f"[client] conectado a {host}:{port}. Escribe y Enter. Ctrl+C para salir.")
    try:
        while not stop_event.is_set():
            line = input("> ")
            wf.write(line.rstrip("\r\n") + "\n")
            wf.flush()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        try: rf.close()
        except: pass
        try: wf.close()
        except: pass
        try: s.close()
        except: pass
        print("\n[client] bye")

if __name__ == "__main__":
    main()
