#!/usr/bin/env python
from mididings import *
from mididings.event import *

config(
  client_name='mididings',
  in_ports=['MFTIn', 'amSynthIn', 'octatrackIn', 'guitarixIn', 'quNexusIn'],
  out_ports=['MFTOut', 'amSynthOut', 'octatrackOut', 'guitarixOut', 'opzOut'],
)

# These functions help map MFT MIDI messages over to other usages.
# I usually use a CC offset to bring other programs CC's in line with
# MFT CCs, keeping it sequential, but with an offset
def amSynthOffset(e):
  e.ctrl = e.ctrl + 63
  return e
def amSynthDeOffset(e):
  e.ctrl = e.ctrl - 63
  return e

def guitarixOffset(e):
  e.ctrl = e.ctrl + 16
  return e
def guitarixDeOffset(e):
  e.ctrl = e.ctrl - 16
  return e
def guitarixShiftOffset(e):
  e.ctrl = e.ctrl + 42
  return e
def guitarixShiftDeOffset(e):
  e.ctrl = e.ctrl - 42
  return e

class MuteFix:
  ccToOctaTrack = {
    16:1, 17:5,
    20:2, 21:6,
    24:3, 25:7,
    28:4, 29:8,
  }
  octaTrackToCc = [16, 20, 24, 28, 17, 21, 25, 29]
  mftCcToOctaMidiTrack = {
    18:1, 19:5,
    22:2, 23:6,
    26:3, 27:7,
    30:4, 31:8,
  }
  octaMidiTrackToMftCc = [18, 22, 26, 30, 19, 23, 27, 31]
  octaCcToOctaMidiTrack = {
    112:1, 116:5,
    113:2, 117:6,
    114:3, 118:7,
    115:4, 119:8,
  }
  octaMidiTrackToOctaCc = [112, 113, 114, 115, 116, 117, 118, 119]
  offColor = 40
  onColor = 85

  volumeMutes = [False, False, False, False, False, False, False, False]
  midiMutes = [False, False, False, False, False, False, False, False]
  mftPort = 'MFTOut'
  octaPort = 'octatrackOut'

  @classmethod
  def octaVolumeMuteFix(klass, e):
    octaTrack = klass.ccToOctaTrack[e.ctrl]
    klass.volumeMutes[octaTrack-1] = not klass.volumeMutes[octaTrack-1]

    mftOut = CtrlEvent(
      klass.mftPort,
      2,
      klass.octaTrackToCc[octaTrack-1],
      klass.onColor if klass.volumeMutes[octaTrack-1] else klass.offColor,
    )
    octaOut = CtrlEvent(
      klass.octaPort,
      octaTrack,
      49,
      klass.volumeMutes[octaTrack-1] * 127,
    )

    print(klass.volumeMutes,klass.midiMutes)
    return [mftOut, octaOut]
  
  @classmethod
  def octaMidiMuteFix(klass, e):
    octaTrack = klass.mftCcToOctaMidiTrack[e.ctrl]
    klass.midiMutes[octaTrack-1] = not klass.midiMutes[octaTrack-1]

    mftOut = CtrlEvent(
      klass.mftPort,
      2,
      klass.octaMidiTrackToMftCc[octaTrack-1],
      klass.onColor if klass.midiMutes[octaTrack-1] else klass.offColor
    )
    octaOut = CtrlEvent(
      klass.octaPort,
      1,
      klass.octaMidiTrackToOctaCc[octaTrack-1],
      int(klass.midiMutes[octaTrack-1]) * 127
    )

    print(klass.volumeMutes,klass.midiMutes)
    return [mftOut, octaOut]
  
  @classmethod
  def mftVolumeMuteFix(klass, e):
    octaTrack = e.channel
    klass.volumeMutes[octaTrack-1] = not klass.volumeMutes[octaTrack-1]

    mftOut = CtrlEvent(
      klass.mftPort,
      2,
      klass.octaTrackToCc[octaTrack-1],
      klass.onColor if klass.volumeMutes[e.channel-1] else klass.offColor,
    )
    octaOut = CtrlEvent(
      klass.octaPort,
      octaTrack,
      49,
      klass.volumeMutes[octaTrack-1] * 127,
    )

    print(klass.volumeMutes,klass.midiMutes)
    return [mftOut, octaOut]
  
  @classmethod
  def mftMidiMuteFix(klass, e):
    octaTrack = klass.octaCcToOctaMidiTrack[e.ctrl]
    klass.midiMutes[octaTrack-1] = not klass.midiMutes[octaTrack-1]

    mftOut = CtrlEvent(
      klass.mftPort,
      2,
      klass.octaMidiTrackToMftCc[octaTrack-1],
      klass.onColor if klass.midiMutes[octaTrack-1] else klass.offColor
    )
    octaOut = CtrlEvent(
      klass.octaPort,
      1,
      klass.octaMidiTrackToOctaCc[octaTrack-1],
      int(klass.midiMutes[octaTrack-1]) * 127
    )

    print(klass.volumeMutes,klass.midiMutes)
    return [mftOut, octaOut]

