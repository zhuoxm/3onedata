#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import time

import can


class Can:
    def __init__(self, channel, bitrate):
        self.interface = 'socketcan'
        self.channel = channel
        self.bitrate = bitrate
        self.bus = None
        self.send_flag = False
        self.receive_flag = True
        self.send_bytes = 0
        self.receive_bytes = 0
        self.name = channel

    def set_send_flag(self, send_flag):
        self.send_flag = send_flag

    def set_receive_flag(self, receive_flag):
        self.receive_flag = receive_flag

    def clear_receive_bytes(self):
        self.receive_bytes = 0

    def get_receive_bytes(self):
        return self.receive_bytes

    def clear_send_bytes(self):
        self.send_bytes = 0

    def get_send_bytes(self):
        return self.send_bytes

    def instance(self):
        can_setup_command = 'ip link set ' + self.channel + ' down && ip link set ' + self.channel + \
                            ' type can bitrate ' + str(self.bitrate) + ' && ip link set ' + self.channel + ' up'
        os.system(can_setup_command)
        self.bus = can.Bus(bustype=self.interface, channel=self.channel, bitrate=self.bitrate)

    # def can_setup(self):
    #     can_setup_command = 'ip link set' + self.channel + 'down && ip link set' + self.channel + 'type can bitrate'
    #     + self.bitrate + ' && ip link set' + self.channel + 'up'
    #     os.system(can_setup_command)

    def send(self):
        if self.bus is None:
            self.instance()
        msg = can.Message(arbitration_id=0xc0ffee, data=[0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77],
                          is_extended_id=False)
        while True:
            if self.send_flag:
                try:
                    self.bus.send(msg, timeout=None)
                    self.send_bytes += len(msg)/8
                    # print("Message sent on {}".format(self.bus.channel_info), 'msg:', msg)
                except can.CanError:
                    print("Message NOT sent")
            time.sleep(0.01)

    def receive(self):
        if self.bus is None:
            self.instance()
        while True:
            if self.receive_flag:
                rev = self.bus.recv()
                if rev is not None:
                    self.receive_bytes += len(rev)/8
            # time.sleep(0.1)
