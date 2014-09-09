#!/usr/bin/env python
'''
neatopylot_server.py - server code for Neato XV-11 Autopylot 

Copyright (C) 2013 Suraj Bajracharya and Simon D. Levy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.


Revision history:


22-FEB-2013 Simon D. Levy   Initial release

09-SEP-2014 SDL             Migrated to github

'''

DEVICE = '/dev/ttyACM0'               # Raspbian
#DEVICE = '/dev/tty.usbmodem1d131'    # Mac OS X
#DEVICE = 'DEBUG'                     # Debugging

import serial
import socket
import time
import sys

# Import values and functions common to client and server
from neatopylot_header import *

# Serial-port timeout
TIMEOUT_SEC  = 0.1

# Sends LF-terminated command to robot and reads result
def docommand(port, command):
    port.write(command + '\n')
    
 
# main =========================================================================

# Default to no robot (test mode)
robot = None
    
# DEBUG is special name to enable debugging    
if DEVICE != 'DEBUG':
    try:
        robot = serial.Serial(DEVICE, 115200, \
            serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, TIMEOUT_SEC)
    except serial.SerialException:
        print('Unable to connect to XV-11 as device ' + DEVICE)
        print('Make sure XV-11 is powered on and USB cable is plugged in!')
        sys.exit(1)
    
    # Put the XV-11 into test mode
    docommand(robot, 'TestMode on')
    
    # Spin up the LIDAR
    docommand(robot, 'SetLDSRotation on')
    
else:
    print('No robot connected; running in test mode')
    

# Keep accepting connections on socket
while True:
    
    # Serve a socket on the host and port specified on the command line

    sock = None   
    
    while True:
    
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        try:
            sock.bind((HOST, PORT))
            break
        
        except socket.error as err:
            print('Bind failed: ' + str(err))
        
        time.sleep(1)
        
    sock.listen(1) 

    # Accept a connection from a client
    print('Waiting for client to connect ...')
    try:
        client, address = sock.accept()
        print('Accepted connection')
    except:
        break
       
    # Handle client requests till quit
    while True:
    
        try:
    
            # Get message from client
            msg = client.recv(MESSAGE_SIZE_BYTES)
            
            # Strip trailing whitespace
            msg = msg.rstrip() 
            
            if  not len(msg):
                print('Client quit')
                break
                                
            if msg[0] ==  's':
                        
                scandata = None
            
                # Robot sends scaled LSD sensor values scaled to (0,1)
                if robot:
                
                    # Run scan command
                    docommand(robot, 'GetLDSScan')
                            
                    # Grab scan results till CTRL-Z
                    scandata = robot.read(MAX_SCANDATA_BYTES)
                                
                # Stubbed version sends constant distances
                else:
                    scandata = ''
                    for k in range(360):
                        scandata = scandata + str(k) + ',1500,100,0\n'
                    
                # Send scan results to client
                client.send(scandata)
            
            elif msg[0] == 'm':
                        
                command = 'SetMotor' + msg[1:]    
                                    
                if robot:
                    docommand(robot, command)
                
                else:
                    print(command) 
                            
        except ValueError as ex:
            break
                
    # Done talking to client
    client.close()

# Shut down the XV-11
    
if (robot):

    print('Shutting down ...')
    
    # Spin down the LIDAR
    docommand(robot, 'SetLDSRotation off')
    
    # Take the XV-11 out of test mode
    docommand(robot, 'TestMode off')
    
    # Close the port
    robot.close()   
    
    # Wait a second while the LIDAR spins down
    time.sleep(1)


