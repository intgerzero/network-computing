#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import math
import time
import hashlib
import mysql.connector

class ClientAuth:
    def __init__(self, *args):
        config = {
                'user': 'root',
                'password': 'vvl.me',
                'host': 'q.vvl.me',
                'database': 'login',
                'raise_on_warnings': True
        }

        # config = args

        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

    def create_token(self, info):
        '''
        86400 seconds is one day.
        '''
        token = hashlib.sha256(os.urandom(16)).hexdigest()
        query = "INSERT INTO token(token, deadline, bankcard) VALUES('{}', {}, '{}');".format(token, math.floor(time.time()+86400), info['bankcard'])
        self.cursor.execute(query)
        self.cnx.commit()
        return token

    def client_auth(self, info):
        query = "SELECT * FROM login WHERE password='{}' AND bankcard='{}';".format(info['password'], info['bankcard'])
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        if result != []:
            token = self.create_token(info)
            return True, token
        else:
            return False, 'Authentication failed.'

    def token_auth(self, info):
        query = "SELECT * FROM token WHERE token='{}' AND deadline>='{}' AND bankcard='{}'".format(info['token'], math.floor(time.time()), info['bankcard'])
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        if result != []:
            return True, 'Verification successed.'
        else:
            return False, 'Verification failed.'

    def token_renewal(self, info):
        status, msg =  self.token_auth(info)
        if status:
            query = "UPDATE token SET deadline='{}' WHERE token='{}';".format(math.floor(time.time()+86400), info['token'])
            self.cursor.execute(query)
            self.cnx.commit()
            return True, 'Renewal successed.'
        else:
            return False, msg

if __name__ == '__main__':
    auth = ClientAuth();
    info_1 = {'bankcard': '1234567890', 'password': '01234567890'}
    status, token = auth.client_auth(info_1)
    print(status, token)
    info_2 = {'bankcard': '1234567890', 'token': token, 'deadline': 1590796159}
    print(auth.token_auth(info_2))
    info_3 = {'bankcard': '1234567890', 'token': token, 'deadline': 1590796159}
    print(auth.token_renewal(info_3))
