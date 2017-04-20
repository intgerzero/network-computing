#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务器崩溃时刻：

1. 第一阶段 recv 之前                -- 正常
2. 第一阶段 recv 后、 ack 前         -- 正常
3. 第一阶段 ack 后、第二阶段 recv 前 -- 无解，数据可能不一致，二阶段提交协议弊端
4. 第二阶段 recv 后、ack 前          -- 未实现，可以根据日志内容进行回滚，恢复正常状态
5. 第二阶段 ack 后                   -- 正常
"""

# ------ TEST POINT ------
TEST_POINT_1 = False # before first stage recv
TEST_POINT_2 = False # before first stage send
TEST_POINT_3 = False # before second recv
TEST_POINT_4 = False # before second send
TEST_POINT_5 = False # 无意义的存在
# --------- END ----------

import sys
import json
import time
import signal
import socket
import logging
from threading import Thread
from sql import SQL

__BACKLOG__ = 5 # listen paramater
__TIMEOUT__ = 10 # client socket timeout

log_fmt = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
date_fmt = '%m-%d %H:%M:%S'
logging.basicConfig(filename='server.log',level=logging.DEBUG, format=log_fmt, datefmt=date_fmt)

class Server:

    def __init__(self, *args):
        """
        address = (address, port)
        """
        signal.signal(signal.SIGCHLD, signal.SIG_IGN) # 处理僵尸进程
        self.address = ("0.0.0.0", 4001)
        if args != None and len(args) == 2:
            self.address = args

    def start_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(self.address)
        s.listen(__BACKLOG__)
        while True:
            client, addr = s.accept()
            client.settimeout(__TIMEOUT__)
            logging.debug("connect from: {}".format(addr))
            t = Thread(target=self.work, args=(client, addr))
            t.start()

    def work(self, client, addr):
        """
        transaction
        """
        iresult = { # 标记事务完成情况
                    1: False, # first stage -- after first recv, before local transaction
                    2: False, # first stage -- after local transaction, before first ack
                    3: False, # first stage and second stage -- after first ack, before second recv
                    4: False, # second stage -- after recv, before commit or rollback
                    5: False, # second stage -- after commit or rollback, before second ack
                    6: False  # second stage -- after second ack
            }
        logging.info("------ Transaction Start ------")
        self.cnx = SQL()
        try:
            # first stage -- enquire

            # test point 1
            if TEST_POINT_1 == True:
                logging.info("TEST_POINT_1 == True, exit")
                sys.exit(0)

            buf = client.recv(1024).decode("utf-8")
            iresult[1] = True
            logging.debug("first stage from coordinaotr: {}".format(buf))

            if buf == '': # meas client closed
                pass
            else:
                msg = json.loads(buf)
                
                sequence = msg['sequence']
                self.task = msg['msg']
                result = self.operation(self.task) # 本地事务操作, 不释放资源

                logging.debug("local transaction result: {}".format(result))
                ack = { 'sequence': sequence,
                        'status': result
                    }
                payload = json.dumps(ack).encode('utf-8')
                
                iresult[2] = True

                # test point 2
                if TEST_POINT_2 == True:
                    logging.info("TEST_POINT_2 == True, exit")
                    sys.exit(0)
                client.sendall(payload)
                iresult[3] = True
                
                logging.info("{} first stage completes.".format(sequence))
                # first stage complete

                # second stage -- commit or rollback

                # test point 3
                if TEST_POINT_3 == True:
                    logging.info("TEST_POINT_3 == True, exit")
                    sys.exit(0)

                buf = client.recv(1024).decode('utf-8')
                iresult[4] = True
                logging.debug("second stage from coordinator: {}".format(buf))

                if buf == '':
                    self.rollback()
                    pass # means client closed
                else:
                    reply = json.loads(buf)
                    if reply['sequence'] == sequence and reply['status'] == 0:
                        logging.debug("commit")
                        self.commit();
                    else:
                        logging.debug("rollback")
                        self.rollback()
                    iresult[5] = True
                    # test point 4
                    if TEST_POINT_4 == True:
                        logging.info("TEST_POINT_4 == True, exit")
                        sys.exit(0)

                    client.sendall(payload)
                    iresult[6] = True

                logging.info("{} second stage completes.".format(sequence))
                
        except Exception as e:
            # 崩溃，检查完成情况
            for i in range(1, 5):
                if iresult[i] == False:
                    if i == 1: # first recv over -- maybe ... nothing to do
                        pass
                    elif i == 2: # local transaction over -- ... nothing to do
                        pass
                    elif i == 3: # first ack over -- rollback
                        self.rollback()    
                    elif i == 4: # second recv over -- .. rollback
                        pass # 二阶段提交无法解决
                    elif i == 5: # commit or rollback over -- ... code must be some question, or database over ... database will automaticly resume
                        pass # 根据记录的协调者信息重新执行操作
                    elif i == 6: # second send over ... 
                        pass # 重新发送

            logging.debug("error: {}".format(e))
        finally:
            self.cnx.close()
            logging.info("------ Transaction End ------")
            client.close()

    def operation(self, task):
        """
        local transaction operation
        return 1 or 0
            means fail or success
        """
        logging.debug("task: {}".format(task))
        result = self.cnx.connect()
        logging.debug("sql connect result: {}".format(result))
        if result: # 成功
            if task['type'] == '20':
                if self.deposit(task):
                    return 0
            elif task['type'] == '30':
                if self.withdraw(task):
                    return 0
            elif task['type'] == '40':
                if self.transfer(task):
                    return 0
        return 1 # 失败

    def commit(self):
        return self.cnx.commit()

    def rollback(self):
        return self.cnx.rollback()

    def deposit(self, msg):
        query = "UPDATE account SET amount=amount+{} where bankcard='{}'".format(int(msg['amount']), msg['bankcard'])
        return self.cnx.execute(query)

    def withdraw(self, msg):
        """
        允许账户余额为负数
        """
        query = "UPDATE account SET amount=amount-{} where bankcard='{}'".format(int(msg['amount']), msg['bankcard'])
        return self.cnx.execute(query)

    def transfer(self, msg):
        query = "UPDATE account SET amount=amount-{} where bankcard='{}'".format(int(msg['amount']), msg['bankcard'])
        if self.cnx.execute(query):
            query = "UPDATE account SET amount=amount+{} where bankcard='{}'".format(int(msg['amount']), msg['transferred'])
            if self.cnx.execute(query):
                return True
        return False

if __name__ == '__main__':
    s = Server()
    s.start_server()
