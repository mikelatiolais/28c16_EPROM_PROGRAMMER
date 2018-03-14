#!/usr/bin/python

import sys
import serial
import binascii
import time
import re
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
        if argv[0] == 'read':  # Found the read operation
            operation = "read"
        if argv[0] == 'write':  # Found the write operation
            operation = "write"
        if argv[0] == 'compare':  # Found the compare operation
            operation = "compare"
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return (operation,opts)

def write_byte(address, byte_val):
  serial_string = "W" + address + ":" + byte_val + "\n"
  print "Attempting: ", serial_string
  try:
    ser.write(serial_string)
    read_val = ser.readline()
  except:
    print "Error writing to EEPROM"
    sys.exit()
  return read_val

def read_byte(address):
  serial_string = "R" + address + "\n"
  print "Attempting: ", serial_string
  try:
    ser.write(serial_string)
    read_val = ser.readline()
    while "OK" in read_val:
      read_val = ser.readline()
  except:
    print "Error writing to EEPROM"
    sys.exit()
  # Split on colon
  #print "Read_val: ", read_val
  byte_list = re.split(r'[:,]', read_val)
  return byte_list[1][:2]
  

(operation,myargs) = getopts(argv)
print "Operation: ",operation

current_index = 0


# Open serial port
ser = serial.Serial()
ser.baudrate = 9600
ser.port = myargs['-s']
ser.timeout = .01 
try:
  ser.open()
except:
  print "Unable to open the serial port: ",myargs['-s']
  sys.exit()

time.sleep(3) # wait for Arduino


# Depending on the operation, either read in or write out
if operation == "write":
  try:
    with open(myargs['-i'], 'rb') as f:
        # Slurp the whole file and efficiently convert it to hex all at once
        hexdata = binascii.hexlify(f.read())
  except:
    print "Error opening input file"
    sys.exit()
  hexlist = map(''.join, zip(hexdata[::2], hexdata[1::2]))

  print hexlist
  rom_length = len(hexlist)
  print rom_length
  for x in range(0,rom_length):
    hex_addr = format(x, 'x')
    val = hexlist[x]
    read_val = write_byte(hex_addr, val)
    print "Got: ",read_val
    print "Now attempting to read back the value"
    new_val = read_byte(hex_addr)
    print "New value: ", new_val
    if val != new_val:
      print "ERROR: Bytes don't match"
      exit(1)
    

if operation == "read":
  try:
    fh = open(myargs['-o'],"ab")  # Open binary output file
  except:
    print "Error opening output file"
    sys.exit()

  for x in range(0,int(myargs['-z']),16):
    serial_string = "R" + format(x, 'x') + "\n"
    print serial_string
    try:
      ser.write(serial_string)
      read_val = ser.readline()
    except:
      print "Error reading from EEPROM"
      sys.exit()
    print "Got:" , read_val
    # Get response
    response = ser.readline()
    byte_list = re.split(r'[:,]', read_val)
    fh.write(binascii.unhexlify(byte_list[1]))
  fh.close()

if operation == "compare":
  print "Compare"
  # Grab binary file data
  # Assume that the file size and the image are the same 
  try:
    with open(myargs['-i'], 'rb') as f:
        # Slurp the whole file and efficiently convert it to hex all at once
        hexdata = binascii.hexlify(f.read())
  except:
    print "Error opening input file"
    sys.exit()
  hexlist = map(''.join, zip(hexdata[::2], hexdata[1::2]))
  # Go through the ROM contents and compare each 16 bytes
  for x in range(0,int(myargs['-z'])):
    address = format(x, 'x')
    read_val = read_byte(address)
    print "Got: ", read_val
    image_val = hexlist[x]
    if image_val == read_val:
      print "Correct"
    else:
      print "ERROR: ROM does not match at address: ", address

ser.close() 
