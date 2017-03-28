#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 发送/接收
# control <--> net
# 生产者、消费者队列

import socket
import asyncio

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('www.sina.com.cn', 80))
s.send(b'GET / HTTP/1.1\r\nHost: www.sina.com.cn\r\nConnection: close\r\n\r\n')
buffer = []
while True:
    # 每次最多接收1k字节:
    d = s.recv(1024)
    if d:
        buffer.append(d)
    else:
        break
data = b''.join(buffer)
s.close()
header, html = data.split(b'\r\n\r\n', 1)
print(header.decode('utf-8'))

class Sender():

    def __init__(self, queue):
        self.queue = queue
        self.sock = socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self):
        self.sock.connect()

    pass

class Receiver():
    pass

class Comsumer():
    def __init__(self, queue):
        self.queue = queue

    async def run(self):
        await asyncio.wait([self.url_queue.put(self.url+repr(i+1)) for i in range(self.number)])
        fetch_tasks = [asyncio.ensure_future(self.fetch_worker()) for _ in range(self.max_tasks)]
        verify_tasks = [asyncio.ensure_future(self.verify_worker()) for _ in range(10*self.max_tasks)]
        tasks = fetch_tasks + verify_tasks
        await self.url_queue.join()
        self.session.close() # close session, otherwise shows error
        print("url_queue done")
        self.raw_proxy_queue.join()
        print("raw_proxy_queue done")
        await self.proxy_queue.join()
        for task in tasks:
            task.cancel()

    async def work(self):
        while True:
            item = await self.queue.get()

