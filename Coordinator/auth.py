#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import math
import time
import hashlib
import mysql.connector

class ClientAuth:

    def __init__(self, **kw):
        # 默认设置
        self.config = {
                'user': 'root',
                'password': 'root',
                'host': 'localhost',
                'database': 'login',
                'raise_on_warnings': True
                };

        # read config from kw
        for key in kw.keys():
            if self.config[key] != None:
                self.config[key] = kw[key]

    def connect(self):
        try:
            self.cnx = mysql.connector.connect(**self.config)
            self.cursor = self.cnx.cursor()
            flag = True
            msg = ''
        except Exception as e:
            flag = False
            msg = e
        finally:
            return flag, msg

    def close(self):
        self.cnx.close();

    def _create_token(self, msg):
        """
        deadline is 86400 seconds, one day
        """
        token = hashlib.sha256(os.urandom(16)).hexdigest()
        deadline = math.floor(time.time()+86400)
        query = "INSERT INTO token(token, deadline, bankcard) VALUES('{}', {}, '{}');".format(token, deadline, msg['bankcard'])
        self.cursor.execute(query)
        self.cnx.commit()
        return token, deadline

    def client_auth(self, msg):
        query = "SELECT * FROM login WHERE password='{}' AND bankcard='{}';".format(msg['password'], msg['bankcard'])
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            if result != []:
                token, deadline = self._create_token(msg)
                flag = True
            else:
                flag = False
                token = 'Authentication fail.'
                deadline = -1
        except Exception as e:
            flag = False
            token = e
            deadline = -1
        finally:
            return flag, token, deadline

    def token_auth(self, msg):
        query = "SELECT * FROM token WHERE token='{}' AND deadline>={} AND bankcard='{}'".format(msg['token'], math.floor(time.time()), msg['bankcard'])
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            if result != []:
                flag = True
                msg = 'Verification success.'
            else:
                flag = False
                msg = 'Verification failed.'
        except Exception as e:
            flag = False
            msg = e
        finally:
            return flag, msg

    def token_renewal(self, msg):
        status, message = self.token_auth(msg)
        deadline = math.floor(time.time()+86400)
        if status:
            query = "UPDATE token SET deadline={} WHERE token='{}';".format(deadline, msg['token']) 
            try:
                self.cursor.execute(query)
                self.cnx.commit()
                flag = True
                message = 'Renewal success.'
            except Exception as e:
                 flag = False
                 message = e
                 deadline = -1
        else:
            flag = False
            deadline = -1
        return flag, message, deadline
    
    def search(self, bankcard):
        query = "SELECT * FROM login WHERE bankcard='{}'".format(bankcard)
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            if result != []:
                flag = True
                error = ''
            else:
                flag = False
                error = 'not exist this account'
        except Exception as e:
            flag = False
            error = e
        finally:
            return flag, error

# Example && test
if __name__ == '__main__':
    auth = ClientAuth()
    print(auth.connect())
    msg = {'bankcard': '1234567890', 'password': '01234567890'}
    status, token, deadline = auth.client_auth(msg)
    print(status, token, deadline)
    msg = {'bankcard': '1234567890', 'token': token, 'deadline': deadline}
    print(auth.token_auth(msg))
    msg = {'bankcard': '1234567890', 'token': token, 'deadline': deadline}
    print(auth.token_renewal(msg))
    auth.close()
