#!/usr/bin/env python3
import serial,time,struct

port = '/dev/ttyUSB0'
baud = 115200
print('Opening serial port {} {}'.format(port,baud))
ser = serial.Serial(port, baud, timeout=0.1)
ser.flushInput()
ser.flushOutput()
