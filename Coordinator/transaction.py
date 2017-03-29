#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import socket
import logging

class Transaction:

    __timeout__ = 5
    __address__ = ('localhost', 4000)
    def __init__(self, info):
        logging.basicConfig(filename='myapp.log', level=logging.INFO)
        logging.info('Transaction Started')

        self.info = info
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.settimeout(__timeout__)

    def connect(self):
        try:
            self.client.connect(__address__)
            return True
        except:
            return False

    def __send(self, payload):
        try:
            self.client.send(payload)
            return True
        except:
            return False

    def __recv(self):
        try:
            msg = self.client.recv(payload)
            return True, msg
        except:
            return False, ''

    def enquire(self):
        msg = {'sequence': self.info['sequence'], 'status': '0'}
        payload = json.dumps(msg)
        if self.send(payload):
            status, msg = self.recv(8196)
            if status:
                return json.loads(msg)
        msg['status'] = 1
        return msg

    def commit(self):
        msg = {'sequence': self.info['sequence'], 'msg': self.info}
        payload = json.dumps(msg)
        if self.send(payload):
            status, msg = self.recv(8196)
            if status:
                return json.loads(msg)
        msg['status'] = 1
        return msg

    def rollback(self):
        msg = {'sequence': self.info['sequence'], 'status': '1'}
        payload = json.dumps(msg)
        self.send(payload)
