#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import hmac
import socket
from xmlrpc.client import ServerProxy

domain = 'localhost'
port = 4000

SUCESS = 0
FAILED = 1

class Client_RPC:
    """
    Client RPC
    https://github.com/intgerzero/network-computing/blob/master/README.md
    see protcol
    """
    __SUCESS__ = 0
    __FAILED__ = 1
    def __init__(self, uri='http://localhost:4000'):
        self.s = ServerProxy(uri, allow_none=True)
        self.sequence = self.generator()

    def generator(self):
        i = 0
        while True:
            value = yield i
            i = (i + 1) % sys.maxsize

    def message(self, flag, args):
        key = dict()
        key['login'] = ('bankcard', 'password')
        key['renewal'] = ('token', 'bankcard')
        key['deposit'] = ('token', 'bankcard', 'amount')
        key['withdraw'] = ('token', 'bankcard', 'amount')
        key['transfer'] = ('token', 'bankcard', 'transferred', 'amount')

        secret_key = dict()
        secret_key['sequence'] = next(self.sequence)
        for i in range(len(key[flag])):
            secret_key[key[flag][i]] = args[i]
        return secret_key

    def login(self, *args):
        """
        args = (bankcard, password)
        """
        secret_key = self.message('login', args)

        resp = self.s.login(secret_key)
        if ((secret_key['sequence'] != resp['sequence']) 
                and (secret_key['status'] != SUCESS)):
            pass                                                
        else:                                                   
            return resp

    def renewal(self, *args):
        """
        args = ('token', 'bankcard')
        """
        secret_key = self.message('renewal', args)

        resp = self.s.renewal(secret_key)
        if ((secret_key['sequence'] != resp['sequence'])
                and (secret_key['status'] != SUCESS)):
            pass
        else:
            return resp

    def deposit(self, *args):
        """
        args = ('token', 'bankcard', 'amount')
        """
        secret_key = self.message('deposit', args)

        resp = self.s.deposit(secret_key)
        if ((secret_key['sequence'] != resp['sequence'])
                and (secret_key['status'] != SUCESS)):
            pass
        else:
            return resp

    def withdraw(self, *args):
        """
        args = ('token', 'bankcard', 'amount')
        """
        secret_key = self.message('withdraw', args)

        resp = self.s.withdraw(secret_key)
        if ((secret_key['sequence'] != resp['sequence'])
                and (secret_key['status'] != SUCESS)):
            pass
        else:
            return resp

    def transfer(self, *args):
        """
        args = ('token', 'bankcard', 'transferred', 'amount')
        """
        secret_key = self.message('transfer', args)

        resp = self.s.transfer(secret_key)
        if ((secret_key['sequence'] != resp['sequence'])
                and (secret_key['status'] != SUCESS)):
            pass
        else:
            return resp

if __name__ == '__main__':
    rpc = Client_RPC()
    print(rpc.login('123', '456'))
    print(rpc.renewal('123', '23'))
    print(rpc.deposit('123', '23312', 12312))
    print(rpc.withdraw('213', '12321', 123))
    print(rpc.transfer('213', '123', '123', 12))
