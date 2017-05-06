#!/bin/bash
sudo killall gvfsd
sudo killall dbus-daemon
sudo killall dbus-launch
cd /home/pi/DSPi
aj-snapshot -d aj-snapshot.xml &
mididings "Filter(CTRL)" &
pd -alsamidi -midiindev 1 -nomidiout -nrt -nogui -noaudio midiDspSwitch.pd &
exit 0
