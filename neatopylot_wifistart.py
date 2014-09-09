#!/usr/bin/env python
'''
neatopylot_wifi_start.py - Creates wifi network for Neato XV-11 Autopylot 

Copyright (C) 2013 Suraj Bajracharya and Simon D. Levy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

'''

# You can make this whatever you want to call your ad-hoc wifi network
ESSID = 'Neato-Raspberry-Pi'

# This grabs the host and port
from neatopylot_header import *

import sys
import os
import time

os.system('ifconfig wlan0 down; iwconfig wlan0 mode Ad-Hoc')
os.system('iwconfig wlan0 essid ' + ESSID)
time.sleep(1)
os.system('ifconfig wlan0 ' + HOST)
os.system('ifconfig wlan0 up')
os.system('udhcpd /etc/udhcpd.conf')
