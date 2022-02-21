#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os


class Sensor:
    def __init__(self, channel):
        self.channel = channel
        self.name = channel
        self.humidity = 0
        self.temperature = 0

    @classmethod
    def get_humidity(cls, channel, device):
        if device == 'TCU300':
            cls.humidity = str(int(os.popen('cat ' + channel).read()[0:5]) / 1000)
            return cls.humidity
        elif device == 'EMU3000':
            tmp_raw = os.popen('cat ' + channel + '/in_humidityrelative_raw').read()
            tmp_scale = os.popen('cat ' + channel + '/in_humidityrelative_scale').read()
            cls.humidity = (int(tmp_raw) * int(tmp_scale))
            return cls.humidity
        elif device == 'TCU1000':
            cls.humidity = str(int(os.popen('cat ' + channel).read()[0:5]) / 1000)
            return cls.humidity
        elif device == 'TCU3000':
            cls.humidity = str(int(os.popen('cat ' + channel).read()[0:5]) / 1000)
            return cls.humidity
    @classmethod
    def get_temperature(cls, channel, device):
        if device == 'TCU300':
            cls.temperature = str(int(os.popen('cat ' + channel).read()[0:5]) / 1000)
            return cls.temperature
        elif device == 'EMU3000':
            tmp_raw = os.popen('cat ' + channel + '/in_temp_raw').read()
            tmp_offset = os.popen('cat ' + channel + '/in_temp_offset').read()
            tmp_scale = os.popen('cat ' + channel + '/in_temp_scale').read()
            cls.temperature = (int(tmp_raw) + int(tmp_offset)) * int(tmp_scale)
            return cls.temperature
        elif device == 'TCU1000':
            cls.temperature = str(int(os.popen('cat ' + channel).read()[0:5]) / 1000)
            return cls.temperature
        elif device == 'TCU3000':
            cls.temperature = str(int(os.popen('cat ' + channel).read()[0:5]) / 1000)
            return cls.temperature


