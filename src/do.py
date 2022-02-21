#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os


class Do:
    def __init__(self, channel):
        self.channel = channel
        self.name = channel
        self.status = 0

    @classmethod
    def set_do_status(cls, channel, action):
        os.system('echo ' + str(action) + ' > ' + channel)

    @classmethod
    def get_do_status(cls, channel):
        cls.status = os.popen('cat ' + channel).read()
        return cls.status
