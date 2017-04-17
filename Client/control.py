#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import socket
import logging

__TIMEOUT__ = 10

logging.basicConfig(filename='control.log',level=logging.DEBUG)

class Control:

    def __init__(self, **kw):
        """
        kw -- dictionary, {'bankcard': bankcard, 'password': password, 'address': address, 'port': port}
        """
        self.login_info = kw
        self.address = (kw['address'], int(kw['port']))

    def login(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(__TIMEOUT__)
        msg = {'type': '00', 'bankcard': self.login_info['bankcard'], 'password': self.login_info['password']}
        payload = json.dumps(msg).encode('utf-8')
        result = {'status': '1', 'msg': 'unknow error'}
        try:
            s.connect(self.address)
            s.sendall(payload)
            resp = json.loads(s.recv(4096).decode('utf-8'))
            logging.debug("login: " + str(resp))
            s.close()

            if resp['status'] == '0':
                self.login_info['token'] = resp['token']
                self.login_info['deadline'] = int(resp['deadline'])
                result = {'status': '0', 'msg': 'login sucessfully'}
            else:
                result = {'status': '1', 'msg': resp['msg']}        
        except Exception as e: # 捕获所有的异常 https://python3-cookbook.readthedocs.io/zh_CN/latest/c14/p07_catching_all_exceptions.html
            result = {'status': '1', 'msg': e};
        finally:
            return result

    def renewal_token(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(__TIMEOUT__)
        msg = {'type': '10', 'bankcard': self.login_info['bankcard'], 'token': self.login_info['token']}
        payload = json.dumps(msg).encode('utf-8')
        while True:
            time.sleep(60)
            if math.floor(time.time()) - self.login_info['deadline'] < 300:
                s.connect(self.address)
                s.sendall(payload)
                msg = json.loads(s.recv(1024).decode('utf-8'))
                s.close()
                if msg['status'] == '0':
                    self.login_info['deadline'] = int(msg['deadline'])
                else:
                    pass # 错误处理

    def deposit(self, amount):
        if amount <=0:
            return
        try:
            msg = {'type': '20', 'token': self.login_info['token'], 'bankcard': self.login_info['bankcard'], "amount": str(amount)}
            result, error = self._transaction(msg)
            return result, error
        except Exception as e:
            return False, e

    def withdraw(self, amount):
        msg = {'type': '30', 'token': self.login_info['token'], 'bankcard': self.login_info['bankcard'], "amount": str(amount)}
        result = self._transaction(msg)

    def transfer(self, amount, transferred):
        pass

    def _transaction(self, msg):
        iResult = False
        error = ""

        logging.info('------Transaction Started------')
        payload = json.dumps(msg).encode('utf-8')
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(__TIMEOUT__)
            s.connect(self.address)
            s.sendall(payload)
            trans_1_recv = s.recv(1024).decode('utf-8')
            logging.info("request from coordinator: {}".format(trans_1_recv))
            msg = json.loads(trans_1_recv)
            
            if msg['status'] == '0': # 可以进行事务操作
                sequence = msg['sequence']
                operation = msg['msg']
                
                # 执行本地 transaction 操作，写日志
                logging.info("redo, msg: {}".format(operation))

                trans_ack = {'sequence': sequence, 'status': '0'}
            
                payload = json.dumps(trans_ack).encode('utf-8')
                s.sendall(payload)
                trans_2_recv = s.recv(1024).decode("utf-8")

                # 释放 transaction 占有的资源
                logging.info("commit from coordinator: {}".format(trans_2_recv))
            
                msg = json.loads(trans_2_recv)

                if msg['sequence'] == sequence and msg['status'] == '0':
                    iResult = True
                else:
                    logging.info("undo, msg: {}".format(operation))
                    error = msg['msg']
                    iResult = False
                s.sendall(payload)
            else: # 无法进行事务操作
                error = msg['msg']

        except Exception as e:
            iResult = False
            error = e
            logging.info("Exception: " + e)
        finally:
            s.close()
            logging.info('------Transaction Ended------')
        print(error)
        return iResult, error
