'''
neatopylot_agent.py - agent code for Neato XV-11 Autopylot 

Copyright (C) 2014 Simon D. Levy

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

class Neatopylot_Agent:
    
    def __init__(self):
        '''Initialize any attributes you need for your agent.
        '''
        pass
        
    def getAxes(self, scan, canvas):
        """Performs your agent's main work.
    
        Args:
            scan: A list of (degrees, distance) tuples.
            canvas: A breezypythongui.EasyCanvas object that you can draw on
    
        Returns:
            A tuple (axis_x, axis_y) for driving the XV-11.  Axis values should be
            in the inteval [-1,+1].
        """
        
        # Default: turn around to the right
        return (1, 0)

