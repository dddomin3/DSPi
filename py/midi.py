#!/usr/bin/env python
from mididings import *
from mididings.event import *

config(
  client_name='mididings',
  in_ports=[
    'MFTIn',        # 0
    'amSynthIn',    # 1
    'octatrackIn',  # 2
    'guitarixIn',   # 3
    'quNexusIn',    # 4
    'opzIn',        # 5
  ],
  out_ports=[
    'MFTOut',       # 6
    'amSynthOut',   # 7
    'octatrackOut', # 8
    'guitarixOut',  # 9
    'opzOut',       # 10
  ],
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
  mftCcToChannel = {
    16:1, 17:5, 18:1, 19:5,
    20:2, 21:6, 22:2, 23:6,
    24:3, 25:7, 26:3, 27:7,
    28:4, 29:8, 30:4, 31:8,
  }
  octaChannelToCc = [16, 20, 24, 28, 17, 21, 25, 29]
  opzTrackToMftCc = [18, 22, 26, 30, 19, 23, 27, 31]
  offColor = 40
  onColor = 85

  octaMutes = [False, False, False, False, False, False, False, False]
  opzMutes = [False, False, False, False, False, False, False, False]
  mftPort = 'MFTOut'
  octaPort = 'octatrackOut'
  opzPort = 'opzOut'

  @classmethod
  def octaMuteFix(klass, e):
    octaChannel = klass.mftCcToChannel[e.ctrl]
    klass.octaMutes[octaChannel-1] = not klass.octaMutes[octaChannel-1]

    mftOut = CtrlEvent(
      klass.mftPort,
      2,
      klass.octaChannelToCc[octaChannel-1],
      klass.onColor if klass.octaMutes[octaChannel-1] else klass.offColor,
    )
    octaOut = CtrlEvent(
      klass.octaPort,
      octaChannel,
      49,
      klass.octaMutes[octaChannel-1] * 127,
    )

    print(klass.octaMutes,klass.opzMutes)
    return [mftOut, octaOut]
  
  @classmethod
  def mftOctaMuteFix(klass, e):
    octaTrack = e.channel
    klass.octaMutes[octaTrack-1] = not klass.octaMutes[octaTrack-1]

    mftOut = CtrlEvent(
      klass.mftPort,
      2,
      klass.octaChannelToCc[octaTrack-1],
      klass.onColor if klass.octaMutes[e.channel-1] else klass.offColor,
    )
    octaOut = CtrlEvent(
      klass.octaPort,
      octaTrack,
      49,
      klass.octaMutes[octaTrack-1] * 127,
    )

    print(klass.octaMutes,klass.opzMutes)
    return [mftOut, octaOut]
  
  @classmethod
  def opzMuteFix(klass, e):
    opzChannel = klass.mftCcToChannel[e.ctrl]
    klass.opzMutes[opzChannel-1] = not klass.opzMutes[opzChannel-1]

    mftOut = CtrlEvent(
      klass.mftPort,
      2,
      klass.opzTrackToMftCc[opzChannel-1],
      klass.onColor if klass.opzMutes[opzChannel-1] else klass.offColor
    )
    opzOut = CtrlEvent(
      klass.opzPort,
      opzChannel,
      53, # CC for opz mute
      int(klass.opzMutes[opzChannel-1])
    )

    print(klass.octaMutes,klass.opzMutes)
    return [mftOut, opzOut]
  
  @classmethod
  def mftOpzMuteFix(klass, e):
    opzChannel = e.channel
    klass.opzMutes[opzChannel-1] = not klass.opzMutes[opzChannel-1]

    mftOut = CtrlEvent(
      klass.mftPort,
      2,
      klass.opzTrackToMftCc[opzChannel-1],
      klass.onColor if klass.opzMutes[opzChannel-1] else klass.offColor
    )
    opzOut = CtrlEvent(
      klass.opzPort,
      opzChannel,
      53, # CC for opz mute
      int(klass.opzMutes[opzChannel-1])
    )

    print(klass.octaMutes,klass.opzMutes)
    return [mftOut, opzOut]

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

        CtrlFilter(18) >> Ctrl('opzOut', 1, 53, EVENT_VALUE), CtrlFilter(19) >> Ctrl('opzOut', 5, 53, EVENT_VALUE),
        CtrlFilter(22) >> Ctrl('opzOut', 2, 53, EVENT_VALUE), CtrlFilter(23) >> Ctrl('opzOut', 6, 53, EVENT_VALUE),
        CtrlFilter(26) >> Ctrl('opzOut', 3, 53, EVENT_VALUE), CtrlFilter(27) >> Ctrl('opzOut', 7, 53, EVENT_VALUE),
        CtrlFilter(30) >> Ctrl('opzOut', 4, 53, EVENT_VALUE), CtrlFilter(31) >> Ctrl('opzOut', 8, 53, EVENT_VALUE),

        CtrlFilter(range(48,64)) >> Process(guitarixOffset) >> Ctrl('guitarixOut', 11, EVENT_CTRL, EVENT_VALUE),
      ],
      ChannelFilter(2) >> [ #MFT Switches Outward
        CtrlFilter(16) >> Process(fixer.octaMuteFix), CtrlFilter(17) >> Process(fixer.octaMuteFix),
        CtrlFilter(20) >> Process(fixer.octaMuteFix), CtrlFilter(21) >> Process(fixer.octaMuteFix),
        CtrlFilter(24) >> Process(fixer.octaMuteFix), CtrlFilter(25) >> Process(fixer.octaMuteFix),
        CtrlFilter(28) >> Process(fixer.octaMuteFix), CtrlFilter(29) >> Process(fixer.octaMuteFix),

        CtrlFilter(18) >> Process(fixer.opzMuteFix), CtrlFilter(19) >> Process(fixer.opzMuteFix),
        CtrlFilter(22) >> Process(fixer.opzMuteFix), CtrlFilter(23) >> Process(fixer.opzMuteFix),
        CtrlFilter(26) >> Process(fixer.opzMuteFix), CtrlFilter(27) >> Process(fixer.opzMuteFix),
        CtrlFilter(30) >> Process(fixer.opzMuteFix), CtrlFilter(31) >> Process(fixer.opzMuteFix),
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
      CtrlFilter(49) >> [
        # Mutes
        ChannelFilter(1) >> Process(fixer.mftOctaMuteFix), ChannelFilter(5) >> Process(fixer.mftOctaMuteFix),
        ChannelFilter(2) >> Process(fixer.mftOctaMuteFix), ChannelFilter(6) >> Process(fixer.mftOctaMuteFix),
        ChannelFilter(3) >> Process(fixer.mftOctaMuteFix), ChannelFilter(7) >> Process(fixer.mftOctaMuteFix),
        ChannelFilter(4) >> Process(fixer.mftOctaMuteFix), ChannelFilter(8) >> Process(fixer.mftOctaMuteFix),
      ],
      CtrlFilter(46) >> [
        # Volume
        ChannelFilter(1) >> Ctrl('MFTOut', 1, 16, EVENT_VALUE), ChannelFilter(5) >> Ctrl('MFTOut', 1, 17, EVENT_VALUE),
        ChannelFilter(2) >> Ctrl('MFTOut', 1, 20, EVENT_VALUE), ChannelFilter(6) >> Ctrl('MFTOut', 1, 21, EVENT_VALUE),
        ChannelFilter(3) >> Ctrl('MFTOut', 1, 24, EVENT_VALUE), ChannelFilter(7) >> Ctrl('MFTOut', 1, 25, EVENT_VALUE),
        ChannelFilter(4) >> Ctrl('MFTOut', 1, 28, EVENT_VALUE), ChannelFilter(8) >> Ctrl('MFTOut', 1, 29, EVENT_VALUE),
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
    ],
    PortFilter('opzIn') >> [
      CtrlFilter(16) >> [
        # Cue Volume
        ChannelFilter(1) >> Ctrl('MFTOut', 1, 18, EVENT_VALUE), ChannelFilter(5) >> Ctrl('MFTOut', 1, 19, EVENT_VALUE),
        ChannelFilter(2) >> Ctrl('MFTOut', 1, 22, EVENT_VALUE), ChannelFilter(6) >> Ctrl('MFTOut', 1, 23, EVENT_VALUE),
        ChannelFilter(3) >> Ctrl('MFTOut', 1, 26, EVENT_VALUE), ChannelFilter(7) >> Ctrl('MFTOut', 1, 27, EVENT_VALUE),
        ChannelFilter(4) >> Ctrl('MFTOut', 1, 30, EVENT_VALUE), ChannelFilter(8) >> Ctrl('MFTOut', 1, 31, EVENT_VALUE),
      ],
    ],
  ]
)
