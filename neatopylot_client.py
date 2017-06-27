#!/usr/bin/env python
'''
neatopylot_client.py - client code for Neato XV-11 Autopylot 

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

24-JAN-2013 Suraj Bajracharya    Initial version as SLAMgui.py

28-JAN-2013 Simon D. Levy        Timer-based update

29-JAN-2013 SDL                  Fixed degrees->radians conversion

04-FEB-2013 SDL                  True LIDAR display

12-FEB-2013 SDL                  Steers XV-11 via joystick

22-FEB-2013 SDL                  Uses arrow keys when joystick not available

09-SEP-2014 SDL                  Migrated to github
'''
# Params =======================================================================

# Update period in milliseconds (less than 200 may cause problems!)
UPDATE_MSEC = 200

# Index of base axis of controller
FIRST_AXIS = 2

# Index of autopilot button
AUTOPILOT_BUTTON = 9

# Maximum LIDAR distance in mm
MAX_LIDAR_DIST_MM = 2500

# Motor parameters
DIST  = 10000 # Arbitrarily large distance to simulate infinity
SPEED = 200

# Frame title
BASE_TITLE = "Neatopylot"

DISPLAY_SIZE         = 500        # square
BACKGROUND_COLOR     = "black"
FOREGROUND_COLOR     = "green"

# ==============================================================================

import socket
import sys
import struct
import time
from math import *

import breezypythongui

# Import agent code
from neatopylot_agent import *
    
# Import constants common to client and server
from neatopylot_header import *

# Import  pygame: Comment-out if you have problems!
import pygame
#pygame = None
    

# XXX popup
def error(dlg, msg):
    dlg.messageBox("Error", msg)
    sys.exit(1)
    
def message(dlg, msg):
    dlg.messageBox("Alert", msg)

class Neato_Client:
    
    # Constructor opens socket to server
    def __init__(self, host, port):
        
        # Connect to host over port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
            
        # Track drive commands for update    
        self.lastx, self.lasty = 0,0
        
        
    # Get LIDAR scan. 
    # Returns scan as a list of (angle, distance, intensity) tuples
    def getScan(self):
        
        # Request a LIDAR scan from the server
        self._send_message('scan')
        
        # Grab the current scan buffer from the server
        scandata = ''
        while True:
            buf = self.sock.recv(MAX_SCANDATA_BYTES)
            scandata += buf.decode('utf-8')
            if len(buf) < MAX_SCANDATA_BYTES:
                break
                                
        # Parse the scan into a list of tuples
        scanvals = []
        for line in scandata.split('\n'):
            try:
                vals = line.split(',')
                # Only use legitimate scan tuples with zero error
                if len(vals) == 4 and not int(vals[3]):
                    angle = int(vals[0])
                    distance = int(vals[1])
                    intensity = int(vals[2])
                    scanvals.append((angle, distance, intensity))
                    
            except:
                None
                
        return scanvals
        
    # Drives in specified direction
    def drive(self, x, y):
                
        # Status changed
        if (x,y) != (self.lastx,self.lasty):
                                              
            # Special handling for halt
            if x == 0 and y == 0: 
                self._setMotors(1, 1, 1)
                
            # Convert (x,y) joystick to motor scaling factors
            # XXX Maybe we can simplify this
            
            if y == 0:
                
                if x > 0:
                    lft,rgt = 1,0
                elif x < 0:
                    lft,rgt = 0,1
                else:
                    lft,rgt = 0,0
                    
            else:
                
                if x > 0:
                    lft,rgt = 1.0,0.5
                elif x < 0:
                    lft,rgt = 0.5,1.0
                else:
                    lft,rgt = 1.0,1.0
                    
                lft *= y
                rgt *= y
                
            self._setMotors(int(lft*DIST), int(rgt*DIST), SPEED)
            
        # Track previous joystick status for update
        self.lastx, self.lasty = x, y

    # Done            
    def close(self):
        self.sock.close()

        
    # Send robot server a mesage to set motor distances and speed
    def _setMotors(self, leftDist, rightDist, speed):
        message = 'm ' + str(leftDist) + ' ' + str(rightDist) + ' ' + str(speed)
        self._send_message(message)
        
    # Send robot server a message padded to MESSAGE_SIZE_BYTES
    def _send_message(self, msg):
        while len(msg) < MESSAGE_SIZE_BYTES:
            msg += ' '
        self.sock.send(bytes(msg.encode('utf-8')))
            
            
# GUI ==========================================================================

class LIDAR_GUI(breezypythongui.EasyFrame):
    
    def __init__(self, host, port, client, controller, agent):
        
        # Set up the window
        breezypythongui.EasyFrame.__init__(self, title = BASE_TITLE)
        
        # Report missing client
        if not client:
            error(self, 'Unable to connect to server on host ' + 
                host + ' over port ' + str(port) + 
             '. Make sure server is running and try again.')
            
        # Canvas
        self.canvas = self.addCanvas(row = 0, column = 0,
            columnspan = 1,
            width = DISPLAY_SIZE,
            height = DISPLAY_SIZE,
            background = BACKGROUND_COLOR)
        self.setResizable(False)
        
        # Holds the vectors after they're drawn
        self.items = list()
        
        # Track drive commands for update    
        self.lastx, self.lasty = 0,0
        
        # Store stuff for timer task
        self.client = client
        self.controller = controller
        self.lastpress_sec = 0
        self.keydown = False
        self.autopilot = False
        self.agent = agent

        # Set up window-close handler
        self.bind('<Destroy>', self.quit)

    def quit(self, event):
        self.client.close()

