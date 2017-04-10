#!/bin/bash
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
sudo mount -o remount,size=128M /dev/shm
sudo killall gvfsd
sudo killall dbus-daemon
sudo killall dbus-launch
cd /home/pi
jackd -P70 -p16 -t2000 -d alsa -dhw:CODEC -p 128 -n 3 -r 48000 -S -s -Xseq &
sleep 10
# nohup zynaddsubfx -r48000 -b128 -o512 -a -U &
# amsynth -r48000 -r128 -c9 -p4 -x &
# jack-dssi-host /usr/lib/dssi/amsynth_dssi.so -n &
sleep 15
guitarix --nogui &
sleep 15
aj-snapshot -d /home/pi/auto.snap &
pd -alsamidi -rt -nogui -noaudio funkSwitch.pd &
exit 0
