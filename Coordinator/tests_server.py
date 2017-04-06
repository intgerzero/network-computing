#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import socket


def transaction_server_test():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 4001))
    s.listen(5)
    while True:
        client, addr = s.accept()
        print("connected: {}".format(addr))
        msg = client.recv(1024).decode('utf-8')
        print(msg)
        trans_1_recv = json.loads(msg)
        trans_1_ack = {'sequence': trans_1_recv['sequence'], 'status': '0'}
        payload = json.dumps(trans_1_ack).encode('utf-8')
        client.sendall(payload)
        msg = client.recv(1024).decode('utf-8')
        print(msg)
        client.sendall(payload)

if __name__ == '__main__':
    transaction_server_test()
