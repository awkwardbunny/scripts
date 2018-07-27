#!/usr/bin/env python3

'''
    dump_amboot.py

    Dump memory contents into a file over serial.
    Written for Parrot's new Anafi drone, which uses amboot for its bootloader.
    The UART serial pins can be found near the SD card holder.
    After attaching to the serial device, amboot shell can be accessed by booting
    the drone while holding down enter.

    This script reads 4 bytes at a time using the read command.
    This is very slow.
'''

import serial
import time
import struct
import argparse
import sys

def s_open(port, baud):
    print('Opening serial port {}'.format(port))
    return serial.Serial(port, baud) #, timeout=0.1)

def getPrompt(ser, ps):
    ser.write(b'\r\n')
    while(not ser.readline().decode('ascii').startswith(ps)):
        pass

def main(port, baud, output):
    # Initialize serial port
    ser = s_open(port, baud)
    ser.flushInput()
    ser.flushOutput()

    # Initial shell
    print('Waiting for amboot shell...')
    #print('Please turn on device if not already on')
    getPrompt(ser, 'amboot>')
    print('Got amboot!')

    # Dump memory to file
    dump(ser, 0x0, 0xffffffff, output)

def patch(ser, beg, data):
    # TODO
    return

def dump(ser, beg, end, fn):

    print('Writing to file {}'.format(fn))
    with open(fn,'wb') as out:
        for addr in range(beg, end, 4):

            # Only print every 0x100 bytes
            if addr%0x100 == 0:
                print('Reading {}...'.format(hex(addr)))
            
            # Read a word
            line = send(ser,'read {}'.format(hex(addr)))

            # Check if it crashed and reset
            if line == 'DEADBEEF':
                print("### CRASH ###")
                ser.write(b'\r\n')
                ser.write(b'\r\n')
                ser.write(b'\r\n')
                ser.write(b'\r\n')
                getPrompt(ser, 'amboot>')
                print('Serial terminal reset')
                break

            # Process output and write to file
            word = line.split(': ')[1][2: ]
            data = bytes.fromhex(word)[::-1] # Endianness convert
            out.write(data)
    print('done.')

def send(ser, msg):

    # Send the command
    ser.write(msg.encode('ascii')+b'\r\n')

    # Wait and read the same line back "amboot> $msg"
    ser.readline()

    # Read and combine reply
    data = ''
    line =  ser.readline().decode('ascii')
    while(not line.startswith('amboot>')):

        # If it crashes and reset, return 'DEADBEEF'
        # When it resets, the first line is 'test'
        if line.startswith('test'):
            return 'DEADBEEF'
        data += line
        line =  ser.readline().decode('ascii')

    # Strip trailing whitespace and return
    return data.rstrip()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Amboot memory dumper', prog=sys.argv[0])

    parser.add_argument(
        '--port','-p',
        help='Serial port device',
        default='/dev/ttyUSB0')

    parser.add_argument(
        '--baud','-b',
        help='Serial port baudrate',
        default=115200)

    parser.add_argument(
        '--out','-o',
        help='Dump output filename',
        default='dump.bin')

    args = parser.parse_args()
    main(args.port, args.baud, args.out)
