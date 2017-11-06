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

mutes = {
  'volume': [False, False,False,False,False,False,False,False,False],
  'midi': [False, False,False,False,False,False,False,False,False],
}
ccToOctaTrack = {
  16:1,17:5,
  20:2,21:6,
  24:3,25:7,
  28:4,29:8,
}
octaTrackToCc = [0,16,20,24,28,17,21,25,29]
mftCcToOctaMidiTrack = {
  18:1,19:5,
  22:2,23:6,
  26:3,27:7,
  30:4,31:8,
}
octaMidiTrackToMftCc = [0,18,22,26,30,19,23,27,31]
octaCcToOctaMidiTrack = {
  112:1,116:5,
  113:2,117:6,
  114:3,118:7,
  115:4,119:8,
}
octaMidiTrackToOctaCc = [0,112,113,114,115,116,117,118,119]
onColor = 40
offColor = 85

def octaVolumeMuteFix(e):
  e.channel = ccToOctaTrack[e.ctrl]
  mutes['volume'][e.channel] = not mutes['volume'][e.channel]
  e.value = mutes['volume'][e.channel] * 255
  e.ctrl = 49
  return e
def octaMidiMuteFix(e):
  e.channel = 1
  mutes['midi'][e.channel] = not mutes['midi'][e.channel]
  e.value = mutes['midi'][e.channel] * 255
  e.ctrl = octaMidiTrackToOctaCc[mftCcToOctaMidiTrack[e.ctrl]]
  return e

def mftVolumeMuteFix(e):
  mutes['volume'][e.channel] = not mutes['volume'][e.channel]
  e.value = onColor if mutes['volume'][e.channel] else offColor
  e.ctrl = octaTrackToCc[e.channel]
  e.channel = 2
  return e
def mftMidiMuteFix(e):
  mutes['midi'][e.channel] = not mutes['midi'][e.channel]
  e.value = onColor if mutes['midi'][e.channel] else offColor
  e.ctrl = octaMidiTrackToMftCc[octaCcToOctaMidiTrack[e.ctrl]]
  e.channel = 2
  return e

