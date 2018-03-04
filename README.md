# 28c16_EPROM_PROGRAMMER
A variant of a DIY EEPROM Programmer found on http://danceswithferrets.org/geekblog/?p=496

This includes the .ino file for the Arduino mega, hacked up from the original, and a quick and dirty python script to read/write

Script arguments:
```python
# eeprom_programmer.py <read/write> OPTIONS
# Command line options:
# -i <input file>               The binary file to be read
# -o <output file>              The file to be written to
# -s <serial port>              The serial port to be used
# -z <size in bytes>            The size of the image to read in bytes
# We assume 9600 baud for simplicity
```
