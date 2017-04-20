#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
客户端崩溃时刻：

1. 发送业务请求之前                     -- 正常
2. 发送业务请求之后，第一阶段 recv 之前 -- 正常
3. 第一阶段 recv 之后、ack 之前         -- 正常
4. 第一阶段 ack 之后、第二阶段 recv 前  -- 无解，数据可能不一致，二阶段提交协议弊端
5. 第二阶段 recv 后、ack 之前           -- 未实现，根据日志可恢复(本地事务范围)
6. 第二阶段 ack 之后, recv result 之前  -- 本地事务范围
7. recv result 之后                     -- 显示问题
"""
# ------ TEST POINT ------
TEST_POINT_1 = False # before request
TEST_POINT_2 = False # before first recv
TEST_POINT_3 = False # before first send
TEST_POINT_4 = False # before second recv
TEST_POINT_5 = False # before second send
TEST_POINT_6 = False # before result recv
TEST_POINT_7 = False # after  result recv
# --------- END ----------

import sys
import json
import time
import math
import signal
import socket
import logging
from threading import Thread

__TIMEOUT__ = 10

log_fmt = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
date_fmt = '%m-%d %H:%M:%S'
logging.basicConfig(filename='control.log',level=logging.INFO, format=log_fmt, datefmt=date_fmt)

class Control:

    def __init__(self, **kw):
        """
        kw -- dictionary, {'bankcard': bankcard, 'password': password, 'address': address, 'port': port}
        """
        signal.signal(signal.SIGCHLD, signal.SIG_IGN) # 处理僵尸进程

        self.login_info = kw
        self.address = (kw['address'], int(kw['port']))

    def login(self):
        """
        return value:
           result = {
                "status": bool,
                "msg": message
            }
        """
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
            logging.debug("login recv: {}".format(buf))

            if buf == '': # means server closed
                result['status'] = False
                result['msg'] = 'server closed'
            else:   
                reply = json.loads(buf)
                if reply['status'] == 0:
                    self.login_info['token'] = reply['token']
                    self.login_info['deadline'] = int(reply['deadline'])
                    result['status'] = True
                    #self.t_renewal = Thread(target=self.renewal_token)
                    #self.t_renewal.start()
                else:
                    result['status'] = False
                result['msg'] = reply['msg']
        except Exception as e:  # 捕获所有的异常 https://python3-cookbook.readthedocs.io/zh_CN/latest/c14/p07_catching_all_exceptions.html
            result['status'] = False
            result['msg'] = e
        finally:
            logging.debug("login result: {}".format(str(result)))
            return result

    def renewal_token(self):
        logging.debug("------ renewal thread start ------")
        msg = {'type': '10', 'bankcard': self.login_info['bankcard'], 'token': self.login_info['token']}
        payload = json.dumps(msg).encode('utf-8')
        while True:
            time.sleep(60)
            logging.debug("------ try to renewal ------")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(__TIMEOUT__)
            date = math.floor(time.time())
            if (self.login_info['deadline']-date) < 300 and \
                    (self.login_info['deadline']-date):
                try:
                    s.connect(self.address)
                    s.sendall(payload)
                    buf = s.recv(1024).decode('utf-8')
                    s.close()
                    if buf == '':
                        logging.info("renewal fail.")
                    else:
                        msg = json.loads(buf)
                        if msg['status'] == 0 and msg['token'] == self.login_info['token']:
                            self.login_info['deadline'] = int(msg['deadline'])
                            logging.info("renewal success.")
                        else:
                            logging.info("renewal fail. token has some question.")
                except Exception as e:
                    logging.info("renewal fail. {}".format(e))

    def stop(self):
        """
        when client exit, kill renewal thread
        """
        self.t_renewal.exit()

    def deposit(self, amount):
        """
        return value:
            result = {
                "status": bool,
                "msg": message
            }
        """
        if amount <= 0:
            pass # 忽略无效金额
        msg = { 'type': '20',
                'token': self.login_info['token'],
                'bankcard': self.login_info['bankcard'],
                "amount": int(amount)
            }
        return self._operation(msg)

    def withdraw(self, amount):
        """
        return value:
            result = {
                "status": bool,
                "msg": message
            }
        """
        if amount <= 0:
            pass # 忽略无效金额
        msg = { 'type': '30',
                'token': self.login_info['token'],
                'bankcard': self.login_info['bankcard'],
                "amount": int(amount)
            }
        return self._operation(msg)

    def transfer(self, amount, transferred):
        """
        return value:
            result = {
                "status": bool,
                "msg": message
            }
        """
        if amount <= 0:
            pass # 忽略无效金额
        msg = { "type": '40',
                "token": self.login_info['token'],
                "bankcard": self.login_info['bankcard'],
                "transferred": str(transferred),
                "amount": int(amount)
            }
        return self._operation(msg)


    def _operation(self, msg):
        result = dict()
        try:
            payload = json.dumps(msg).encode('utf-8')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(__TIMEOUT__)
            s.connect(self.address)
            
            # test point 1
            if TEST_POINT_1 == True:
                logging.info("TEST_POINT_1 == True, exit")
                exit(0)

            s.sendall(payload)

            if TEST_POINT_2 == True:
                logging.info("TEST_POINT_2 == True, exit")
                exit(0)

            buf = s.recv(1024).decode('utf-8')
            if buf == '': # 连接被关闭
                result['status'] = False # 事务执行失败
                result['msg'] = 'socket closed'
            else:
                reply = json.loads(buf)
                if reply.get('sequence') is None:
                    result['status'] = False
                    result['msg'] = reply['msg']
                else:
                    self._transaction(s, reply) # ignore return
                
                    # test point 6
                    if TEST_POINT_6 == True:
                        logging.info("TEST_POINT_6 == True, exit")
                        exit(0)

                    buf = s.recv(1024).decode('utf-8')
                    logging.debug("deposite result: {}".format(buf))

                    # test point 7
                    if TEST_POINT_7 == True:
                        logging.info("TEST_POINT_7 == True, exit")
                        exit(0)

                    if buf == '': # 连接被关闭
                        result['msg'] = 'socket close'
                        result['status'] = False
                    else:
                        result = json.loads(buf)
                        if result['status'] == 0:
                            result['status'] = True
                        else:
                            result['status'] = False
        except Exception as e:
            result['status'] = False
            result['msg'] = e
        finally:
            return result

    def _transaction(self, s, reply):
        logging.info("------ Transaction Start ------")

        result = dict()
        try:
            # first stage -- enquire or close socket or can't operation transaction
            logging.debug("first stage from coordinaotr: {}".format(str(reply)))

            sequence = reply['sequence'] # 标记事务序列

            # 执行本地事务操作，但不释放资源
            logging.info("redo, msg: {}".format(str(reply['msg'])))

            ack = {'sequence': sequence, 'status': 0} # 回复
            payload = json.dumps(ack).encode('utf-8')

            if TEST_POINT_3 == True:
                logging.info("TEST_POINT_3 == True, exit")
                exit(0)

            s.sendall(payload)
            logging.info("{} first stage completes.".format(sequence))

            # second stage -- commit or rollback

            if TEST_POINT_4 == True:
                logging.info("TEST_POINT_4 == True, exit")
                exit(0)

            buf = s.recv(1024).decode('utf-8')
            logging.debug("second stage from coordinator: {}".format(buf))

            if buf == "": # 连接被关闭
                result['status'] = False # 事务执行失败
                result['msg'] = 'socket closed'
                # roolback
            else:
                reply = json.loads(buf)
                if reply['sequence'] == sequence and reply['status'] == 0:
                    # 执行成功，释放资源
                    result['status'] = True
                    result['msg'] = 'transaction success'
                else:
                    # 回滚操作，释放资源
                    result['status'] = False
                    result['msg'] = 'transaction fail'
                if TEST_POINT_5 == True:
                    logging.info("TEST_POINT_% == True, exit")
                    exit(0)
                s.sendall(payload)
            logging.info("{} second stage completes.".format(sequence))

        except Exception as e:
            result['status'] = False
            result['msg'] = e
        finally:
            logging.info("------ Transaction End ------")
            logging.debug("transaction result: {}".format(str(result)))
            return result
