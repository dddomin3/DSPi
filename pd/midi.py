#!/usr/bin/python
from mididings import *

config(
  client_name='mididings',
  in_ports=['MFT','amSynth','octatrack', 'guitarix'],
  out_ports=['MFT','amSynth','octatrack', 'guitarix'],
)

# These functions help map MFT MIDI messages over to other usages.
# I usually use a CC offset to bring other programs CC's in line with
# MFT CCs, keeping it sequential but with an offset
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

mutes = [False,False,False,False,False,False,False,False]
midiMutes = [False,False,False,False,False,False,False,False]
ccToOctaTrack = {
  16:1,17:5,
  20:2,21:6,
  24:3,25:7,
  28:4,29:8,
}
octaTrackToCc = [16,20,24,28,17,21,25,29]
ccToOctaMidiTrack = {
  18:1,19:5,
  22:2,23:6,
  26:3,27:7,
  30:4,31:8,
}
octaMidiTrackToCc = [18,22,26,30,19,23,27,31]
onColor = 40
offColor = 85

run(
  [  
    PortFilter('MFT') >> [
      ChannelFilter(1) >> [ #MFT Outward
        CtrlFilter(range(0,16)) >> CtrlMap(0,80) >> Ctrl('amSynth', 9, EVENT_CTRL, EVENT_VALUE),

        CtrlFilter(16) >> Ctrl('octatrack', 1, 47, EVENT_VALUE), CtrlFilter(17) >> Ctrl('octatrack', 5, 47, EVENT_VALUE),
        CtrlFilter(20) >> Ctrl('octatrack', 2, 47, EVENT_VALUE), CtrlFilter(21) >> Ctrl('octatrack', 6, 47, EVENT_VALUE),
        CtrlFilter(24) >> Ctrl('octatrack', 3, 47, EVENT_VALUE), CtrlFilter(25) >> Ctrl('octatrack', 7, 47, EVENT_VALUE),
        CtrlFilter(28) >> Ctrl('octatrack', 4, 47, EVENT_VALUE), CtrlFilter(29) >> Ctrl('octatrack', 8, 47, EVENT_VALUE),

        CtrlFilter(18) >> Ctrl('octatrack', 1, 48, EVENT_VALUE), CtrlFilter(19) >> Ctrl('octatrack', 5, 48, EVENT_VALUE),
        CtrlFilter(22) >> Ctrl('octatrack', 2, 48, EVENT_VALUE), CtrlFilter(23) >> Ctrl('octatrack', 6, 48, EVENT_VALUE),
        CtrlFilter(26) >> Ctrl('octatrack', 3, 48, EVENT_VALUE), CtrlFilter(27) >> Ctrl('octatrack', 7, 48, EVENT_VALUE),
        CtrlFilter(30) >> Ctrl('octatrack', 4, 48, EVENT_VALUE), CtrlFilter(31) >> Ctrl('octatrack', 8, 48, EVENT_VALUE),

        CtrlFilter(range(48,64)) >> Process(guitarixOffset) >> Ctrl('guitarix', 11, EVENT_CTRL, EVENT_VALUE),
      ],
      ChannelFilter(2) >> [ #MFT Switches Outward
        # TODO: implement switch fix...
        CtrlFilter(16) >> Ctrl('octatrack', 1, 49, EVENT_VALUE), CtrlFilter(17) >> Ctrl('octatrack', 5, 49, EVENT_VALUE),
        CtrlFilter(20) >> Ctrl('octatrack', 2, 49, EVENT_VALUE), CtrlFilter(21) >> Ctrl('octatrack', 6, 49, EVENT_VALUE),
        CtrlFilter(24) >> Ctrl('octatrack', 3, 49, EVENT_VALUE), CtrlFilter(25) >> Ctrl('octatrack', 7, 49, EVENT_VALUE),
        CtrlFilter(28) >> Ctrl('octatrack', 4, 49, EVENT_VALUE), CtrlFilter(29) >> Ctrl('octatrack', 8, 49, EVENT_VALUE),

        CtrlFilter(18) >> Ctrl('octatrack', 1, 112, EVENT_VALUE), CtrlFilter(19) >> Ctrl('octatrack', 1, 116, EVENT_VALUE),
        CtrlFilter(22) >> Ctrl('octatrack', 1, 113, EVENT_VALUE), CtrlFilter(23) >> Ctrl('octatrack', 1, 117, EVENT_VALUE),
        CtrlFilter(26) >> Ctrl('octatrack', 1, 114, EVENT_VALUE), CtrlFilter(27) >> Ctrl('octatrack', 1, 118, EVENT_VALUE),
        CtrlFilter(30) >> Ctrl('octatrack', 1, 115, EVENT_VALUE), CtrlFilter(31) >> Ctrl('octatrack', 1, 119, EVENT_VALUE),
      ],
      ChannelFilter(5) >> [ #Shifted MFT Outward
        CtrlFilter(range(0,12)) >> Process(amSynthOffset) >> Ctrl('amSynth', 9, EVENT_CTRL, EVENT_VALUE),
        CtrlFilter(12) >> Ctrl('amSynth', 9, 0, EVENT_VALUE),
        CtrlFilter(13) >> Program('amSynth', 9, EVENT_VALUE),
        CtrlFilter(range(14,16)) >> Process(amSynthOffset) >> Ctrl('amSynth', 9, EVENT_CTRL, EVENT_VALUE),

        CtrlFilter(range(48,64)) >> Process(guitarixShiftOffset) >> Ctrl('guitarix', 11, EVENT_CTRL, EVENT_VALUE),
      ]
    ],
    PortFilter('amSynth') >> [
      # Unshifted
      CtrlFilter(80) >> Ctrl('MFT', 1, 0, EVENT_VALUE),      
      CtrlFilter(range(1,16)) >> Ctrl('MFT', 1, EVENT_CTRL, EVENT_VALUE),
      CtrlFilter(range(63,75)) >> Process(amSynthDeOffset) >> Ctrl('MFT', 5, EVENT_CTRL, EVENT_VALUE),
      # Shifted
      CtrlFilter(0) >> Ctrl('MFT', 5, 12, EVENT_VALUE),
      Filter(PROGRAM) >> Ctrl('MFT', 5, 13, EVENT_VALUE),
      CtrlFilter(range(77,79)) >> Process(amSynthDeOffset) >> Ctrl('MFT', 9, EVENT_CTRL, EVENT_VALUE),
    ],
    PortFilter('octatrack') >> [
      ChannelFilter(1) >> [ #MFT Inward
        # MIDI Mutes
        CtrlFilter(112) >> Ctrl('MFT', 2, 18, EVENT_VALUE), CtrlFilter(116) >> Ctrl('MFT', 2, 19, EVENT_VALUE),
        CtrlFilter(113) >> Ctrl('MFT', 2, 22, EVENT_VALUE), CtrlFilter(117) >> Ctrl('MFT', 2, 23, EVENT_VALUE),
        CtrlFilter(114) >> Ctrl('MFT', 2, 26, EVENT_VALUE), CtrlFilter(118) >> Ctrl('MFT', 2, 27, EVENT_VALUE),
        CtrlFilter(115) >> Ctrl('MFT', 2, 30, EVENT_VALUE), CtrlFilter(119) >> Ctrl('MFT', 2, 31, EVENT_VALUE),
      ],
      CtrlFilter(49) >> [
        # Mutes
        ChannelFilter(1) >> Ctrl('MFT', 2, 16, EVENT_VALUE), ChannelFilter(5) >> Ctrl('MFT', 2, 17, EVENT_VALUE),
        ChannelFilter(2) >> Ctrl('MFT', 2, 20, EVENT_VALUE), ChannelFilter(6) >> Ctrl('MFT', 2, 21, EVENT_VALUE),
        ChannelFilter(3) >> Ctrl('MFT', 2, 24, EVENT_VALUE), ChannelFilter(7) >> Ctrl('MFT', 2, 25, EVENT_VALUE),
        ChannelFilter(4) >> Ctrl('MFT', 2, 28, EVENT_VALUE), ChannelFilter(8) >> Ctrl('MFT', 2, 29, EVENT_VALUE),
      ],
      CtrlFilter(47) >> [
        # Volume
        ChannelFilter(1) >> Ctrl('MFT', 1, 16, EVENT_VALUE), ChannelFilter(5) >> Ctrl('MFT', 1, 17, EVENT_VALUE),
        ChannelFilter(2) >> Ctrl('MFT', 1, 20, EVENT_VALUE), ChannelFilter(6) >> Ctrl('MFT', 1, 21, EVENT_VALUE),
        ChannelFilter(3) >> Ctrl('MFT', 1, 24, EVENT_VALUE), ChannelFilter(7) >> Ctrl('MFT', 1, 25, EVENT_VALUE),
        ChannelFilter(4) >> Ctrl('MFT', 1, 28, EVENT_VALUE), ChannelFilter(8) >> Ctrl('MFT', 1, 29, EVENT_VALUE),
      ],
      CtrlFilter(48) >> [
        # Cue Volume
        ChannelFilter(1) >> Ctrl('MFT', 1, 18, EVENT_VALUE), ChannelFilter(5) >> Ctrl('MFT', 1, 19, EVENT_VALUE),
        ChannelFilter(2) >> Ctrl('MFT', 1, 22, EVENT_VALUE), ChannelFilter(6) >> Ctrl('MFT', 1, 23, EVENT_VALUE),
        ChannelFilter(3) >> Ctrl('MFT', 1, 26, EVENT_VALUE), ChannelFilter(7) >> Ctrl('MFT', 1, 27, EVENT_VALUE),
        ChannelFilter(4) >> Ctrl('MFT', 1, 30, EVENT_VALUE), ChannelFilter(8) >> Ctrl('MFT', 1, 31, EVENT_VALUE),
      ],
    ],
    PortFilter('guitarix') >> [
        CtrlFilter(range(64,80)) >> Process(guitarixDeOffset) >> Ctrl('MFT', 1, EVENT_CTRL, EVENT_VALUE),
        CtrlFilter(range(80,95)) >> Process(guitarixShiftDeOffset) >> Ctrl('MFT', 5, EVENT_CTRL, EVENT_VALUE),
    ]
  ]
)