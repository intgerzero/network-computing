#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import math
import json
import socket
import logging

logging.basicConfig(filename='transaction.log', level=logging.DEBUG)

class Transaction:

    __timeout__ = 5
    __address__ = ('localhost', 4000)
    def __init__(self, b_msg, sponsor, participator):
        """
        msg -- message, bytes, client --> route
        sponsor -- sponsor's sock
        participator -- participator's sock
        """
        self.msg = msg
        self.cohorts = {'sponsor': sponsor,
                'participator': participator}
        for sock in self.cohorts.values():
            sock.settimeout(2)
        self.sequence = math.floor(time.time())

        logging.info('{} ------Transaction Started------'.format(self.sequence))


    def __send(self, key, payload):
        try:
            self.cohorts[key].sendall(payload)
            return True
        except socket.timeout:
            return False

    def __recv(self, key):
        try:
            buf = self.cohorts[key].recv(1024)
            msg = json.load(buf.decode('utf-8'))
            if msg['status'] == 0:
                return True
            else:
                logging.info("{} {} rejected".format(self.sequence, key))
                return False
        except socket.timeout:
            logging.info("{} {} timeout".format(self.sequence, key))
            return False

    def enquire(self, key):
        msg = {'sequence': self.sequence, 'msg': self.msg}
        payload = json.dumps(msg).encode('utf-8')
        if sock.__send(key, payload):
            if self.__recv(key):
                return True
        return False

    def commit(self, key):
        msg = {'sequence': self.sequence, 'status': '0'}
        payload = json.dumps(msg).encode('utf-8')
        if self.__send(key, payload):
            if self.__recv(key):
                return True
        return False

    def rollback(self, key):
        msg = {'sequence': self.sequence, 'status': '1'}
        payload = json.dumps(msg).encode('utf-8')
        if self.__send(key, payload):
            if self.__recv(key):
                return True
        return False

    def two_phase_commit(self):
        logging.info("{} first stage.".format(self.sequence))

        flag = 0
        for key in self.cohorts.keys(): # request stage
            if not self.enquire(key):
                flag = 1
            logging.info("{} {} responses.".format(self.sequence, key))
        
        logging.info("{} second stage.".format(self.sequence))
        for key in self.cohorts.keys(): # commit stage
            if flag:
                self.rollback(key)
            logging.info("{} {} commits.".format(self.sequence, key))

        logging.info('{} ------Transaction Ended------'.format(self.sequence))
