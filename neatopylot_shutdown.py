#!/usr/bin/env python
'''
neatopylot_shutdown.py - emergency shutdown for Neatopylot - ends test mode

Copyright (C) 2013 Suraj Bajracharya and Simon D. Levy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

 You should have received a copy of the GNU Lesser General Public License 
 along with this program.  If not, see <http://www.gnu.org/licenses/>
'''

DEVICE = '/dev/ttyACM0'               # Raspbian
#DEVICE = '/dev/tty.usbmodem1d131'    # Mac OS X

# Serial-port timeout
TIMEOUT_SEC  = 0.1

import serial

# Sends LF-terminated command to robot and reads result
def docommand(port, command):
    port.write(command + '\n')
    
 
# main =========================================================================

try:
    robot = serial.Serial(DEVICE, 115200, \
        serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, TIMEOUT_SEC)
except serial.SerialException:
    print('Unable to connect to XV-11 as device ' + DEVICE)
    print('Make sure XV-11 is powered on and USB cable is plugged in!')
    sys.exit(1)
    
# Take the XV-11 out of test mode
docommand(robot, 'TestMode off')
