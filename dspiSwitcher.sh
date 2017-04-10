#!/bin/bash
echo $dspi
[ $dspi == 'guitarix' ] && (
  killall jack-dssi-host
  killall jack-rack
  killall guitarix
  sleep 10
  guitarix --nogui > /home/pi/DSPi/jackboot.log &
  echo "nernerner"
  exit 0;
)
[ $dspi == 'amsynth' ] && (
  killall guitarix
  killall jack-rack
  killall jack-dssi-host
  sleep 10
  jack-dssi-host /usr/lib/dssi/amsynth_dssi.so -n > /home/pi/DSPi/jackboot.log &
  echo "wubwubwub"
  exit 0;
)
[ $dspi == 'sidechain' ] && (
  killall guitarix
  killall jack-dssi-host
  killall jack-rack
  sleep 10
  jack-rack --help > /home/pi/DSPi/jackboot.log &
  echo "unAunAunA"
  exit 0;
)
exit 1;
