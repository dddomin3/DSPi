# DSPi: An Audio Raspberry Pi Audio module/journey

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

## **I:** Installing Raspian

### **I1:** Download Raspian Lite

<https://www.raspberrypi.org/downloads/raspbian/>
Lite, since you want a minimal os with no gui, really.

### **I2:** Par`dd`y time: Using dd to back up and install Raspian

I use dd, and a sd card reader to manage my raspi sd card. /dev/mmcblk0 is where my sdcard mounts. Correct the below to correspond! Unmount your sdcard, but leave it plugged in. Makes this happen easier.

`sudo dd bs=4M if=/dev/mmcblk0 of=from-sd-card.img status=progress`

Backs up your SD card to a file called `from-sd-card.img`

`sudo dd bs=4M if=2017-04-10-raspbian-jessie-lite.img of=/dev/mmcblk0 status=progress && sync`

Installs Raspian to your sd card.

Feel free to use NOOBS or whatever way you install raspbian. This is just what i do! :)

### **I3:** Making your new pi experience better

`touch /media/cheekymusic/boot/ssh` enables ssh

`sudo nano /media/cheekymusic/f2100b2f-ed84-4647-b5ae-089280112716/etc/wpa_supplicant/wpa_supplicant.conf` the stuff on the bottom to auto-connect to your networks.

```conf
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

## **II:** Kernel Building (Cross Compiling)

If you want to process low-latency DSPi, you're going to need a pre-emptable kernel... Sadly, step one is to compile a kernel... Good luck! These instructions are for cross compilation on a linux system (Ubuntu Studio) but should definitely work for other debian-based OS's. I also happen to have an SD card port, which definitely eases Raspberry Pi setup.

### **II1:** Cleaning your kernel dir (Or grabbing a new one it if you're starting from scratch)

```bash
cd ~
git clone https://github.com/raspberrypi/tools.git
git clone https://github.com/raspberrypi/linux.git
cd linux/
make clean
git clean -f
git reset --hard
git checkout raspberrypi-kernel_1.20170405-1
```

Make sure, by the way, to check out a commit/release where the kernel version matches (look below for patches, etc)
Check this file (and similar commits) for the kernel version. This usually happens after a release and whatnot.
<https://github.com/raspberrypi/linux/tree/raspberrypi-kernel_1.20170405-1>

### **II2:** Grab Kernel Patch

```bash
cd ~/linux
wget https://www.kernel.org/pub/linux/kernel/projects/rt/4.4/[*.patch.gz] # Replace with patch matching the kernel you grabbed from kernel repo
zcat [patch.file.patch.gz] | patch -p1
```

Make sure the kernel patch matches the kernel version in the previous step EXACTLY! I've made this mistake, and it prevents the pi from booting. YMMV.
I used `patch-4.4.50-rt63.patch.gz` as of this commit.

### **II3:** Grab configs from raspi

```bash
scp pi@ip.address.of.pi:/proc/config.gz
zcat config.gz > .config
# or grab it from the sd card

rm .oldconfig # do i need to do this?
make olddefconfig # this sets defaults for a lot of stuff
make menuconfig # Need a large terminal

# Kernel Features > Preemption Kernel (Low Latency Desktop)
# CPU Power Management > Frequency Scaling > Performance
```

`make menuconfig` may fail if your terminal isn't maximized.

OR

you can just `mv .basicRtKernelConfig ~/linux/.config` and use the preconfigured config file in the repo... this was generated with the directions above with the aforementioned kernel/patch versions

### **II4:** One last step before building the kernel--Mis en place

Plug in your Raspian SD card (should definitely work for other distros). Note how it mounts. You really just need to find the `/boot` and `/lib` directories.

```bash
sudo apt-get install git build-essential make lzop ncurses-dev gcc-arm-linux-gnuebi fakeroot kernel-package dev-essential
# Not sure if we need all of them
```

`sudo yum install #...` may work for non-debian systems. The only things that may differ are `build-essential` and `dev-essential`.

Edit installkernal.sh and kernel.source to match the directories for your system.
Note: `/media/cheekymusic` is where the sd card was mounted. `/home/cheekymusic === ~`
`chmod 755 installkernel.sh` so you can execute it.

TODO: Figure out if we really need to delete the firmware here.

### **II5:** Building kernel

```bash
source kernel.source
cd ~/linux
make zImage modules dtbs -j4 # -j#, where # is CPU cores * 1.5 (of your compiling machine)
make modules_install -j4
mkdir ~/$INSTALL_MOD_PATH/boot/
./scripts/mkknlimg ./arch/arm/boot/zImage $INSTALL_MOD_PATH/boot/$KERNEL.img
```

grab this firmware if you want wifi (Pi 3 Model B):
<https://github.com/RPi-Distro/firmware-nonfree/tree/master/brcm80211>
and copy it into `$INSTALL_MOD_PATHlib/firmware`

