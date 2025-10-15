from server import ChatServer

def test_server_start_stop_no_clients_and_broadcast_noop():
    srv = ChatServer(host="127.0.0.1", port=0)
    srv.start()
    try:
        # broadcast sin clientes no debe fallar
        srv.broadcast("ping")
        # address debe estar poblada (host, puerto asignado)
        host, port = srv.address
        assert host == "127.0.0.1"
        assert isinstance(port, int) and port > 0
    finally:
        srv.stop()
