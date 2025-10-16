def test_broadcast_to_all_in_order(server, connect_fn, send_line_fn, recv_line_fn):
    addr = server.address
    s1, r1, w1 = connect_fn(addr)
    s2, r2, w2 = connect_fn(addr)
    s3, r3, w3 = connect_fn(addr)
    try:
        send_line_fn(w1, "m1")
        send_line_fn(w2, "m2")
        send_line_fn(w3, "m3")

        expected = ["m1", "m2", "m3"]

        assert [recv_line_fn(r1), recv_line_fn(r1), recv_line_fn(r1)] == expected
        assert [recv_line_fn(r2), recv_line_fn(r2), recv_line_fn(r2)] == expected
        assert [recv_line_fn(r3), recv_line_fn(r3), recv_line_fn(r3)] == expected
    finally:
        for r, w, s in [(r1,w1,s1),(r2,w2,s2),(r3,w3,s3)]:
            r.close(); w.close(); s.close()
