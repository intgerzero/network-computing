#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import socket
import logging

__TIMEOUT__ = 10

logging.basicConfig(filename='route.log',level=logging.DEBUG)

class Control:

    def __init__(self, **kw):
        """
        kw -- dictionary, {'bankcard': bankcard, 'password': password, 'address': address, 'port': port}
        """
        self.login_info = kw
        self.address = (kw['address'], kw['port'])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(__TIMEOUT__)

    def login(self):
        msg = {'type': '00', 'bankcard': self.login_info['bankcard'], 'password': self.login_info['password']}
        payload = json.dumps(msg).encode('utf-8')
        try:
            self.s.connect(self.address)
            self.s.sendall(payload)
            msg = json.loads(self.s.recv(4096).decode('utf-8'))
            logging.debug("login: " + str(msg))
            self.s.close()

            if msg['status'] == '0':
                self.login_info['token'] = msg['token']
                self.login_info['deadline'] = int(msg['deadline'])
            else:
                pass
        except socket.timeout:
            pass

    def renewal_token(self):
        msg = {'type': '10', 'bankcard': self.login_info['bankcard'], 'token': self.login_info['token']}
        payload = json.dumps(msg).encode('utf-8')
        while True:
            time.sleep(60)
            if math.floor(time.time()) - self.login_info['deadline'] < 300:
                self.s.connect(self.address)
                self.s.sendall(payload)
                msg = json.loads(self.s.recv(1024).decode('utf-8'))
                if msg['status'] == '0':
                    self.login_info['deadline'] = int(msg['deadline'])
                else:
                    pass

    def deposit(self, amount):
        if amount <=0:
            return
        msg = {'type': '20', 'token': self.login_info['token'], 'bankcard': self.login_info['bankcard'], "amount": str(amount)}
        payload = json.dumps(msg).encode('utf-8')


    def withdraw(self, amount):
        pass

    def transfer(self, amount, transferred):
        pass
