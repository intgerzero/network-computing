#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import math
import json
import socket
import logging

log_fmt = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
date_fmt = '%m-%d %H:%M:%S'
logging.basicConfig(filename='route.log',level=logging.DEBUG, format=log_fmt, datefmt=date_fmt)

__TIMEOUT__ = 5

class Transaction:

    def __init__(self, msg, clnt, serv):
        """
        msg -- message, dictionary, from client
        clnt -- client's sock
        serv -- remote server's sock
        """
        self.msg = msg
        self.cohorts = {'client': clnt,
                        'server': serv
                        }
        for sock in self.cohorts.values():
            sock.settimeout(__TIMEOUT__) # 设置超时时间
        self.sequence = math.floor(time.time()) # 事务序列号

    def __send(self, key, msg):
        payload = json.dumps(msg).encode('utf-8')
        try:
            if self.cohorts[key] is None: # 不存在
                flag = False
                erro = "{} closed".format(key)
            else:
                self.cohorts[key].sendall(payload)
                logging.debug("{} send {} to {}".format(self.sequence, str(msg), key))
                flag = True
                error = ''
        except Exception as e:
            error = e
            flag = False
        finally:
            return flag, error
    
    def __recv(self, key):
        try:
            if self.cohorts[key] is None:
                flag = False
                error = "{} closed".format(key)
            else:
                buf = self.cohorts[key].recv(1024).decode('utf-8')
                if buf == '': # 连接关闭
                    logging.debug("{} closed socket".format(key))
                    flag = False
                    error = "{}'s socket was closed".format(key)
                else:
                    logging.debug("{} {} responses: {}".format(self.sequence, key, buf))
                    msg = json.loads(buf)

                    if msg['status'] == 0 and msg['sequence'] == self.sequence:
                        flag = True
                        error = ''
                    else:
                        flag = False
                        error = "{} reject".format(key)
        except Exception as e:
            flag = False
            error = e
        finally:
            return flag, error

    def _send_msg(self, key, msg):
        status, error = self.__send(key, msg)
        if status:
            status, error = self.__recv(key)
        return status, error

    def enquire(self, key): # 第一阶段 -- 询问
        msg = {'sequence': self.sequence, 'msg': self.msg}
        return self._send_msg(key, msg)

    def commit(self, key): # 第二阶段 -- 提交，必会成功
        msg = {'sequence': self.sequence, 'status': 0}
        return self._send_msg(key, msg)

    def roolback(self, key): # 第二阶段 -- 回滚，必会成功
        msg = {'sequence': self.sequence, 'status': 1}
        return self._send_msg(key, msg)

    def two_phase_commit(self):
        """
        return value:
            result = {
                "status": bool,
                "msg": message
            }
        """
        logging.info("{} ------ Transaction Started ------".format(self.sequence))
        logging.info("{} ------ First Stage ------".format(self.sequence))

        collect = list()
        flag = True # 第一阶段参与者标志
        # 1. 协调者节点向所有参与者节点询问是否可以执行提交操作
        # 2. 参与者执行询问发起为止的所有事务操作，并将 Undo / Redo 信息写入日志
        # 3. 各参与节点相应协调者节点发起的询问。如果实际执行成功，发送一个同意消息，否则会认为执行失败
        for key in self.cohorts.keys(): # request stage
            status, error = self.enquire(key)
            if status:
                collect.append(key)
            else:
                flag = False
                logging.debug("{} {}".format(key, error))

        logging.info("{} ------ Second Stage ------".format(self.sequence))

        # 1. 协调者节点向所有参与者节点发出 正式提交/回滚 请求
        # 2. 参与者正式 完成操作/回滚，释放占用的资源
        # 3. 参与者节点向协调者节点发送 操作/回滚 完成消息
        # 4. 协调者节点收到所有参与者节点反馈的 消息 后，取消事务
        if flag: # 参与者们可以执行事务操作
            for key in collect:
                self.commit(key) # 一定可执行成功，不检查状态
        else: # 回滚
            for key in collect:
                self.roolback(key)

        logging.info("{} ------ Transaction End ------".format(self.sequence))

        return flag # 事务是否成功执行
