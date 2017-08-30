#!/bin/bash
sudo killall gvfsd
sudo killall dbus-daemon
sudo killall dbus-launch
cd /home/pi/DSPi/configs/
aj-snapshot -d aj-snapshot.xml &
cd /home/pi/DSPi/pd/
pd -alsamidi -midiindev 1 -midioutdev 1 -nrt -nogui -noaudio midiDspSwitch.pd &
exit 0
