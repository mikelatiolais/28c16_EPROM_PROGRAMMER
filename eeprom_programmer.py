#!/usr/bin/python

import sys
import serial
import binascii
import time
from sys import argv

# eeprom_programmer.py <read/write> OPTIONS
# Command line options:
# -i <input file>		The binary file to be read
# -o <output file>		The file to be written to 
# -s <serial port>		The serial port to be used
# -z <size in bytes>            The size of the image to read in bytes
# We assume 9600 baud for simplicity

def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    operation = ""
    while argv:  # While there are arguments left to parse...
        if argv[0] == 'read':  # Found a "-name value" pair.
            operation = "read"
        if argv[0] == 'write':  # Found a "-name value" pair.
            operation = "write"
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return (operation,opts)

(operation,myargs) = getopts(argv)
print "Operation: ",operation

current_index = 0


# Open serial port
ser = serial.Serial()
ser.baudrate = 9600
ser.port = myargs['-s']
ser.timeout = 2
ser.open()
time.sleep(3) # wait for Arduino
ser.write(b"V\n")
print "I wrote V"
read_val = ser.readline()
print "I read from serial"
print read_val


# Depending on the operation, either read in or write out
if operation == "write":
  with open(myargs['-i'], 'rb') as f:
      # Slurp the whole file and efficiently convert it to hex all at once
      hexdata = binascii.hexlify(f.read())
  hexlist = map(''.join, zip(hexdata[::2], hexdata[1::2]))

  print hexlist
  rom_length = len(hexlist)
  print rom_length
  for x in range(0,rom_length):
    hex_addr = hex(x)
    val = hexlist[x]
    serial_string = "W" + hex_addr + ":" + val + "\n"
    print serial_string
    ser.write(serial_string)
    read_val = ser.readline()
    print "Got: ",read_val

if operation == "read":
  fh = open(myargs['-o'],"w")
  for x in range(0,int(myargs['-z'])):
    serial_string = "R" + hex(x) + "\n"
    print serial_string
    ser.write(serial_string)
    read_val = ser.readline()
    print "Got:" , read_val


ser.close() 