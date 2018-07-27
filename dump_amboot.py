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

import serial,time,struct

def s_open():
    port = '/dev/ttyUSB0'
    baud = 115200

    print('Opening serial port {}'.format(port))
    return serial.Serial(port, baud) #, timeout=0.1)

def getPrompt(ser, ps):
    ser.write(b'\r\n')
    while(not ser.readline().decode('ascii').startswith(ps)):
        pass
    print('Got amboot!')

def main():
    # Initialize serial port
    ser = s_open()
    ser.flushInput()
    ser.flushOutput()

    # Initial shell
    print('Waiting for amboot shell...')
    #print('Please turn on device if not already on')
    getPrompt(ser, 'amboot>')

    # Dump memory to file
    #dump(ser, 0, 0x1000, 'Bootstrap.bin')
    #dump(ser, 0x10000000, 0x10025f70, 'Bootloader.bin')
    #dump(ser, 0x4000, 0x8020, 'ARM_TRUST_FW.bin')

    #dump(ser, 0x0, 0xffffffff, 'dump.bin')
    #dump(ser, 0x500000, 0xffffffff, 'dump.bin')
    #dump(ser, 0x40680000, 0x40680000+9187336, 'kernel.bin')

def patch(ser, beg, data):
    # TODO
    return

def dump(ser, beg, end, fn):
    print('Writing to file {}'.format(fn))
    with open(fn,'wb') as out:
        for addr in range(beg, end, 4):
            if addr%0x100 == 0:
                print('Reading {}...'.format(hex(addr)))
            line = send(ser,'read {}'.format(hex(addr)))
            if line == 'DEADBEEF':
                print("### CRASH ###")
                ser.write(b'\r\n')
                ser.write(b'\r\n')
                ser.write(b'\r\n')
                ser.write(b'\r\n')
                ser.write(b'\r\n')
                ser.write(b'\r\n')
                while(not ser.readline().decode('ascii').startswith('amboot>')):
                    pass
                print('Serial terminal reset')
                break
            word = line.split(': ')[1][2: ]
            data = bytes.fromhex(word)[::-1]
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
        if line.startswith('test'):
            return 'DEADBEEF'
        data += line
        line =  ser.readline().decode('ascii')

    # Strip trailing whitespace and return
    return data.rstrip()

if __name__ == '__main__':
    main()