Then run `./installkernel.sh` with your sd card mounted.

Try append these to `/boot/cmdline.txt` if you run into issues:

```conf
dwc_otg.speed=1 sdhci_bcm2708.enable_llm=0 smsc95xx.turbo_mode=N
```

`sdhci_bcm2708.enable_llm=0` disables low latency mode for sd card
`dwc_otg.speed=1` Forces the USB controller to use 1.1 mode (since the USB 2.0 controller on the pi may cause issues with some audio interfaces)
`smsc95xx.turbo_mode=N` Disable the turbo mode for the ethernet controller

Then add the following lines to `/etc/dbus-1/system.conf`: (INSIDE \<busconfig\> tags!)

```xml
 <policy user="pi">
       <allow own="org.freedesktop.ReserveDevice1.Audio1"/>
 </policy>
```

This allows the dbus-compiled jack server to run without a GUI running.

### **II6:** Installing music stuff and configuring it

Install this stuff!
`sudo apt-get install qjackctl jackd2 guitarix aj-snapshot puredata git pd-ggee`

- Jackd2 (jackd2) is audio server
- qjackctl is a QT-based GUI to manage jackd2 server. There are others if you prefer.
- guitarix is a guitar amp simulator
- aj-snapshot is the automatic audio/midi auto connection daemon. May be able to replace this with `--jack-autoconnect` (and similar CLI flags) on guitarix and amsynth.
- git to clone this repo
- puredata and pd-ggee for MIDI translation and script launching on MIDI message

Allow jack server to use realtime priority (it'll ask when you're installing. Say yes.)

Run `sudo raspi-config`:

- Alter Boot Options so that raspi turns on with Console with auto-login (3 Boot Options -> B1 -> B2).
- Set the GPU Memory to 16 under "7 Advanced Options -> A3"

### **II7:** amSynth building from source

Build amSynth on your raspi using the instructions below. It's braindead simple to do.
<https://github.com/amsynth/amsynth/wiki/BuildingFromSource>
Make sure you checkout a release. `git checkout release-1.7.1` is the most recent at the time of this commit (2017/04/29)

### **II8:** Getting Music Stuff to run on boot

1. `git clone https://github.com/dddomin3/DSPi.git ~/DSPi` <br/>
  Cloning this repo into ~/DSPi allows me to `git pull` to get any updates, since jackboot points at `~/DSPi/bash/jackstart.sh`. Hopefully you can do the same!
1. Move the jackboot script into init.d: `sudo cp ~/DSPi/bash/jackboot /etc/init.d/jackboot` and make sure it's executable: `sudo chmod 755 /etc/init.d/jackboot`
1. Edit `~/DSPi/bash/jackstart.sh` <br/>
  Edit Line 7 of `jackstart.sh` ( `-dhw:CODEC` ) to match your soundcard (run `qjackctl` to figure out the name of your sound card) <br/>
  Honestly, you might have to experiment A LOT with this line. It has the biggest effect on your audio latency, which is the core of this entire project. You can use qjackctl to help fine-tune settings without busting a blood vessel in your forehead. <br/>
  For a fact, if you're not using the UCA-222/202, you probably don't want `-S` (Force 16-bit, since UCA-222 is 16-bit) <br/>
1. Make sure it's executable: `sudo chmod 755 ~/DSPi/bash/jackstart.sh`
NOTE: This is because the audio stuff needs to run as the pi user, and I can't figure to a better way to do that...
1. Register it in update-rc.d `sudo update-rc.d jackboot defaults`
1. Run `jackstart.sh` manually, then run `qjackctl &`
1. Open up the connections menu, and make all the connections you desire. Plug in any midi controllers, and route connections from them, to MIDI-Through (in alsa tab), and from system:1 to guitarix (on MIDI tab), `amsynth` and `jack-rack`. Using the `seq` drivers midi-through allows for easy modification of your midi-autoconnection schema. Most of the time, I just add another connection by hand (once I know the name of the controller in alsa) in the `aj-snapshot.xml`.
1. Run `aj-snapshot ~/DSPi/configs/aj-snapshot.xml` to generate the aj-snapshot file used in `jackstart.sh`.
1. `touch jackboot.log` if you want to have user access to the logs. Otherwise, `root` creates the logs, and you'll need to sudo to access them.

> If you ever want to remove the script from start-up, run the following command:
> `sudo update-rc.d -f  jackboot remove`

`/etc/init.d` instructions paraphrased from resource \#4.
`jackstart.sh` based on resource \#5.

### **II9:** Pure Data

jackstart.sh starts a puredata script which assists in switching which dsp is currently running on the pi. The PD script responds to values on MIDI:`CH16 PC`. Depending on the value, a specific program (or "DSPi") will be ran, and others will be killed:

