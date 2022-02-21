#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import time
import serial

send_content = bytes('01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234'
                     '567890123456789ABCD', 'utf-8')


class Serial:
    def __init__(self, port, bitrate, size, stop, parity):
        self.port = port
        self.bitrate = bitrate
        self.parity = parity
        self.size = size
        self.stop = stop
        self.open_com = None
        self.send_flag = False
        self.receive_flag = True
        self.send_bytes = 0
        self.receive_bytes = 0
        self.name = port
        self.send_status = None
        self.receive_status = None

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

    def open(self):
        try:
            self.open_com = serial.Serial(
                port=self.port,
                baudrate=self.bitrate,
                parity=self.parity,
                stopbits=self.stop,
                bytesize=self.size,
                timeout=None)
        except Exception as e:
            print(e)

    def close(self):
        if self.open_com is not None and self.open_com.isOpen:
            self.open_com.close()

    def receive(self):
        if self.open_com is None:
            self.open()
        while True:
            if self.receive_flag:
                count = self.open_com.inWaiting()
                if count != 0:
                    count = self.open_com.inWaiting()
                    rev = self.open_com.read(count)
                    self.receive_bytes += len(rev)
                    # print(self.name, ':', self.receive_bytes, end='\r')
                # _thread.start_new_thread(self.receive, ())
            time.sleep(0.01)

    def send(self):
        if self.open_com is None:
            self.open()
        while True:
            if self.send_flag:
                count = self.open_com.write(send_content)
                self.send_bytes += count
            # self.flush()
            time.sleep(0.01)