#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import errno
import socket
import logging
from transaction import Transaction
from auth import ClientAuth

logging.basicConfig(filename='route.log',level=logging.DEBUG)

class Route:
    '''
    synchronized works, not need sequence
    '''
    def __init__(self, *args):
        self.address = args
        self.client_auth = ClientAuth()

    def start_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(self.address)
        s.listen(5)

        while True:
            client, addr = s.accept()
            client.settimeout(2) # timeout time is 2 seconds
            logging.debug("connected: {}".format(addr))
            try:
                while True:
                   buf = client.recv(8192)
                   if not buf:
                       break
                   msg = json.loads(buf.decode('utf-8'))
                   logging.debug('msg: {}'.format(msg))
                   if msg['type'] == "00":
                       logging.debug("type: {}".format(msg['type']))
                       client.sendall(self._auth(msg))
                   elif msg['type'] == "10":
                       logging.debug("type: {}".format(msg['type']))
                       client.sendall(self._renewal(msg))
                   elif msg['type'] == "20" or msg['type'] == '30' or msg['type'] == '40':
                       logging.debug("type: {}".format(msg['type']))
                       client.sendall(self._transaction(msg, client))
            except socket.timeout:
                logging.debug("client timeout.")
                pass

    def _server_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 4001))
        return sock

    def _auth(self, msg):
        result = self.client_auth.client_auth(msg)
        resp = {'type': '01',
                'token': '',
                'expiration': str(result[2]),
                'msg': ''}
        if result[0] == True:
            resp['status'] = 0
            resp['token'] = result[1]
        else:
            resp['status'] = 1
            resp['msg'] = result[1]
        logging.debug("auth: {}".format(resp))
        return json.dumps(resp).encode('utf-8')

    def _renewal(self, msg):
        result = self.client_auth.token_renewal(msg)
        resp = {'type': '11',
                'token': msg['token']}
        if result[0] == True:
            resp['status'] = 0
            resp['msg'] = result[1]
        else:
            resp['status'] = 1
            resp['msg'] = result[1]
        logging.debug("renewal: {}".format(resp))
        return json.dumps(resp).encode('utf-8')

    def _transaction(self, msg, client):
        result = self.client_auth.token_auth(msg)
        logging.debug("transaction auth: {}".format(result))
        if result[0]:
            serv_sock = self._server_sock()
            tran = Transaction(msg, client, serv_sock)
            flag = tran.two_phase_commit()
            serv_sock.close()
        resp = {'type': str(int(msg['type'])+1),
                'token': msg['token']}
        if result[0] and flag:
            resp['status'] = 0
            resp['msg'] = 'Success.'
        else:
            resp['status'] = 1
            if result[0]:
                resp['msg'] = 'Transaction failed.'
            else:
                resp['msg'] = result[1]
        return json.dumps(resp).encode('utf-8')

if __name__ == "__main__":
    co = Route('0.0.0.0', 4000)
    co.start_server()
