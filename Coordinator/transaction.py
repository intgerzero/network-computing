#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import socket
import logging

class Transaction:

    def __init__(self, sequence):
        self.sequence = sequence
        self.file = open("coordinator.log", 'a+')
        pass

    def enquire(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def accept_connection(self):
        while True:
            client, address = self.server.accept()

            self.participantes[address] = {
                        'socket': client,
                        'commit': True
                    }

    def receive(self, client):
        msg = ''
        while True:
            buf = client.recv(8192).decode('utf-8')
            if not buf:
                break
            msg += buf
        status = json.loads(msg)
        if status['commit']:
            pass
