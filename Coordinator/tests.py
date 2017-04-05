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
    print(msg)
    return msg

def renewal_test(token):
    """
    renewal token expiration time
    protocol type '10'
    """
    msg = {'type': '10', 'bankcard': '1234567890', 'token': token, 'deadline': 1590796159}
    payload = json.dumps(msg).encode('utf-8')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 4000))
    s.sendall(payload)
    msg = s.recv(4096).decode('utf-8')
    print(msg)
    s.close()

if __name__ == '__main__':
    msg = auth_test()
    renewal_test(msg['token'])
