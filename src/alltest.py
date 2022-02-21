#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import time

import serial

import canbus
import serialbus
import di
import do
import sensor
import curses
from curses import wrapper
import _thread

stdscr = curses.initscr()
curses.noecho()
curses.nocbreak()
stdscr.keypad(1)
# stdscr.box()

width = os.get_terminal_size().columns
height = os.get_terminal_size().lines
c_y = height//2 + 5
c_x = width//2 - 10
linnum = 0

ZH_ = bytes('01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234'
            '567890123456789ABCD', 'utf-8')

INFO_ = 'please input: \nstart_send(a-all cN-N) \n2-stop_send \n3-clear_receive_com \n4-clear_send_com ' \
        '\n5-start_send_can \n6-stop_send_can \n7-clear_receive_can \n8-clear_send_can\ndo_control(do1/0-open/close all,dN1/0-open/close channel_N)'


DICT_ = {'EMU3000': {'serial_port': ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3', '/dev/ttyUSB4',
                                     '/dev/ttyUSB5','/dev/ttyUSB6', '/dev/ttyUSB7'],
                     'can_channel': ['can1', 'can2'],
                     'di': ['/sys/bus/iio/devices/iio:device2/in_voltage0_raw',
                            '/sys/bus/iio/devices/iio:device2/in_voltage1_raw',
                            '/sys/bus/iio/devices/iio:device2/in_voltage2_raw',
                            '/sys/bus/iio/devices/iio:device2/in_voltage3_raw',
                            '/sys/bus/iio/devices/iio:device2/in_voltage4_raw',
                            '/sys/bus/iio/devices/iio:device2/in_voltage5_raw',
                            '/sys/bus/iio/devices/iio:device2/in_voltage6_raw',
                            '/sys/bus/iio/devices/iio:device2/in_voltage7_raw'],
                     'do': ['/sys/bus/iio/devices/iio:device3/out_voltage0_raw',
                            '/sys/bus/iio/devices/iio:device3/out_voltage1_raw',
                            '/sys/bus/iio/devices/iio:device3/out_voltage2_raw',
                            '/sys/bus/iio/devices/iio:device3/out_voltage3_raw',
                            '/sys/bus/iio/devices/iio:device3/out_voltage4_raw',
                            '/sys/bus/iio/devices/iio:device3/out_voltage5_raw',
                            '/sys/bus/iio/devices/iio:device3/out_voltage6_raw',
                            '/sys/bus/iio/devices/iio:device3/out_voltage7_raw'],
                     'sensor': ['/sys/bus/iio/devices/iio:device0','/sys/bus/iio/devices/iio:device0']},
         'TCU300': {'serial_port': ['/dev/rs485s0p1', '/dev/rs485s0p2', '/dev/rs485s0p3', '/dev/rs485s0p4',
                                    '/dev/rs232s0p5'],
                    'can_channel': ['cans0p1'],
                    'sensor': ['/sys/class/hwmon/hwmon2/temp1_input', '/sys/class/hwmon/hwmon2/humidity1_input']},
         'TCU1000': {'serial_port': ['/dev/rs485s0p1', '/dev/rs485s0p2', '/dev/rs485s0p3', '/dev/rs485s0p4',
                                     '/dev/rs232s0p5'],
                     'can_channel': ['cans0p1'],
                     'sensor': ['/sys/class/hwmon/hwmon2/temp1_input', '/sys/class/hwmon/hwmon2/humidity1_input']},
         'TCU3000': {'serial_port': ['/dev/rs485s0p1', '/dev/rs232s0p2'],
                     'sensor': ['/sys/class/hwmon/hwmon2/temp1_input', '/sys/class/hwmon/hwmon2/humidity1_input'],
                     'di': ['/sys/bus/iio/devices/iio:device1/in_voltage0_raw'],
                     'do': ['/sys/bus/iio/devices/iio:device2/out_voltage0_raw']},
         'TCU5000': {'serial_port': ['/dev/rs485s0p1', '/dev/rs485s0p2', '/dev/rs485s0p3', '/dev/rs485s0p4',
                                     '/dev/rs232s0p1'],
                     'can_channel': ['cans0p1','cans0p2','cans0p3','cans0p4'],
                     'sensor': ['/sys/class/hwmon/hwmon2/temp1_input', '/sys/class/hwmon/hwmon2/humidity1_input']},
         }

