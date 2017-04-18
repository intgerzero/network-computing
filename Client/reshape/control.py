#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import signal
import socket
import logging
from threading import Thread

__TIMEOUT__ = 10

logging.basicConfig(filename='control.log',level=logging.DEBUG)

class Control:

    def __init__(self, **kw):
        """
        kw -- dictionary, {'bankcard': bankcard, 'password': password, 'address': address, 'port': port}
        """
        signal.signal(signal.SIGCHLD, signal.SIG_IGN) # 处理僵尸进程

        self.login_info = kw
        self.address = (kw['address'], int(kw['port']))

    def login(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(__TIMEOUT__)
        
        msg = {'type': '00',
                'bankcard': self.login_info['bankcard'],
                'password': self.login_info['password']
                }
        payload = json.dumps(msg).encode('utf-8')
        
        result = dict()
        try:
            s.connect(self.address)
            s.sendall(payload)
            buf = s.recv(1024).decode('utf-8')
            s.close()
            logging.debuf("login: " + buf)

            if buf == '': # means server closed
                result['status'] = 1
                result['msg'] = 'server closed'
            else:   
                msg = json.dumps(buf)
                
                if msg['status'] == 0:
                    self.login_info['token'] = msg['token']
                    self.login_info['deadline'] = int(msg['deadline'])
                    result['status'] = 0
                    t = Thread(target=self.work)
                    t.start()
                else:
                    result['status'] = 1
                result['msg'] = msg['msg']
        except Exception as e:  # 捕获所有的异常 https://python3-cookbook.readthedocs.io/zh_CN/latest/c14/p07_catching_all_exceptions.html
            result['status'] = 1
            result['msg'] = e
        finally:
            return result

    def renewal_token(self):
        msg = {'type': '10', 'bankcard': self.login_info['bankcard'], 'token': self.login_info['token']}
        payload = json.dumps(msg).encode('utf-8')
        while True:
            time.sleep(60)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(__TIMEOUT__)
            if math.floor(time.time()) - self.login_info['deadline'] < 300:
                try:
                    s.connect(self.address)
                    s.sendall(payload)
                    buf = s.recv(1024).decode('utf-8')
                    s.close()
                    if buf == '':
                        logging.info("renewal fail.")
                    else:
                        msg = json.loads(buf)
                        if msg['status'] == 0:
                            self.login_info['deadline'] = int(msg['deadline'])
                            logging.info("renewal success.")
                        else:
                            logging.info("renewal fail.")
                except Exception as e:
                    logging.info("renewal fail. {}".format(e))

    def deposit(self, amount):
        if amount <= 0:
            pass

        try:
            msg = {'type': '20', 'token': self.login_info['token'], 'bankcard': self.login_info['bankcard'], "amount": int(amount)}

        except Exception as e:
            pass

    def _transaction(self, msg):
        logging.info("------ Transaction Start ------")

        payload = json.dumps(msg).encode('utf-8')
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(__TIMEOUT__)
            s.connect(self.address)
            s.sendall(payload)
    
            # first stage -- enquire
            buf = s.recv(1024).decode('utf-8')
            logging.debug("from coordinaotr: {}".format(buf))

            if buf == '': # 连接被关闭
                pass
            else:
                replay = json.loads(buf)
                sequence = reply['sequence']
                operation = reply['msg']

                if operation != msg: # 有问题的回复
                    pass
                else:
                    ack = {'sequence': sequence, 'status': '0'} # 回复
                    payload = json.dumps(ack).encode('utf-8')
                    

        except Exception as e:
            pass
        finally:
            s.close()