run(
  [  
    PortFilter('MFT') >> [
      ChannelFilter(1) >> [ #MFT Outward
        CtrlFilter(range(0,16)) >> CtrlMap(0,80) >> Ctrl('amSynth', 9, EVENT_CTRL, EVENT_VALUE),

        CtrlFilter(16) >> Ctrl('octatrack', 1, 46, EVENT_VALUE), CtrlFilter(17) >> Ctrl('octatrack', 5, 46, EVENT_VALUE),
        CtrlFilter(20) >> Ctrl('octatrack', 2, 46, EVENT_VALUE), CtrlFilter(21) >> Ctrl('octatrack', 6, 46, EVENT_VALUE),
        CtrlFilter(24) >> Ctrl('octatrack', 3, 46, EVENT_VALUE), CtrlFilter(25) >> Ctrl('octatrack', 7, 46, EVENT_VALUE),
        CtrlFilter(28) >> Ctrl('octatrack', 4, 46, EVENT_VALUE), CtrlFilter(29) >> Ctrl('octatrack', 8, 46, EVENT_VALUE),

        CtrlFilter(18) >> Ctrl('octatrack', 1, 47, EVENT_VALUE), CtrlFilter(19) >> Ctrl('octatrack', 5, 47, EVENT_VALUE),
        CtrlFilter(22) >> Ctrl('octatrack', 2, 47, EVENT_VALUE), CtrlFilter(23) >> Ctrl('octatrack', 6, 47, EVENT_VALUE),
        CtrlFilter(26) >> Ctrl('octatrack', 3, 47, EVENT_VALUE), CtrlFilter(27) >> Ctrl('octatrack', 7, 47, EVENT_VALUE),
        CtrlFilter(30) >> Ctrl('octatrack', 4, 47, EVENT_VALUE), CtrlFilter(31) >> Ctrl('octatrack', 8, 47, EVENT_VALUE),

        CtrlFilter(range(48,64)) >> Process(guitarixOffset) >> Ctrl('guitarix', 11, EVENT_CTRL, EVENT_VALUE),
      ],
      ChannelFilter(2) >> [ #MFT Switches Outward
        # TODO: implement switch fix...
        CtrlFilter(16) >> Process(octaVolumeMuteFix) >> Port('octatrack'), CtrlFilter(17) >> Process(octaVolumeMuteFix) >> Port('octatrack'),
        CtrlFilter(20) >> Process(octaVolumeMuteFix) >> Port('octatrack'), CtrlFilter(21) >> Process(octaVolumeMuteFix) >> Port('octatrack'),
        CtrlFilter(24) >> Process(octaVolumeMuteFix) >> Port('octatrack'), CtrlFilter(25) >> Process(octaVolumeMuteFix) >> Port('octatrack'),
        CtrlFilter(28) >> Process(octaVolumeMuteFix) >> Port('octatrack'), CtrlFilter(29) >> Process(octaVolumeMuteFix) >> Port('octatrack'),

        CtrlFilter(18) >> Process(octaMidiMuteFix) >> Port('octatrack'), CtrlFilter(19) >> Process(octaMidiMuteFix) >> Port('octatrack'),
        CtrlFilter(22) >> Process(octaMidiMuteFix) >> Port('octatrack'), CtrlFilter(23) >> Process(octaMidiMuteFix) >> Port('octatrack'),
        CtrlFilter(26) >> Process(octaMidiMuteFix) >> Port('octatrack'), CtrlFilter(27) >> Process(octaMidiMuteFix) >> Port('octatrack'),
        CtrlFilter(30) >> Process(octaMidiMuteFix) >> Port('octatrack'), CtrlFilter(31) >> Process(octaMidiMuteFix) >> Port('octatrack'),
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
        CtrlFilter(112) >> Process(mftMidiMuteFix) >> Port('MFT'), CtrlFilter(116) >> Process(mftMidiMuteFix) >> Port('MFT'),
        CtrlFilter(113) >> Process(mftMidiMuteFix) >> Port('MFT'), CtrlFilter(117) >> Process(mftMidiMuteFix) >> Port('MFT'),
        CtrlFilter(114) >> Process(mftMidiMuteFix) >> Port('MFT'), CtrlFilter(118) >> Process(mftMidiMuteFix) >> Port('MFT'),
        CtrlFilter(115) >> Process(mftMidiMuteFix) >> Port('MFT'), CtrlFilter(119) >> Process(mftMidiMuteFix) >> Port('MFT'),
      ],
      CtrlFilter(49) >> [
        # Mutes
        ChannelFilter(1) >> Process(mftVolumeMuteFix) >> Port('MFT'), ChannelFilter(5) >> Process(mftVolumeMuteFix) >> Port('MFT'),
        ChannelFilter(2) >> Process(mftVolumeMuteFix) >> Port('MFT'), ChannelFilter(6) >> Process(mftVolumeMuteFix) >> Port('MFT'),
        ChannelFilter(3) >> Process(mftVolumeMuteFix) >> Port('MFT'), ChannelFilter(7) >> Process(mftVolumeMuteFix) >> Port('MFT'),
        ChannelFilter(4) >> Process(mftVolumeMuteFix) >> Port('MFT'), ChannelFilter(8) >> Process(mftVolumeMuteFix) >> Port('MFT'),
      ],
      CtrlFilter(46) >> [
        # Volume
        ChannelFilter(1) >> Ctrl('MFT', 1, 16, EVENT_VALUE), ChannelFilter(5) >> Ctrl('MFT', 1, 17, EVENT_VALUE),
        ChannelFilter(2) >> Ctrl('MFT', 1, 20, EVENT_VALUE), ChannelFilter(6) >> Ctrl('MFT', 1, 21, EVENT_VALUE),
        ChannelFilter(3) >> Ctrl('MFT', 1, 24, EVENT_VALUE), ChannelFilter(7) >> Ctrl('MFT', 1, 25, EVENT_VALUE),
        ChannelFilter(4) >> Ctrl('MFT', 1, 28, EVENT_VALUE), ChannelFilter(8) >> Ctrl('MFT', 1, 29, EVENT_VALUE),
      ],
      CtrlFilter(47) >> [
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