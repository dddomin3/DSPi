#!/bin/bash
sudo rm -r /media/cheekymusic/boot/overlays/
sudo rm -r /media/cheekymusic/rootfs/lib/firmware/
cd ~/rtkernel/boot &&
sudo cp -rd * /media/cheekymusic/boot/ &&
cd ~/rtkernel/lib &&
sudo cp -dr * /media/cheekymusic/rootfs/lib/
