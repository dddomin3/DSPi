#!/bin/bash
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
# sudo mount -o remount,size=128M /dev/shm #dont think i need to do this due to gpu mem being pretty low.
sudo killall gvfsd
sudo killall dbus-daemon
sudo killall dbus-launch
cd /home/pi/DSPi
jackd -P80 -p16 -S -t8000 -dalsa -dhw:CODEC -p128 -n4 -r48000 -s -S -Xseq &
sleep 15
dspi=amsynth dspiSwitcher.sh
sleep 15
aj-snapshot -d aj-snapshot.xml &
pd -alsamidi -midiindev 1 -nomidiout -nrt -nogui -noaudio midiDspSwitch.pd &
exit 0