# Deadband filter for noisy controller
def deadbandFilter(value):
    
    return 0 if abs(value) < .01 else value
        
        
# Timer task for gui update
def task(gui):
    
    # Assume no axis input
    axis_x, axis_y = 0,0
    
    # Use controller if available
    if gui.controller:
        
        # Force joystick polling
        pygame.event.pump()    
        
        # Pressing autopilot button turns on autopilot; other buttons turn it off
        for k in range(gui.controller.get_numbuttons()):
            if gui.controller.get_button(k):
                if k == AUTOPILOT_BUTTON:
                    gui.autopilot = True
                #else:
                #    gui.autopilot = False
        
        # Grab joystick axis values (forward comes in negative)
        axis_x = deadbandFilter(gui.controller.get_axis(FIRST_AXIS))
        axis_y = deadbandFilter(-gui.controller.get_axis(FIRST_AXIS+1))
        
        # Axes disable autopilot
        if axis_x or axis_y:
            gui.autopilot = False
                
    # If no controller, use timing to check key-release    
    else:
                
        lag = 1000 * (time.time() - gui.lastpress_sec) 
        if lag < UPDATE_MSEC:
            if gui.keydown:
                axis_x, axis_y = gui.axis_x, gui.axis_y
            gui.keydown = True
        else:
            gui.keydown = False
            
    # Request a LIDAR scan from the server
    scan = gui.client.getScan()
    
    # Clear the canvas
    for item in gui.items:
        gui.canvas.deleteItem(item)
        gui.items = list()
        
    # Locate the center of the screen (also the scaling factor)
    ctr = DISPLAY_SIZE / 2
    
    # Read the distance values and draw them as line segments
    for scanline in scan:
        angle = scanline[0]
        dist  = scanline[1]
        angle = angle * pi / 180         # degrees to radians
        dist = dist / float(MAX_LIDAR_DIST_MM)    # millimeters to (0,1)
        scale = ctr
        x = ctr - (scale * dist * sin(angle))
        y = ctr - (scale * dist * cos(angle))
        gui.items.append(gui.canvas.drawLine(ctr, ctr, x, y, 
                fill=FOREGROUND_COLOR))

    # We will update the title based on whether the autpilot is on     
    title = BASE_TITLE 
    
    if gui.autopilot:
        
        title += '    AUTOPILOT ON'
        
        # Get action from agent
        axis_x, axis_y = gui.agent.getAxes(scan, gui.canvas)
            
    # Update the title to report autopilot as needed
    gui.setTitle(title)
    
    # Use axis values to drive robot
    gui.client.drive(axis_x, axis_y)
        
    # Reschedule event
    gui.after(UPDATE_MSEC, task, gui)            
        
        
# Key-press handler for GUI frame    
def keypress(event):  
        
    # Strip literal quotes from key symbol
    keysym = repr(event.keysym)[1:-1]
    
    # Assume no arrow keys pressed    
    event.widget.axis_x, event.widget.axis_y = 0,0
    
    # Check all arrow keys
    if keysym == 'Right':
        event.widget.axis_x = +1
    elif keysym == 'Left':
        event.widget.axis_x = -1
    if keysym == 'Up':
        event.widget.axis_y = +1
    elif keysym == 'Down':
        event.widget.axis_y = -1
     
    # Spacebar toggles autopilot 
    elif keysym == 'space':
        event.widget.autopilot = not event.widget.autopilot
        
    # If any arrow key was pressed, axes have been set    
    if event.widget.axis_x or event.widget.axis_y:
                
        # Record arrow-key press time for fake release
        event.widget.lastpress_sec = time.time()   
        
        # Axis control disables autopilot
        event.widget.autopilot = False
           
# main =========================================================================
    
# Create client on host, port specified on command line
try:
    client = Neato_Client(HOST, PORT)
except:
    client = None

# Assume no controller
controller = None

# Set up PyGame and the controller if available
if pygame:
    pygame.joystick.init()
    pygame.display.init()
    try:
        controller = pygame.joystick.Joystick(0)
        controller.init()
        try:
            controller.get_axis(FIRST_AXIS)
        except:
            controller = None
    except:
        pass
        
# Initialize the autopilot agent
agent = Neatopylot_Agent()
        
# Create gui with host, port, controller
gui = LIDAR_GUI(HOST, PORT, client, controller, agent)
    
# Start timer-task
gui.after(UPDATE_MSEC, task, gui)

# Use arrow keys if no controller
if not controller:
    message(gui, 'No joystick available: Use arrow keys and spacebar')                 
    gui.bind('<Key>', keypress)
    gui.focus_set()
    
# Handle GUI events till done
gui.mainloop()


