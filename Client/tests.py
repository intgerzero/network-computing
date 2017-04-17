#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from control import Control

class Test:

    def __init__(self):
        kw = {'bankcard': '1234567890', 'password': '01234567890', 'address': '127.0.0.1', 'port': 4000}
        self.c = Control(**kw)

    def login_test(self):
        resp = self.c.login()
        print(resp)

    def deposit_test(self):
        resp = self.c.deposit(200)
        print(resp)

if __name__ == '__main__':
    test = Test()
    test.login_test()
    test.deposit_test()