device = None
com_bitrate = None
com_byte = None
com_stop = None
com_parity = None

can_bitrate = None

coms = globals()
cans = globals()
# dos = globals()


def instance_serial():
    for i in range(len(DICT_[device]['serial_port'])):
        coms[DICT_[device]['serial_port'][i]] = serialbus.Serial(DICT_[device]['serial_port'][i], com_bitrate, com_byte, com_stop, com_parity)


def instance_can():
    for i in range(len(DICT_[device]['can_channel'])):
        cans[DICT_[device]['can_channel'][i]] = canbus.Can(DICT_[device]['can_channel'][i], can_bitrate)


# def instance_do():
#     for i in range(len(DICT_[device]['do'])):
#         dos[DICT_[device]['do'][i]] = do.Do(DICT_[device]['do'][i])


def loop_read_serial():
    # while True:
    #     for i in range(len(DICT_[device]['serial_port'])):
    #         coms[DICT_[device]['serial_port'][i]].receive()
    for i in range(len(DICT_[device]['serial_port'])):
        _thread.start_new_thread(coms[DICT_[device]['serial_port'][i]].receive, ())
        # coms[DICT_[device]['serial_port'][i]].receive()


def loop_send_serial():
    # while True:
    #     for i in range(len(DICT_[device]['serial_port'])):
    #         coms[DICT_[device]['serial_port'][i]].send()
    for i in range(len(DICT_[device]['serial_port'])):
        _thread.start_new_thread(coms[DICT_[device]['serial_port'][i]].send, ())


def loop_read_can():
    # while True:
    #     for i in range(len(DICT_[device]['can_channel'])):
    #         cans[DICT_[device]['can_channel'][i]].receive()
    #         pass
    for i in range(len(DICT_[device]['can_channel'])):
        _thread.start_new_thread(cans[DICT_[device]['can_channel'][i]].receive, ())


def loop_send_can():
    # while True:
    #     for i in range(len(DICT_[device]['can_channel'])):
    #         # cans[DICT_[device]['can_channel'][i]].send()
    #         pass
    for i in range(len(DICT_[device]['can_channel'])):
        _thread.start_new_thread(cans[DICT_[device]['can_channel'][i]].send, ())


def loop_refresh():
    global linnum
    while True:
        stdscr.addstr(1, 0, INFO_)
        linnum = c_y
        for i in range(len(DICT_[device]['serial_port'])):
            linnum += 1
            str_com = DICT_[device]['serial_port'][i] + ' rx: ' + str(coms[DICT_[device]['serial_port'][i]].get_receive_bytes()) + ' tx: ' + \
                      str(coms[DICT_[device]['serial_port'][i]].get_send_bytes()) + '\n'
            stdscr.addstr(linnum, 0, str_com)

        if 'can_channel' in DICT_[device]:
            for j in range(len(DICT_[device]['can_channel'])):
                linnum += 1
                str_can = DICT_[device]['can_channel'][j] + ' rx: ' + str(cans[DICT_[device]['can_channel'][j]].get_receive_bytes()) + ' tx: ' + \
                          str(cans[DICT_[device]['can_channel'][j]].get_send_bytes()) + '\n'
                stdscr.addstr(linnum, 0, str_can)

        if 'di' in DICT_[device]:
            str_di = ''
            for k in range(len(DICT_[device]['di'])):
                linnum += 1
                str_di += 'DI-' + str(k) + ': ' + di.Di.get_di_status(DICT_[device]['di'][k] + '  ')
            stdscr.addstr(linnum, 0, str_di)

        if 'do' in DICT_[device]:
            str_do = ''
            for m in range(len(DICT_[device]['do'])):
                linnum += 1
                # str_do += 'DO-' + str(m) + ': ' + dos[DICT_[device]['do'][i]].get_do_status()
                str_do += 'DO-' + str(m) + ': ' + do.Do.get_do_status(DICT_[device]['do'][m])
            stdscr.addstr(linnum, 0, str_do)

        if 'sensor' in DICT_[device]:
            str_tmp = 'temperature: ' + sensor.Sensor.get_temperature(DICT_[device]['sensor'][0], device) + ' humidity: ' + \
                      sensor.Sensor.get_humidity(DICT_[device]['sensor'][1], device)
            stdscr.addstr(linnum+1, 0, str_tmp)

        stdscr.refresh()
        time.sleep(0.8)
        # curses.endwin()


