#!/bin/bash
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
# sudo mount -o remount,size=128M /dev/shm #dont think i need to do this due to gpu mem being pretty low.
sudo killall gvfsd
sudo killall dbus-daemon
sudo killall dbus-launch
cd /home/pi/DSPi
jackd -P70 -p16 -t2000 -d alsa -dhw:CODEC -p 128 -n 3 -r 48000 -S -s -Xseq &
sleep 15
guitarix --nogui &
sleep 15
aj-snapshot -d aj-snapshot.xml &
pd -alsamidi -nrt -nogui -noaudio -nomidiout midiDspSwitch.pd &
exit 0
