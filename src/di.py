#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os


class Di:
    def __init__(self, channel):
        self.channel = channel
        self.name = channel
        self.status = 0

    @classmethod
    def get_di_status(cls, channel):
        cls.status = os.popen('cat ' + channel).read()
        return cls.status

