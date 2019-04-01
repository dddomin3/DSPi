#!/bin/bash
sudo killall gvfsd
sudo killall dbus-daemon
sudo killall dbus-launch
cd /home/pi/DSPi/configs/
aj-snapshot -d aj-snapshot.xml &
cd /home/pi/DSPi/py/
python midi.py &
exit 0
