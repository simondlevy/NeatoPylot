NeatoPylot
==========

Auto-Pilot the Neato XV-11 from Python



This repository contains code for 
running a stubbed version of the XV-11 AutoPylot 
program, which allows you to auto-pilot the 
<a href="http://www.amazon.com/Neato-XV-11-Robotic-Vacuum-System/dp/B003UBPB6E">
Neato XV-11</a> wirelessly from source code written in Python.  
The stubbed agent class contains an empty <tt><b>__init__</b></tt>
method and a <tt><b>getAxes</b></tt> method that accepts a LIDAR scan
from the XV-11 and returns an (<i>x</i>, <i>y</i>) axis pair representing 
a virtual joystick position.
By modifying just these two methods you can exploit the XV-11's onboard LIDAR for 
exploring <a href="http://www.youtube.com/watch?v=XhqAgiIAI-4&feature=youtu.be">
obstacle avoidance</a>,
<a href="http://home.wlu.edu/~levys/software/breezyslam/">
SLAM</a>, and other tasks, without having to write any of your own
communication or serial-port code

<p>

As with 
<a href="http://home.wlu.edu/~levys/software/ardrone_autopylot">
AR.Drone Autopylot</a>, the idea is that you start driving the robot around using 
manual control (joystick axis), and it switches to autopilot mode when you click a 
button. Autopilot runs by sending the XV-11 the same joystick axis commands
as in manual mode. Grabbing the joystick again or clicking another button 
takes it out of autopilot.

<h3>Hardware Checklist</h3>
<ul>
<li>
Obviously, an XV-11.  Make sure it has the current 
<a href="http://www.neatorobotics.com/support/software-updates/">firmware</a>.
An 
<a href="http://www.amazon.com/Neato-XV-21-Allergy-Automatic-Cleaner/dp/B007JOJ9QQ">
XV-21</a> will probably work too, but I haven't tried one.
<p><li> A small computer with wifi capability to mount onboard the XV-11 without
blocking the LIDAR scan.
<a href="http://www.raspberrypi.org">Raspberry Pi</a> works well for this. 
The Raspberry Pi 3 has a Broadcom wifi chip onboard, saving you the hassle
of finding a wifi adapter that supports ad-hoc networking.
<p><li> A battery to power the onboard computer, if it doesn't have one built in.
<a href="https://www.amazon.com/gp/product/B00QQYIUFG/ref=oh_aui_detailpage_o06_s00?ie=UTF8&psc=1">
This rechargeable battery</a> provided around three hours of power for my Raspberry Pi, via
a six-inch micro USB cable.
<p><li> A short 
<a href="http://www.amazon.com/gp/product/B001S0I1Z2/ref=oh_details_o00_s00_i00?ie=UTF8&psc=1">USB A to mini-B cable</a>
to connect the onboard computer to the XV-11's
USB port.
<p><li> Velcro tape to keep the onboard computer (and battery) attached securely to 
the XV-11.
<p><li>A laptop computer on which to run the client program, which will talk over
wifi to the server program running on the onboard computer.  I have tested
the client on Windows, Mac OS X, and Linux, and the server on Mac OS X and 
Linux.
<p><li> A PS3 gamepad controller, 
<a href="http://www.amazon.com/Logitech-Extreme-Joystick-Silver-Black/dp/B00009OY9U">
Logitech joystick</a>, or similar device for driving the XV-11 from the laptop. 
The client will work without such a device, allowing you to drive using the
arrow keys on your keyboard, but you'll have more fun using a real
controller. I used an inexpensive, wired PS3 controller knockoff like 
<a href="http://www.amazon.com/Nyko-Core-Controller-PS3-Playstation-3/dp/B003G2Z4FK/ref=sr_1_1?s=videogames&ie=UTF8&qid=1361584521&sr=1-1&keywords=ps3+wired+controller">
this one</a>.
</ul>

<h3>Software Checklist</h3>

Both the server and client are written in Python, so you will need to have Python
running on both the laptop and onboard computer.  I have tested both the
server and client in Python 2 and Python 3. You will also need the 
following packages:

<ul>
<li> <a href="http://home.wlu.edu/~lambertk/breezypythongui/index.html">
BreezyPythonGUI</a> on the laptop.
<br><br>
<li> <a href="http://pyserial.sourceforge.net">Pyserial</a> on the onboard computer.
<br><br>
<li> <a href="http://www.pygame.org/news.html">Pygame </a> on the laptop:
not strictly necessary, but enables joystick control.
</ul>

<h3>Getting Started</h3>

If you're using a Raspberry Pi as your onboard computer, you'll probably use
one of the USB ports for the wifi dongle and the other for connecting to the
XV-11's mini-USB port.  In that case, connecting the Pi to a USB keyboard and mouse 
to do the following steps is going to be impossible.  So for the following 
steps I recommend talking to the Pi over a wired 
network, using the Ethernet jack.  Once you've got everything connected, 
do the following:

<ol>

<li> Look at the <tt><b>HOST</b></tt> and  <tt><b>PORT</b></tt> variables
in <tt><b>neatopylot_header.py</b></tt> to make sure they won't interfere
with anything else you may be running on your network (unlikely), and modify
them if they do. 

