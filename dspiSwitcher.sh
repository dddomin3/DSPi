#!/bin/bash
echo $dspi
[ $dspi == 'guitarix' ] && (
  killall amsynth
  killall jack-rack
  killall guitarix
  sleep 10
  guitarix --nogui >> /home/pi/DSPi/jackboot.log &
  echo "nernerner"
  exit 0;
)
[ $dspi == 'amsynth' ] && (
  killall guitarix
  killall jack-rack
  killall amsynth
  sleep 10
  amsynth -x -r48000 -c9 -p4 >> /home/pi/DSPi/jackboot.log &
  echo "wubwubwub"
  exit 0;
)
[ $dspi == 'sidechain' ] && (
  killall guitarix
  killall amsynth
  killall jack-rack
  sleep 10
  jack-rack --help >> /home/pi/DSPi/jackboot.log &
  echo "unAunAunA"
  exit 0;
)
exit 1;
