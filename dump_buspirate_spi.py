#!/usr/bin/env python3
import serial,time,struct,argparse

'''
    dump_buspirate_spi.py

    Dump memory contents into a file over serial.
    Written originally because flashrom couldn't read MX25L25635F properly.
    It read all 0's until I tried bus pirate and with the last SPI option (H instead of Hi-Z) set.

    This script reads 4096 bytes at a time.
    Has lots of overhead ('0x' and spaces, extra processing time, etc)
    32MB calculated to take ~3.6 hours to dump...

    TODO: Use binary mode to save some time...
    http://dangerousprototypes.com/blog/2009/10/08/bus-pirate-raw-spi-mode/
'''

def s_open():
    port = '/dev/ttyUSB0'
    baud = 115200

    print('Opening serial port {}'.format(port))
    return serial.Serial(port, baud, timeout=0.001)

def main():

    # Initialize serial port
    ser = s_open()
    ser.flushInput()
    ser.flushOutput()

    # Initial prompt
    print('Waiting for prompt...')
    send(ser, '')

    # Configure for SPI
    print('Configuring for SPI')
    send(ser, 'm')
    send(ser, '5')
    send(ser, '4')
    send(ser, '')
    send(ser, '')
    send(ser, '')
    send(ser, '')
    send(ser, '2')

    size = 32*1024*1024
    each_read = 4*1024
    fn = 's0mething2.bin'

    # Dump
    dump(ser, 0x0, size, each_read, fn)

def dump(ser, beg, end, step, fn):

    # Send a read command from 0x0
    send(ser, '[3 0 0 0')

    # Dump memory to file
    print('Writing to file {}'.format(fn))
    with open(fn,'wb') as out:
        for i in range(beg, end, step):
            print('Reading {}...'.format(hex(i)))
            line = send(ser, 'r:{}'.format(step))
            data = line[8:]
            hexstr = ''.join(data.split(' 0x'))
            b = bytearray.fromhex(hexstr)
            out.write(b)
            #print(b)

    send(ser, ']')
    print('done.')

def send(ser, msg):

    # Send the command
    ser.write(msg.encode('ascii')+b'\n')
    time.sleep(0.1)

    # Wait and read the same line back "amboot> $msg"
    ser.readline().decode('ascii')

    # Read and combine reply
    data = ''
    line = ser.readline().decode('ascii')
    while(not ( \
        line.startswith('(1)>') or \
        line.startswith('(2)>') or \
        line.startswith('HiZ>') or \
        line.startswith('SPI>'))):
        data += line
        line = ser.readline().decode('ascii')

    # Strip trailing whitespace and return
    #data += line
    return data.rstrip()

if __name__ == '__main__':
    main()