def main():
    global device
    global com_bitrate
    global com_byte
    global com_stop
    global com_parity
    global can_bitrate
    # stdscr.addstr(c_y + 5, c_x, 'please input device model(ex: EMU3000/TCU300/TCU1000/TCU3000)', curses.A_REVERSE)
    while True:
        c = input('\rplease input device model(ex: EMU3000/TCU300/TCU1000/TCU3000/TCU5000)\r')
        if c == 'EMU3000':
            device = c
            break
        elif c == 'TCU300':
            device = c
            break
        elif c == 'TCU1000':
            device = c
            break
        elif c == 'TCU3000':
            device = c
            break
        elif c == 'TCU5000':
            device = c
            break
        else:
            continue

    while True:
        c = input('\rplease input com_bitrate 1-115200 2-57600 3-38400 4-19200 5-9600 6-4800 7-2400 8-1200 9-600 10-300')
        if c == '1':
            com_bitrate = 115200
            break
        elif c == '2':
            com_bitrate = 57600
            break
        elif c == '3':
            com_bitrate = 38400
            break
        elif c == '4':
            com_bitrate = 19200
            break
        elif c == '5':
            com_bitrate = 9600
            break
        elif c == '6':
            com_bitrate = 4800
            break
        elif c == '7':
            com_bitrate = 2400
            break
        elif c == '8':
            com_bitrate = 1200
            break
        elif c == '9':
            com_bitrate = 600
            break
        elif c == '10':
            com_bitrate = 300
            break
        else:
            continue

    while True:
        c = input('\rplease input com_byte_size 1-8bit 2-7bit 3-6bit 4-5bit                                            ')
        if c == '1':
            com_byte = serial.EIGHTBITS
            break
        elif c == '2':
            com_byte = serial.SEVENBITS
            break
        elif c == '3':
            com_byte = serial.SIXBITS
            break
        elif c == '4':
            com_byte = serial.FIVEBITS
            break
        else:
            continue

    while True:
        c = input('\rplease input com_stop_bits 1-1bit 2-2bit 3-1.5bit                                                 ')
        if c == '1':
            com_stop = serial.STOPBITS_ONE
            break
        elif c == '2':
            com_stop = serial.STOPBITS_TWO
            break
        elif c == '3':
            com_stop = serial.STOPBITS_ONE_POINT_FIVE
            break
        else:
            continue

    while True:
        c = input('\rplease input com_parity 1-None 2-Odd 3-Even                                                       ')
        if c == '1':
            com_parity = serial.PARITY_NONE
            break
        elif c == '2':
            com_parity = serial.PARITY_ODD
            break
        elif c == '3':
            com_parity = serial.PARITY_EVEN
            break
        else:
            continue

    while True:
        c = input('\rplease input can_bitrate 1-1000K 2-800K 3-500k 4-250k 5-100K 6-50K 7-20K 8-15K 9-10k 10-5k        ')
        if c == '1':
            can_bitrate = 1000000
            break
        elif c == '2':
            can_bitrate = 800000
            break
        elif c == '3':
            can_bitrate = 500000
            break
        elif c == '4':
            can_bitrate = 250000
            break
        elif c == '5':
            can_bitrate = 100000
            break
        elif c == '6':
            can_bitrate = 50000
            break
        elif c == '7':
            can_bitrate = 20000
            break
        elif c == '8':
            can_bitrate = 15000
            break
        elif c == '9':
            can_bitrate = 10000
            break
        elif c == '10':
            can_bitrate = 5000
            break
        else:
            continue

    # if 'do' in DICT_[device]:
    #     instance_do()

    if 'can_channel' in DICT_[device]:
        instance_can()
        loop_read_can()
        loop_send_can()
    instance_serial()
    # _thread.start_new_thread(loop_read_can, ())
    # _thread.start_new_thread(loop_send_can, ())
    loop_read_serial()
    loop_send_serial()

    _thread.start_new_thread(loop_refresh, ())
    # _thread.start_new_thread(loop_read_serial, ())
    # _thread.start_new_thread(loop_send_serial, ())

    while True:
        select = input()
        if select == 'a':
            for i in range(len(DICT_[device]['serial_port'])):
                # coms[ports[i]].flushOutput()
                coms[DICT_[device]['serial_port'][i]].set_send_flag(True)

        elif len(select) == 2 and select[0] == 'c' and 1 <= int(select[1]) <= len(DICT_[device]['serial_port']):
            coms[DICT_[device]['serial_port'][int(select[1]) - 1]].set_send_flag(True)

        elif select == '2':
            for i in range(len(DICT_[device]['serial_port'])):
                coms[DICT_[device]['serial_port'][i]].set_send_flag(False)

        elif select == '3':
            for i in range(len(DICT_[device]['serial_port'])):
                coms[DICT_[device]['serial_port'][i]].clear_receive_bytes()

        elif select == '4':
            for i in range(len(DICT_[device]['serial_port'])):
                coms[DICT_[device]['serial_port'][i]].clear_send_bytes()

        elif select == '5':
            for i in range(len(DICT_[device]['can_channel'])):
                cans[DICT_[device]['can_channel'][i]].set_send_flag(True)

        elif select == '6':
            for i in range(len(DICT_[device]['can_channel'])):
                cans[DICT_[device]['can_channel'][i]].set_send_flag(False)

        elif select == '7':
            for i in range(len(DICT_[device]['can_channel'])):
                cans[DICT_[device]['can_channel'][i]].clear_receive_bytes()

        elif select == '8':
            for i in range(len(DICT_[device]['can_channel'])):
                cans[DICT_[device]['can_channel'][i]].clear_send_bytes()

        # elif select == '9':
        #     for i in range(len(DICT_[device]['do'])):
        #         dos[DICT_[device]['do'][i]].set_do_status(1)
        #
        # elif select == '10':
        #     for i in range(len(DICT_[device]['do'])):
        #         dos[DICT_[device]['do'][i]].set_do_status(0)

        elif len(select) == 3 and select[0:2] == 'do' and select[2] == '1':
            for i in range(len(DICT_[device]['do'])):
                do.Do.set_do_status(DICT_[device]['do'][i], 1)
                # dos[DICT_[device]['do'][i]].set_do_status(1)

        elif len(select) == 3 and select[0:2] == 'do' and select[2] == '0':
            for i in range(len(DICT_[device]['do'])):
                do.Do.set_do_status(DICT_[device]['do'][i], 0)
                # dos[DICT_[device]['do'][i]].set_do_status(0)

        elif len(select) == 3 and select[0] == 'd' and 1 <= int(select[1]) <= len(DICT_[device]['do']) and select[2] == '1':
            do.Do.set_do_status(DICT_[device]['do'][int(select[1]) - 1], 1)
            # dos[DICT_[device]['do'][int(select[1]) - 1]].set_do_status(1)

        elif len(select) == 3 and select[0] == 'd' and 1 <= int(select[1]) <= len(DICT_[device]['do']) and select[2] == '0':
            do.Do.set_do_status(DICT_[device]['do'][int(select[1]) - 1], 0)
            # dos[DICT_[device]['do'][int(select[1]) - 1]].set_do_status(0)

        else:
            pass
            # print('input error, please retry!')


if __name__ == '__main__':
    main()
    curses.endwin()