#!/bin/bash
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
killall amsynth
killall jack-rack
killall guitarix
[ $dspi == 'guitarix' ] && (
  killall jackd &&
  jackd -P80 -p16 -S -t8000 -dalsa -dhw:CODEC,0 -p64 -n6 -r48000 -s -S -Xseq -Dtrue -i >> /home/pi/DSPi/jackboot.log &
  sudo ifdown wlan0
  sleep 15
  guitarix --nogui >> /home/pi/DSPi/jackboot.log &
  chrt -p 75 $! &
  echo "nernerner"
  exit 0;
)
[ $dspi == 'amsynth' ] && (
  killall jackd &&
  jackd -P80 -p16 -S -t8000 -dalsa -dhw:CODEC,0 -p64 -n6 -r48000 -s -S -Xseq -i0 -Dfalse >> /home/pi/DSPi/jackboot.log &
  sudo ifdown wlan0
  sleep 15
  amsynth -x -malsa -ajack -c9 -p4 -r48000 >> /home/pi/DSPi/jackboot.log &
  chrt -p 75 $! &
  echo "wubwubwub"
  exit 0;
)
[ $dspi == 'debug' ] && (
  sudo ifup wlan0
  echo "Debugging" >> /home/pi/DSPi/jackboot.log
  exit 0;
)
exit 1;
