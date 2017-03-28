#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xmlrpc.server import SimpleXMLRPCServer

class KeyValueServer:
    _rpc_methods_ = ['login', 'renewal', 'deposit', 'withdraw', 'transfer']
    def __init__(self, address):
        self._serv = SimpleXMLRPCServer(address, allow_none=True)
        for name in self._rpc_methods_:
            self._serv.register_function(getattr(self, name))

    def login(self, secret_key):
        print(secret_key)
        resp = {'sequence': secret_key['sequence'],
                'token': '1234567890',
                'staus': 0,
                'expiration': 36000,
                'msg': ''}
        return resp

    def renewal(self, secret_key):
        print(secret_key)
        resp = {'sequence': secret_key['sequence'],
                'token': secret_key['token'],
                'status': 0,
                'msg': ''}
        return resp

    def deposit(self, secret_key):
        print(secret_key)
        resp = {'sequence': secret_key['sequence'],
                'token': secret_key['token'],
                'status': 0,
                'msg': ''}
        return resp

    def withdraw(self, secret_key):
        print(secret_key)
        resp = {'sequence': secret_key['sequence'],
                'token': secret_key['token'],
                'status': 0,
                'msg': ''}
        return resp

    def transfer(self, secret_key):
        print(secret_key)
        resp = {'sequence': secret_key['sequence'],
                'token': secret_key['token'],
                'status': 0,
                'msg': ''}
        return resp

    def serve_forever(self):
        self._serv.serve_forever()

if __name__ == '__main__':
    kvserv = KeyValueServer(('', 4000))
    kvserv.serve_forever()