<br><br>

<li> Copy the source code from your laptop to your onboard computer.

<br><br>


<li> Set up an ad-hoc network on the onboard computer.
For the Raspberry Pi I found several web pages 
describing how to do this by modifying configuration files in <tt><b>/etc</b></tt>, 
but I couldn't get any of them to work.  So I wrote a little Python script
<tt><b>neatopylot_wifistart.py</b></tt> and included it in the repository.
Of course, you will need to run this script using <tt><b>sudo</b></tt>.
If you <tt><b>sudo</b></tt> the script from <tt><b>/etc/rc.local</b></tt>, you can get
it to run automatically every time you boot your Pi:
<pre>
python /home/pi/NeatoPylot/neatopylot_wifistart.py
</pre>
You can then follow the directions 
<a href="http://wiki.gumstix.org/index.php?title=Creating_an_Ad-hoc_Wireless_Network#Running_DHCP_Server_on_Ad-hoc_Network">
here</a>. 
to get your Pi to serve up a dhcp
network. (These directions are for a Gumstix computer, but they worked for my
Pi too.)
<br><br>
If the onboard computer is a Mac, I would follow the procedure
described 
<a href="http://www.dummies.com/how-to/content/how-to-set-up-an-ad-hoc-wireless-network.html">
here</a>.
<br><br>
<li> From your laptop, join the ad-hoc network that you just created in 
the previous step.  If you use my script to create the network, it will be
called <b>Neato-Raspberry-Pi</b>.
<br><br>
<li> On your onboard computer, make sure that the value of the <tt><b>DEVICE</b></tt>
variable in <tt><b>neatopylot_server.py</b></tt> matches the name
of the device mapped to the XV-11's USB connection in <tt><b>/dev</b></tt>.
On my Raspberry Pi, this was <tt><b>/dev/ttyACM0</b></tt>.
<br><br>
<li> On your onboard computer, run the <tt><b>neatopylot_server.py</b></tt>
script.  It will wait for a client to connect.
<br><br>
<li> On your laptop computer, run the <tt><b>neatopylot_client.py</b></tt>
script.  It will pop up a window showing the XV-11's LIDAR.  You can then 
use your gaming console or the arrow keys to drive the XV-11 around.  If you
use the arrow keys, make sure you've selected the popup window, so it will
get the arrow-key events.
<br><br>
<li> In <tt><b>neatopylot_agent.py</b></tt>
modify the <tt><b>getAxes()</b></tt> method and (if needed) 
the <tt><b>__init__()</b></tt> method, to do something more interesting
than just turning around to the right.
</ol>

I set up the client so that it drives on Axes 2 and 3 (the lower-right 
joystick) and the autopilot is activated by Button 9 (the start button).
If you want to modify these settings, edit the <tt><b>FIRST_AXIS</b></tt>
and <tt><b>AUTOPILOT_BUTTON</b></tt> variables in 
<tt><b>neatopylot_client.py</b></tt>.  Occasionally the server will halt without
shutting down the LIDAR motor, leaving the XV-11 in test mode &ndash; bad news,
because you can't power it down, use it to vacuum, etc.
If this happens,
you can run the <tt><b>neatopylot_shutdown.py</b></tt> script on the
server to stop the LIDAR
motor and take the XV-11 out of test mode.

<h3>Known Issues</h3>
<ul>
<li> I have had problems using Pygame on the Mac.  If this happens, change
the pygame import at the top of <tt><b>neatopylot_server.py</b></tt> 
as follows:
<pre>
  #import pygame
  pygame = None
</pre>

Then use the arrow keys to drive the XV-11, and the spacebar to toggle the
autopilot.
<br><br>
<li> If you opt not to use a game controller and use the arrow
keys to steer (spacebar to toggle autopilot),  the response is a bit sluggish.
This is because I could not get the key-release interrupt to work correctly
in the Tkinter package that underlies BreezyPythonGUI.
Again, if you get this working yourself, please 
<a href="mailto:simon.d.levy@gmail.com">let me know</a>!

<br><br>
<li> Pygame may 
<a href="http://archives.seul.org/pygame/users/Aug-2009/msg00110.html">
report the joystick value</a> without your asking to see it.

<br><br>
<li> There is a lot more sensor data that one could retrieve from the XV-11.
The LIDAR scan, retrieved via the <b>GetLDSScan</b> command, 
is the only data I found useful, but if you would like to
use other commands <b>Get*</b> from the 
<a href="http://www.neatorobotics.com/programmers-manual/table-of-robot-application-commands/">
list</a>, let me know &ndash; and feel free of course to modify the code yourself!

</ul>

<h3>Alternatives</h3>

If you're already using the
<a href="http://www.willowgarage.com/pages/software/ros-platform">ROS</a>
platform, you might also look into the 
<a href="http://www.ros.org/news/2010/12/neato-xv-11-driver-for-ros-albany-ros-pkg.html">
XV-11 Driver</a> there.

<h3>Copyright, Licensing, and Questions</h3>

Copyright and licensing information can be found in the header of each source file. 
Please <a href="mailto:simon.d.levy@gmail.com">contact</a> me with questions or 
suggestions.  

</body>

