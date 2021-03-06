#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import errno
import signal
import socket
import logging
from threading import Thread
from transaction import Transaction
from auth import ClientAuth

__BACKLOG__ = 5 # listen paramater
__TIMEOUT__ = 10 # client socket timeout

log_fmt = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
date_fmt = '%m-%d %H:%M:%S'
logging.basicConfig(filename='route.log',level=logging.INFO, format=log_fmt, datefmt=date_fmt)

class Route:

    def __init__(self, **kw):
        """
        kw = {
            'local_server': (address, port),
            'remote_server': (address, port),
            'database': {
                'user': username,
                'password': password,
                'host': host,
                'database': database,
                'raise_on_warnings': True
            }
        }
        """
        signal.signal(signal.SIGCHLD, signal.SIG_IGN) # 处理僵尸进程
        # default setting
        self.config = {
                'local_server': ('0.0.0.0', 4000),
                'remote_server': ('localhost', 4001),
                'database': {} # use default settings
                }

        # read config from kw
        for key in kw.keys():
            if key == 'database' and isinstance(kw[key], dict):
                self.config[key] = kw[key]
                continue
            if self.config[key] != None and len(kw[key]) == 2:
                self.config[key] = kw[key]

        self.client_auth = ClientAuth(**self.config['database'])

    def start_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(self.config['local_server'])
        s.listen(__BACKLOG__)

        while True:
            client, addr = s.accept()
            client.settimeout(__TIMEOUT__)
            logging.debug("connect from: {}".format(addr))
            t = Thread(target=self.work, args=(client, addr))
            t.start()

    def work(self, client, addr):
        try:
            buf = client.recv(1024).decode('utf-8')

            logging.debug("receive: {}".format(buf))
            if buf == '': # means client closed
                pass
            else:
                msg = json.loads(buf)

                if msg['type'] == '00':
                    client.sendall(self._auth(msg)) 
                elif msg['type'] == '10':
                    client.sendall(self._renewal(msg))
                elif msg['type'] == '20' or msg['type'] == '30':
                    client.sendall(self._transaction(msg, client))
                elif msg['type'] == '40':
                    # 先验证是否存在收款人账户
                    self.client_auth.connect()
                    status, error = self.client_auth.search(msg['transferred'])
                    logging.debug("transferred status {}".format(status))
                    self.client_auth.close()
                    if status:
                        reply = self._transaction(msg, client)
                    else:
                        message = { 'type': str(int(msg['type'])+1),
                                    'token': msg['token'],
                                    'status': 1,
                                    'msg': error
                            }
                        reply = json.dumps(message).encode('utf-8')
                    client.sendall(reply)
        except Exception as e:
            logging.debug("Client {}".format(e))
        finally:
            client.close()

    def _auth(self, msg):
        status, error = self.client_auth.connect()
        if status:
            status, token, deadline = self.client_auth.client_auth(msg)

            msg = { 'type': '01',
                    'deadline': deadline
                }
            if status:
                msg['status'] = 0
                msg['token'] = token
                msg['msg'] = 'Authentication success.'
            else:
                msg['status'] = 1
                msg['token'] = ''
                msg['msg'] = token
        else:
            msg = {'type': '01',
                    'status': 1,
                    'deadline': -1,
                    'token': '',
                    'msg': error
                }
            self.client_auth.close()
        logging.info("_auth result: {}".format(msg))
        return json.dumps(msg).encode('utf-8')

    def _renewal(self, msg):
        status, error = self.client_auth.connect()
        if status:
            status, message, deadline = self.client_auth.token_renewal(msg)
            msg = { 'type': '11',
                    'token': msg['token'],
                    'deadline': deadline,
                    'msg': message
                    }
            if status:
                msg['status'] = 0
            else:
                msg['status'] = 1
        else:
            msg = {'type': '11',
                    'token': msg['token'],
                    'deadline': -1,
                    'msg': error,
                    'status': 1
                    }
            self.client_auth.close()
        logging.debug("_renewal result: {}".format(msg))
        return json.dumps(msg).encode('utf-8')

    def _server_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(self.config['remote_server'])
            sock.settimeout(__TIMEOUT__)
            msg = ''
        except Exception as e:
            sock = None
            msg = e
        finally:
            return sock, msg

    def _transaction(self, msg, client):
        """
        事务操作前先验证身份
        验证成功后再进行操作
        return value:
            message = {
                "type": '11' or '21' or '31' or '41',
                "token": token,
                "status": '0' or '1',
                "msg": message
            }
        """
        message = { 'type': str(int(msg['type'])+1),
                'token': msg['token']
            };

        status, error = self.client_auth.connect()
        if status:
            status, error = self.client_auth.token_auth(msg)
            logging.debug("authentication status: {} {}".format(status, error))
            if status: # 认证成功
                serv_sock, error = self._server_sock()
                if serv_sock != None:
                    tran = Transaction(msg, client, serv_sock)
                    flag = tran.two_phase_commit()
                    serv_sock.close()

                    if flag:
                        message['status'] = 0
                        message['msg'] = 'Success'
                    else:
                        message['status'] = 1
                        message['msg'] = 'transaction failed.'
                else:
                    message['status'] = 1
                    message['msg'] = "remote server wasn't reply"
            else: # 认证失败
                message['status'] = 1
                message['msg'] = 'authentication fail'
        else:
            message['status'] = 1
            message['msg'] = error

        self.client_auth.close()
        logging.debug('_authencation result: {}'.format(str(message)))
        return json.dumps(message).encode('utf-8')

if __name__ == '__main__':
    co = Route()
    co.start_server()
