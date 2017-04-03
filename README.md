# Introduction
This repository is me self-documenting my journeys in using a Raspberry Pi as an integral part of my music setup. I usually make alternative/electronic/indie music without a computer, but I don't want to dismiss the benefits of having a computer in my setup. I want to be able to use:
- VST, VSTis
- USB MIDI Controllers
- Guitar Amp Simulators
- Audio Recording
- Synthesizer Programs
- DSP
- Pure Data Patches/Super-Collider

... without stifling my creativity through excessive use of mouse and keyboard.
This necessitates a low-latency environment with tons of connectivity. My plan is to cycle through all of the aforementioned functions through a standardized MIDI CC/Program Change Schema, effectively creating a MIDI controlled module that is a jack-of-all-trades in my music setup.
# Kernel Building (Cross Compiling)
If you want to process low-latency DSP, you're going to need a preemptable kernel... Sadly, step one is to compile a kernel... Good luck!

## Cleaning your kernel dir (Or grabbing a new one it if you're starting from scratch)
```code:bash
cd ~
git clone https://github.com/raspberrypi/tools.git
git clone https://github.com/raspberrypi/linux.git
cd linux/
make clean
git clean -f
git reset --hard
```
Make sure, by the way, to check out a commit/release where the kernel version matches (look below for patches, etc)
Check this file (and similar commits) for the kernel version. This usually happens after a release and whatnot.
https://github.com/raspberrypi/linux/commit/702c0ce9a7c7ad1b22883aa82d8c29eaa6e65aab

## Grab Kernel Patch
```
cd ~
wget https://www.kernel.org/pub/linux/kernel/projects/rt/4.4/[*.patch.gz] # Replace with patch matching the kernel you grabbed from kernel repo
zcat [patch.file.patch.gz] | patch -p1
```

## Grab configs from raspi
```
scp pi@ip.address.of.pi :/proc/config.gz
zcat config.gz > .config
# or grab it from the sd card

make menuconfig #Need a large terminal

# Kernel Features > Preemption Kernel (Low Latency Desktop)
# CPU Power Management > Frequency Scaling > Performance
```

## One last step before building the kernel--Mis en place
Plug in your Raspian SD card (should definitely work for other distros). Note how it mounts. You really just need to find the `/boot` and `/lib` directories.
```
sudo apt-get install git build-essential make lzop ncurses-dev gcc-arm-linux-gnuebi fakeroot kernel-package dev-essential
# Not sure if we need all of them
```

Make these files. `chmod 755 installkernel.sh` so you can execute it. Look at the paths and replace them as needed...:
### kernel.source
```
export KERNEL_SRC=/home/cheekymusic/linux/
export ARCH=arm
export CROSS_COMPILE=${CCPREFIX}
export MODULES_TEMP=/home/cheekymusic/modules/
export CCPREFIX=/home/cheekymusic/tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/arm-linux-gnueabihf-
export KERNEL=kernel7
export INSTALL_MOD_PATH=/home/cheekymusic/rtkernel/
```
Aside: MODULES_TEMP might not be used...
### installkernel.sh
```
sudo rm -r /media/cheekymusic/boot/overlays/
sudo rm -r /media/cheekymusic/7f593562-9f68-4bb9-a7c9-2b70ad620873/lib/firmware/
cd ~/rtkernel/boot
sudo cp -rd * /media/cheekymusic/boot/
cd ../lib
sudo cp -dr * /media/cheekymusic/7f593562-9f68-4bb9-a7c9-2b70ad620873/lib/
```
/media/cheekymusic is where the sd card was mounted

Aside: Do you really need to delete the firmware here?

## Building kernel
```
source kernel.source
cd ~/linux
make zImage modules dtbs -j4 # -j#, where # is CPU cores * 1.5 (of your compiling machine)
make modules_install -j4
```

grab this firmware if you want wifi (Pi 3 Model B):
https://github.com/RPi-Distro/firmware-nonfree/tree/master/brcm80211
and copy it into `$INSTALL_MOD_PATHlib/firmware`

Then run `./installkernel` with your sd card mounted.

Try append these to `/boot/cmdline.txt` if you run into issues:
```
dwc_otg.speed=1 sdhci_bcm2708.enable_llm=0
```
`sdhci_bcm2708.enable_llm=0` disables low latency mode for sd card
`dwc_otg.speed=1` Forces the USB controller to use 1.1 mode (since the USB 2.0 controller on the pi may cause issues with some audio interfaces)

## Making your new pi experience better:
`touch /media/cheekymusic/boot/ssh` enables ssh

Add the follow to auto-connect to your networks
```
network={
        ssid="SSID_AMAZING_2.4"
        psk="fourwordsallcapswithspaces"
}

network={
        ssid="CheekyMusicWifi"
        psk="PASSKEY"
        key_mgmt=WPA-PSK
}
```

## Installing music stuff and configuring it

Install this stuff!
```
sudo apt-get install jackd2 guitarix amsynth aj-snapshot jack-dssi-host dssi-jack-host # forgot the package name...
```
Jack2 (jackd2) is audio server.
guitarix is amp sim
amsynth is synth
aj-snapshot is the audio/midi auto connection daemon
jack-dssi-host is a dssi host, which can do things like host synths, host VSTs, etc.

And then add the following lines to /etc/dbus-1/system.conf:

```
 <policy user="pi">
       <allow own="org.freedesktop.ReserveDevice1.Audio1"/>
 </policy>
```

This allows the dbus compiled jack server to run without a GUI running.

Run `raspi-config` and make Boot Options so that raspi turns on with Console (login might be necessary as well).

## Getting Music Stuff to run on boot
1. Move the jackboot script into `/etc/init.d/jackboot`
2. Make it executable: `sudo chmod 755 /etc/init.d/jackboot`
3. Copy `jackstart.sh` into `~/jackstart.sh`
  1. Edit Line 7 of `jackstart.sh` ( `-dhw:CODEC` ) to match your soundcard (run `qjackctl` to figure out the name of your sound card)
  2. Honestly, you might have to experiment A LOT with this line. It has the biggest effect on your audio latency, which is the core of this entire project.
    - For a fact, if you're not using the UCA-222/202, you probably don't want `-S` (Force 16-bit, since UCA-222 is 16-bit)
4. Make it executable: `sudo chmod 755 ~/jackstart.sh`
NOTE: This is because the audio stuff needs to run as the pi user, and I'm too stupid to figure ot a better way to do that...
5. Register it in update-rc.d `sudo update-rc.d NameOfYourScript defaults`
6. Run `jackstart.sh` manually, then run `qjackctl &`
7. Open up the connections menu, and make all the connections you desire. Plug in any midi controllers, and route connections from them, to MIDI-Through (in alsa), and from system:1 to guitarix (on MIDI)
8. Run `aj-snapshot ~/auto.snap` to generate the aj-snapshot file used in `jackstart.sh`.

> If you ever want to remove the script from start-up, run the following command:
> `sudo update-rc.d -f  NameOfYourScript remove`

Paraphrased from resource \#4, except for the jackstart part (for obvious reasons).



## Resources
1. If I would choose one source, it'd be this one
http://wiki.linuxaudio.org/wiki/raspberrypi

2. Realtime kernel patching. Most of this is based on this article.
http://www.frank-durr.de/?p=203

3. Some general things you have to understand about kernel patching for raspi
https://www.raspberrypi.org/documentation/linux/kernel/patching.md

4. Running stuff on boot for RasPi
http://www.stuffaboutcode.com/2012/06/raspberry-pi-run-program-at-start-up.html
