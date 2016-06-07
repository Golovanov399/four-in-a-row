#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import pickle

sock = socket.socket()
sock.bind(('', 9090))
sock.listen(2)


connections = []
addrs = []

for i in range(2):
    conn, addr = sock.accept()
    connections.append(conn)
    addrs.append(addr)
    print ('connected:', addr)

connections[0].send(pickle.dumps({'player_turn':'x'}))
connections[1].send(pickle.dumps({'player_turn':'o'}))

current_player = 0
closed_connections = 0

while closed_connections < 2:
    conn_in = connections[current_player]
    conn_out = connections[1 - current_player]
    data = pickle.loads(conn_in.recv(1024))
    print ('data=', data)
    if data['ended']:
        connections[current_player].close()
        closed_connections = closed_connections + 1
    conn_out.send(pickle.dumps(data))
    current_player = 1 - current_player



for conn in connections:
    conn.close()

sock.close()