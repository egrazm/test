from src.server import ChatServer
import signal
import sys
import time

def main():
    srv = ChatServer(host="127.0.0.1", port=0)
    srv.start()
    h, p = srv.address
    print(f"[server] listening on {h}:{p}. Press Ctrl+C to stop.")

    def _stop(*args):
        print("\n[server] stopping...")
        srv.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    # dormir “para siempre” hasta que llegue la señal
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        _stop()

if __name__ == "__main__":
    main()