- 0: Runs guitarix (Turns off wireless chip)
- 64: Runs amsynth (Turns off wireless chip)
- 127: Turns on wireless chip

### **II10:** Run amSynth using native nogui option

Note: As of this commit, amsynth on the raspian repos do not support this option. You must compile amSynth on the raspi to get these capabilities.
<https://github.com/amsynth/amsynth/wiki/BuildingFromSource>
REALLY easy to do, actually. VERY well documented.

`amsynth -x -mjack -aalsa -r48000 -c9 -p4`

- -x is no gui
- -mjack forces jack midi
- -alsa forces alsa audio
- -c9 makes amSynth respond to midi channel 9
- -p4 is max of 4 notes of polyphony
- -r48000 runs amSynth at 48000 sample rate

Also included amsynthSettings, contents can go right into `~/` for midi mapping (Line Number + 1 = Midi CC).

## **A:** Jenkins can do up to II5 for you :)

1. Set up jenkins to use `/bin/bash` for shell scripts. (Check in settings...)
1. Get git plugin, and pipeline plugin.
1. Make new project based on this repo, pointing at Jenkinsfile. <https://jenkins.io/doc/book/pipeline/getting-started/>
1. Do a `sudo visudo` and add `jenkins ALL=(ALL:ALL) NOPASSWD:ALL` to your sudoers. TODO: Should probably not give ALL these permission to jenkins...

## **B:** Ansible can do the rest for you!

Install ansible on your system.

`sudo nano /etc/ansible/hosts` on your system, and add the following:

```conf
[dspi]
192.168.x.y #ip address or hostname of your pi
```

Go onto your pi, and add your jenkins/ansible machines ssh key to your pi

<https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md>
Might have to do:

```bash
eval `ssh-agent -s`
ssh-add
sudo reboot
```

But I'm not sure

Now Jenkins (via ansible) should be able to enforce all configs on your pi for you :)

Test connection by running the following command, and seeing a success

```bash
cheekymusic@cheekymusic-Q550LF:~$ ansible all -m ping -u pi --private-key ~/.ssh/id_rsa.pub --become
192.168.1.18 | SUCCESS => {
    "changed": false, 
    "ping": "pong"
}
```

## **C:** MIDI Reference

- *Channel 1*
  - **MFTT** *CC 0-63* MIDI Out and Updates
- *Channel 2*
  - **MFTT** *CC 0-127* Switch Out and Indicator Light In
- *Channel 3*
  - **MFTT** *CC 0-63* Switch Animations & Brightness
- *Channel 4*
  - **MFTT** *CC 0-3, 8-31* Banks and Side Buttons
- *Channel 5*
  - **MFTT** *CC 0-63* Shift Out and Updates
  - **Guitarix** *CC 64-103* Guitar Amp and EFX Params
- *Channel 6*
  - **MFTT** *CC 0-127* Ring Animations and Brightness
- *Channel 7*
  - **Octa** *Notes, CC 46, 47, 49* Track 7: Mutes, Volumes, and Cues
- *Channel 8*
  - **MFTT** *CC ??* Sequencer
  - **Octa** *Notes, CC 46, 47, 49* Track 8: Mutes, Volumes, and Cues
- *Channel 9*
  - **amSynth** *Notes, CC 0-80, PC* Synth Params
- *Channel 10*
  - **Octa** Auto Channel
- *Channel 11*
  - **Octa** *Notes, CC 46, 47, 49, 112-119* Track 1: Mutes, Volumes, and Cues
- *Channel 12*
  - **Octa** *Notes, CC 46, 47, 49* Track 2: Mutes, Volumes, and Cues
- *Channel 13*
  - **Octa** *Notes, CC 46, 47, 49* Track 3: Mutes, Volumes, and Cues
- *Channel 14*
  - **Octa** *Notes, CC 46, 47, 49* Track 4: Mutes, Volumes, and Cues
- *Channel 15*
  - **Octa** *Notes, CC 46, 47, 49* Track 5: Mutes, Volumes, and Cues
- *Channel 16*
  - **Meta** *PC* DSPi Switch
  - **Octa** *Notes, CC 46, 47, 49* Track 6: Mutes, Volumes, and Cues

## **i** Resources

1. If I would choose one source, it'd be this one: <http://wiki.linuxaudio.org/wiki/raspberrypi>
1. Realtime kernel patching. Most of this is based on this article: <http://www.frank-durr.de/?p=203>
1. Some general things you have to understand about kernel patching for raspi: <https://www.raspberrypi.org/documentation/linux/kernel/patching.md>
1. Running stuff on boot for RasPi: <http://www.stuffaboutcode.com/2012/06/raspberry-pi-run-program-at-start-up.html>
1. Script for running jack gui-less, and disabling other unneccesary services: <https://github.com/autostatic/scripts/blob/rpi/jackstart>
