#!/bin/bash
[ $dspi == 'guitarix' ] && (
  killall amsynth
  killall jack-rack
  killall guitarix
  sudo ifdown wlan0 &
  sleep 10
  guitarix --nogui >> /home/pi/DSPi/jackboot.log &
  chrt -p 75 $! &
  echo "nernerner"
  exit 0;
)
[ $dspi == 'amsynth' ] && (
  killall guitarix
  killall jack-rack
  killall amsynth
  sudo ifdown wlan0 &
  sleep 10
  amsynth -x -malsa -ajack -c9 -p4 -r48000 >> /home/pi/DSPi/jackboot.log &
  chrt -p 75 $! &
  echo "wubwubwub"
  exit 0;
)
[ $dspi == 'sidechain' ] && (
  killall guitarix
  killall amsynth
  killall jack-rack
  sudo ifup wlan0 &
  sleep 10
  jack-rack --help >> /home/pi/DSPi/jackboot.log &
  chrt -p 75 $! &
  echo "unAunAunA"
  exit 0;
)
exit 1;
