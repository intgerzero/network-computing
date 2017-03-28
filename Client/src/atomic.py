#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def sequence():
    i = 0
    while True:
        value = yield i
        i += 1
