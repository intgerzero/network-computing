#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Client tests scripts
"""

import json
import socket

def auth_test():
    """
    client authentication test
    protocol type '00'
    """
    msg = {'type': '00', 'bankcard': '1234567890', 'password': '01234567890'}
    payload = json.dumps(msg).encode('utf-8')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 4000))
    s.sendall(payload)
    msg = json.loads(s.recv(4096).decode('utf-8'))
    s.close()
    print("auth_test: " + str(msg))
    return msg

def renewal_test(token):
    """
    renewal token expiration time
    protocol type '10'
    """
    msg = {'type': '10', 'bankcard': '1234567890', 'token': token}
    payload = json.dumps(msg).encode('utf-8')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 4000))
    s.sendall(payload)
    msg = s.recv(4096).decode('utf-8')
    print("renewal_test: " + str(msg))
    s.close()

def transaction_test(token):
    """
    transaction test
    protocol type '20' '30' '40'
    """
    msg = {'type': '20', 'token': token, 'bankcard': '1234567890', "amount": "100"}
    payload = json.dumps(msg).encode('utf-8')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 4000))
    s.sendall(payload)
    msg = s.recv(1024).decode('utf-8')
    print("transaction_test: " + str(msg))
    trans_1_recv = json.loads(msg)
    trans_1_ack = {'sequence': trans_1_recv['sequence'], 'status': '0'}
    payload = json.dumps(trans_1_ack).encode('utf-8')
    s.sendall(payload)
    msg = s.recv(1024).decode('utf-8')
    print("transaction_test: " + str(msg))
    trans_2_recv = json.loads(msg)
    if trans_2_recv['status'] == '1':
        return
    trans_2_ack = {'sequence': trans_2_recv['sequence'], 'status': '0'}
    payload = json.dumps(trans_2_ack).encode('utf-8')
    s.sendall(payload)
    s.close()

if __name__ == '__main__':
    msg = auth_test()
    renewal_test(msg['token'])
    transaction_test(msg['token'])
