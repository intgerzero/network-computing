#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import math
import json
import socket
import logging
import transaction

logging.basicConfig(filename='transaction.log', level=logging.DEBUG)

class Transaction:

    def __init__(self, msg, sponsor, participator):
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


    def __send(self, key, msg):
        payload = json.dumps(msg).encode('utf-8')
        try:
            self.cohorts[key].sendall(payload)
            logging.info("{} send {} to {}.".format(self.sequence, str(msg), key))
            return True
        except socket.timeout:
            logging.info("{} send {} to {}, timeout.".format(self.sequence, str(msg), key))
            return False

    def __recv(self, key):
        try:
            buf = self.cohorts[key].recv(1024)
            msg = json.loads(buf.decode('utf-8'))
            logging.info("{} {} responses: {}.".format(self.sequence, key, str(msg)))
            if msg['status'] == '0'  and msg['sequence'] == self.sequence:
                return True
            else:
                logging.info("{} {} rejected".format(self.sequence, key))
                return False
        except socket.timeout:
            logging.info("{} {} timeout".format(self.sequence, key))
            return False

    def enquire(self, key):
        msg = {'sequence': self.sequence, 'msg': self.msg}
        if self.__send(key, msg):
            if self.__recv(key):
                return True
        return False

    def commit(self, key):
        msg = {'sequence': self.sequence, 'status': '0'}
        if self.__send(key, msg):
            if self.__recv(key):
                return True
        return False

    def rollback(self, key):
        msg = {'sequence': self.sequence, 'status': '1'}
        if self.__send(key, msg):
            if self.__recv(key):
                return True
        return False

    def two_phase_commit(self):
        logging.info("{}: first stage.".format(self.sequence))

        flag = True
        for key in self.cohorts.keys(): # request stage
            flag = self.enquire(key)
        
        logging.info("{}: second stage.".format(self.sequence))
        for key in self.cohorts.keys(): # commit stage, ignore result
            if flag == False:
                self.rollback(key)
            else:
                self.commit(key)

        logging.info('{} ------Transaction Ended------'.format(self.sequence))
        
        return flag
