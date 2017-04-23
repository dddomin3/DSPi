#!/bin/bash
sudo rm -r /media/cheekymusic/boot/overlays/
sudo rm -r /media/cheekymusic/f2100b2f-ed84-4647-b5ae-089280112716/lib/firmware/
cd ~/rtkernel/boot &&
sudo cp -rd * /media/cheekymusic/boot/ &&
cd ~/rtkernel/lib &&
sudo cp -dr * /media/cheekymusic/f2100b2f-ed84-4647-b5ae-089280112716/lib/
