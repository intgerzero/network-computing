#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from auth import ClientAuth
from xmlrpc.server import SimpleXMLRPCServer

class Coordinator:
    _rpc_methods_ = ['login', 'renewal', 'deposit', 'withdraw', 'transfer']
    def __init__(self, address):
        self._serv = SimpleXMLRPCServer(address, allow_none=True)
        for name in self._rpc_methods_:
            self._serv.register_function(getattr(self, name))
        # MySQL Server
        self.auth = ClientAuth();

    def login(self, info):
        result = self.auth.client_auth(info)
        resp = {'sequence': info['sequence'],
                'token': '',
                'expiration': 36000,
                'msg': ''}
        if result[0] == True:
            resp['status'] = 0
            resp['token'] = result[1]
        else:
            resp['status'] = 1
            resp['msg'] = result[1] 
        return resp

    def renewal(self, info):
        result = self.auth.token_renewal(info)
        resp = {'sequence': info['sequence'],
                'token': '',
                'msg': ''}
        if result[0] == True:
            resp['status'] = 0
            resp['token'] = result[1]
        else:
            resp['status'] = 1
            resp['msg'] = result[1]
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
    kvserv = Coordinator(('', 4000))
    kvserv.serve_forever()
