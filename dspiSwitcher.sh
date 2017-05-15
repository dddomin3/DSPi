#!/bin/bash
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
killall -9 amsynth
killall -9 guitarix
killall -9 jackd
[ $dspi == 'guitarix' ] && (
  jackd -P80 -p16 -S -t2000 -dalsa -dhw:CODEC,0 -p64 -n6 -r48000 -s -S -Xseq -D >> /home/pi/DSPi/jackboot.log &
  # chrt -a -r -p 80 $! &
  sleep 15
  guitarix --nogui >> /home/pi/DSPi/jackboot.log &
  chrt -a -r -p 75 $! &
  echo "nernerner"
  sudo ifdown wlan0 &
  exit 0;
)
[ $dspi == 'amsynth' ] && (
  jackd -s -S -P80 -p16 -t2000 -dalsa -dhw:CODEC,0 -r48000 -p64 -n6 -s -S -P -Xnone >> /home/pi/DSPi/jackboot.log &
  # chrt -a -r -p 80 $! &
  sleep 15
  amsynth -x -malsa -ajack -c9 -p4 -r48000 >> /home/pi/DSPi/jackboot.log &
  chrt -a -r -p 75 $! &
  echo "wubwubwub"
  sudo ifdown wlan0 &
  exit 0;
)
[ $dspi == 'debug' ] && (
  sudo ifup wlan0 &
  echo "Debugging" >> /home/pi/DSPi/jackboot.log
  exit 0;
)
exit 1;
