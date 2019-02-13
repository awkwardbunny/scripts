#!/usr/bin/env python3
import serial
import time
import struct
import argparse
import sys

'''
    dump_buspirate_spi_binary.py

    Binary mode version of dump_buspirate_spi.pu

    Dump memory contents into a file over serial.
    Written originally because flashrom couldn't read MX25L25635F properly.
    It read all 0's until I tried bus pirate and with the last SPI option (H instead of Hi-Z) set.
'''

commands = {
    'BBIO1': b'\x00',
    'SPI1': b'\x01',
    'CS_L': b'\x01',
    'CS_H': b'\x01',
    'READ': b'\x10',
    'SPEED': b'\x60'
}

def s_open(port, baud):
    print('Opening serial port {}'.format(port))
    return serial.Serial(port, baud, timeout=0.01)

def main(port, baud, output):

    # Initialize serial port
    ser = s_open(port, baud)
    ser.flushInput()
    ser.flushOutput()

    print('Attempting to enter binary mode')
    #ser.write(b'\x00'*20)
    #time.sleep(0.01)
    line = ''
    for i in range(25):
        line = ser.read(5)
        print('Attempt {}: {}'.format(i,line))
        if line == b'BBIO1':
            break
        ser.write(b'\x00')
        time.sleep(0.01)
    #if not enterBinary(ser):
    #    print('Failed!')
    #    ser.close()
    #    sys.exit()
    #print('Success!')

    line = ser.read(5)
    while line == b'BBIO1':
        print('Clearing buffer: {}'.format(line))
        line = ser.read(5)

    print('Buffer should be empty: {}'.format(line))
    print('(y)')

    print('Entering SPI mode')
    line = b''
    while not line == b'SPI1':
        ser.write(b'\x01')
        time.sleep(0.01)
        line = ser.read(5)
        print(line)
       # if not line == b'SPI1':
       #     print('Failed!')
       #     ser.close()
       #     sys.exit()
    print('Success!') 

    print('Configuring speed.')
    if not sendConf(ser,bytes([commands.get('SPEED')[0] & b'\x00'[0]])):
        print('Failed!')
        ser.close()
        sys.exit()
    print('Success!')

    print('Configuring SPI.')
    if not sendConf(ser,bytes(b'\x8a')):
        print('Failed!')
        ser.close()
        sys.exit()
    print('Success!')

    sys.exit()

    print('Sending a read command from 0x0')
    ser.write(b'\x14')
    ser.write(b'\x03\x00\x00\x00')
    ser.read(4)

    print('Reading data')
    ser.write(b'\x1F')
    ser.write(b'\x00'*16)
    data = ser.read(16)
    print(data)

    sys.exit()

    send(ser, '2')

    size = 32*1024*1024
    each_read = 4*1024

    # Dump
    dump(ser, 0x0, size, each_read, output)

def enterBinary(ser):
    for i in range(25): # Needs 20 times, but for extra
        ser.write(commands.get('BBIO1'))
        time.sleep(0.01)
        line = ser.read(5)
        #print('Attempt {}: {}'.format(i,line))
        if line == b'BBIO1':
            return True
    return False

def sendConf(ser,cmd):
    ser.write(cmd)
    time.sleep(0.01)
    line = ser.read(1)
    print('Read: {}'.format(line))
    if line == b'\x00':
        return False
    return True

def dump(ser, beg, end, step, fn):

    # TODO beginning address currently not used; always starts from zero
    # This is because I'm too lazy to read on whether LSB goes first or last

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

    # Wait and read the same line back
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

    parser = argparse.ArgumentParser(description='Buspirate SPI dumper', prog=sys.argv[0])

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
