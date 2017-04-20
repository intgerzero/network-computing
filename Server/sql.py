#!/usr/bin/env python3
# -*- coding: utf-8

import mysql.connector

class SQL:
    """
    database: account
    tables: account
        account:
            bankcard char(20)
            amount   int(11)
    """

    def __init__(self, **kw):
        # 默认设置
        self.config = {
                'user': 'root',
                'password': 'root',
                'host': 'localhost',
                'database': 'account',
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
        except Exception as e:
            flag = False
        finally:
            return flag

    def close(self):
        try:
            self.cnx.close()
        except:
            pass

    def execute(self, query):
        try:
            self.cursor.execute(query)
            flag = True
        except Exception as e:
            flag = False
        finally:
            return flag

    def commit(self):
        try:
            self.cnx.commit()
            flag = True
        except:
            flag = False
        finally:
            return flag

    def rollback(self):
        try:
            self.cnx.rollback()
            flag = True
        except:
            flag = False
        finally:
            return flag