fixer = MuteFix()

run(
  [
    ChannelFilter(16) >> [ # Global MIDI DSPi Program Change
      ProgramFilter(1) >> System('/home/pi/DSPi/bash/dspiSwitcher.sh amsynth'),
      ProgramFilter(64) >> System('/home/pi/DSPi/bash/dspiSwitcher.sh guitarix'),
      ProgramFilter(128) >> System('/home/pi/DSPi/bash/dspiSwitcher.sh debug'),
    ],
    PortFilter('MFTIn') >> [
      ChannelFilter(1) >> [ #MFT Outward
        CtrlFilter(range(0,16)) >> CtrlMap(0,80) >> Ctrl('amSynthOut', 9, EVENT_CTRL, EVENT_VALUE),

        CtrlFilter(16) >> Ctrl('octatrackOut', 1, 46, EVENT_VALUE), CtrlFilter(17) >> Ctrl('octatrackOut', 5, 46, EVENT_VALUE),
        CtrlFilter(20) >> Ctrl('octatrackOut', 2, 46, EVENT_VALUE), CtrlFilter(21) >> Ctrl('octatrackOut', 6, 46, EVENT_VALUE),
        CtrlFilter(24) >> Ctrl('octatrackOut', 3, 46, EVENT_VALUE), CtrlFilter(25) >> Ctrl('octatrackOut', 7, 46, EVENT_VALUE),
        CtrlFilter(28) >> Ctrl('octatrackOut', 4, 46, EVENT_VALUE), CtrlFilter(29) >> Ctrl('octatrackOut', 8, 46, EVENT_VALUE),

        CtrlFilter(18) >> Ctrl('octatrackOut', 1, 47, EVENT_VALUE), CtrlFilter(19) >> Ctrl('octatrackOut', 5, 47, EVENT_VALUE),
        CtrlFilter(22) >> Ctrl('octatrackOut', 2, 47, EVENT_VALUE), CtrlFilter(23) >> Ctrl('octatrackOut', 6, 47, EVENT_VALUE),
        CtrlFilter(26) >> Ctrl('octatrackOut', 3, 47, EVENT_VALUE), CtrlFilter(27) >> Ctrl('octatrackOut', 7, 47, EVENT_VALUE),
        CtrlFilter(30) >> Ctrl('octatrackOut', 4, 47, EVENT_VALUE), CtrlFilter(31) >> Ctrl('octatrackOut', 8, 47, EVENT_VALUE),

        CtrlFilter(range(48,64)) >> Process(guitarixOffset) >> Ctrl('guitarixOut', 11, EVENT_CTRL, EVENT_VALUE),
      ],
      ChannelFilter(2) >> [ #MFT Switches Outward
        # TODO: implement switch fix...
        CtrlFilter(16) >> Process(fixer.octaVolumeMuteFix), CtrlFilter(17) >> Process(fixer.octaVolumeMuteFix),
        CtrlFilter(20) >> Process(fixer.octaVolumeMuteFix), CtrlFilter(21) >> Process(fixer.octaVolumeMuteFix),
        CtrlFilter(24) >> Process(fixer.octaVolumeMuteFix), CtrlFilter(25) >> Process(fixer.octaVolumeMuteFix),
        CtrlFilter(28) >> Process(fixer.octaVolumeMuteFix), CtrlFilter(29) >> Process(fixer.octaVolumeMuteFix),

        CtrlFilter(18) >> Process(fixer.octaMidiMuteFix), CtrlFilter(19) >> Process(fixer.octaMidiMuteFix),
        CtrlFilter(22) >> Process(fixer.octaMidiMuteFix), CtrlFilter(23) >> Process(fixer.octaMidiMuteFix),
        CtrlFilter(26) >> Process(fixer.octaMidiMuteFix), CtrlFilter(27) >> Process(fixer.octaMidiMuteFix),
        CtrlFilter(30) >> Process(fixer.octaMidiMuteFix), CtrlFilter(31) >> Process(fixer.octaMidiMuteFix),
      ],
      ChannelFilter(5) >> [ #Shifted MFT Outward
        CtrlFilter(range(0,12)) >> Process(amSynthOffset) >> Ctrl('amSynthOut', 9, EVENT_CTRL, EVENT_VALUE),
        CtrlFilter(12) >> Ctrl('amSynthOut', 9, 0, EVENT_VALUE),
        CtrlFilter(13) >> Program('amSynthOut', 9, EVENT_VALUE),
        CtrlFilter(range(14,16)) >> Process(amSynthOffset) >> Ctrl('amSynthOut', 9, EVENT_CTRL, EVENT_VALUE),

        CtrlFilter(range(48,64)) >> Process(guitarixShiftOffset) >> Ctrl('guitarixOut', 11, EVENT_CTRL, EVENT_VALUE),
      ],
      ChannelFilter(4) >> [ #MFT Side Buttons
        # Bank 1: 8 9 10 11 12 13
        CtrlFilter(8)  >> Ctrl('amSynthOut',9,21,EVENT_VALUE), CtrlFilter(11) >> [CtrlValueFilter(127) >> NoteOn('amSynthOut',9,48,127), CtrlValueFilter(0) >> NoteOff('amSynthOut',9,48)],
        CtrlFilter(9) >> CtrlValueFilter(127) >> System('/home/pi/DSPi/bash/dspiSwitcher.sh amsynth'), # Ctrl(12) >> NextBank()
        CtrlFilter(10) >> Ctrl('amSynthOut', 9, 91, EVENT_VALUE), CtrlFilter(13) >> [CtrlValueFilter(127) >> NoteOn('amSynthOut',9,24,127), CtrlValueFilter(0) >> NoteOff('amSynthOut',9,24)],
        # Bank 2: 14 15 16 17 18 19
        CtrlFilter(15) >> [
          CtrlValueFilter(127) >> System('jack_capture --daemon -O 7777 &') >> Ctrl('MFTOut', 3, 29, 127),
          CtrlValueFilter(0) >> System('oscsend localhost 7777 /jack_capture/stop') >> Ctrl('MFTOut', 3, 29, 0)
        ],
        # Bank 3: 20 21 22 23 24 25
        CtrlFilter(21) >> CtrlValueFilter(127) >> System('/home/pi/DSPi/bash/dspiSwitcher.sh debug'),
        # Bank 4: 26 27 28 29 30 31
        CtrlFilter(26) >> Ctrl('guitarixOut', 11, 96, EVENT_VALUE),
        CtrlFilter(27) >> CtrlValueFilter(127) >> System('/home/pi/DSPi/bash/dspiSwitcher.sh guitarix'),
                                                                                   CtrlFilter(31) >> CtrlValueFilter(0) >> System('sudo shutdown -h now'),
      ],
    ],
    PortFilter('amSynthIn') >> [
      # Unshifted
      CtrlFilter(80) >> Ctrl('MFTOut', 1, 0, EVENT_VALUE),      
      CtrlFilter(range(1,16)) >> Ctrl('MFTOut', 1, EVENT_CTRL, EVENT_VALUE),
      CtrlFilter(range(63,75)) >> Process(amSynthDeOffset) >> Ctrl('MFTOut', 5, EVENT_CTRL, EVENT_VALUE),
      # Shifted
      CtrlFilter(0) >> Ctrl('MFTOut', 5, 12, EVENT_VALUE),
      Filter(PROGRAM) >> Ctrl('MFTOut', 5, 13, EVENT_VALUE),
      CtrlFilter(range(77,79)) >> Process(amSynthDeOffset) >> Ctrl('MFTOut', 9, EVENT_CTRL, EVENT_VALUE),
    ],
    PortFilter('octatrackIn') >> [
      ChannelFilter(1) >> [ #MFT Inward
        # MIDI Mutes
        CtrlFilter(112) >> Process(fixer.mftMidiMuteFix), CtrlFilter(116) >> Process(fixer.mftMidiMuteFix),
        CtrlFilter(113) >> Process(fixer.mftMidiMuteFix), CtrlFilter(117) >> Process(fixer.mftMidiMuteFix),
        CtrlFilter(114) >> Process(fixer.mftMidiMuteFix), CtrlFilter(118) >> Process(fixer.mftMidiMuteFix),
        CtrlFilter(115) >> Process(fixer.mftMidiMuteFix), CtrlFilter(119) >> Process(fixer.mftMidiMuteFix),
      ],
      CtrlFilter(49) >> [
        # Mutes
        ChannelFilter(1) >> Process(fixer.mftVolumeMuteFix), ChannelFilter(5) >> Process(fixer.mftVolumeMuteFix),
        ChannelFilter(2) >> Process(fixer.mftVolumeMuteFix), ChannelFilter(6) >> Process(fixer.mftVolumeMuteFix),
        ChannelFilter(3) >> Process(fixer.mftVolumeMuteFix), ChannelFilter(7) >> Process(fixer.mftVolumeMuteFix),
        ChannelFilter(4) >> Process(fixer.mftVolumeMuteFix), ChannelFilter(8) >> Process(fixer.mftVolumeMuteFix),
      ],
      CtrlFilter(46) >> [
        # Volume
        ChannelFilter(1) >> Ctrl('MFTOut', 1, 16, EVENT_VALUE), ChannelFilter(5) >> Ctrl('MFTOut', 1, 17, EVENT_VALUE),
        ChannelFilter(2) >> Ctrl('MFTOut', 1, 20, EVENT_VALUE), ChannelFilter(6) >> Ctrl('MFTOut', 1, 21, EVENT_VALUE),
        ChannelFilter(3) >> Ctrl('MFTOut', 1, 24, EVENT_VALUE), ChannelFilter(7) >> Ctrl('MFTOut', 1, 25, EVENT_VALUE),
        ChannelFilter(4) >> Ctrl('MFTOut', 1, 28, EVENT_VALUE), ChannelFilter(8) >> Ctrl('MFTOut', 1, 29, EVENT_VALUE),
      ],
      CtrlFilter(47) >> [
        # Cue Volume
        ChannelFilter(1) >> Ctrl('MFTOut', 1, 18, EVENT_VALUE), ChannelFilter(5) >> Ctrl('MFTOut', 1, 19, EVENT_VALUE),
        ChannelFilter(2) >> Ctrl('MFTOut', 1, 22, EVENT_VALUE), ChannelFilter(6) >> Ctrl('MFTOut', 1, 23, EVENT_VALUE),
        ChannelFilter(3) >> Ctrl('MFTOut', 1, 26, EVENT_VALUE), ChannelFilter(7) >> Ctrl('MFTOut', 1, 27, EVENT_VALUE),
        ChannelFilter(4) >> Ctrl('MFTOut', 1, 30, EVENT_VALUE), ChannelFilter(8) >> Ctrl('MFTOut', 1, 31, EVENT_VALUE),
      ],
      Filter(SYSRT) >> Port('opzOut')
    ],
    PortFilter('guitarixIn') >> [
        CtrlFilter(range(64,80)) >> Process(guitarixDeOffset) >> Ctrl('MFTOut', 1, EVENT_CTRL, EVENT_VALUE),
        CtrlFilter(range(80,95)) >> Process(guitarixShiftDeOffset) >> Ctrl('MFTOut', 5, EVENT_CTRL, EVENT_VALUE),
    ],
    PortFilter('quNexusIn') >> [
      ChannelFilter(1) >> KeyFilter(72,96) >> Port('octatrackOut'),
      ChannelFilter(2) >> KeyFilter(72,96) >> Port('octatrackOut'),
      ChannelFilter(3) >> KeyFilter(72,96) >> Port('octatrackOut'),
      ChannelFilter(4) >> KeyFilter(72,96) >> Port('octatrackOut'),
      ChannelFilter(5) >> KeyFilter(72,96) >> Port('octatrackOut'),
      ChannelFilter(6) >> KeyFilter(72,96) >> Port('octatrackOut'),
      ChannelFilter(7) >> KeyFilter(72,96) >> Port('octatrackOut'),
      ChannelFilter(8) >> Channel(10) >> KeyFilter(72,96) >> Port('octatrackOut'), # Don't need notes on master track, so set to auto channel
      ChannelFilter(9) >> Port('amSynthOut'),
      ChannelFilter(10) >> Channel(1) >> Port('opzOut'), # OP-Z Kick
      ChannelFilter(11) >> Channel(2) >> Port('opzOut'), # OP-Z Snare
      ChannelFilter(12) >> Channel(3) >> Port('opzOut'), # OP-Z Hats
      ChannelFilter(13) >> Channel(5) >> Port('opzOut'), # OP-Z Bass
      ChannelFilter(14) >> Channel(6) >> Port('opzOut'), # OP-Z Lead
      ChannelFilter(15) >> Channel(7) >> Port('opzOut'), # OP-Z Arp
      ChannelFilter(16) >> Channel(8) >> Port('opzOut'), # OP-Z Chords
    ]
  ]
)
