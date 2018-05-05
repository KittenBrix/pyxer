#   Sample
#
#
#
#   Sample contains a series of functions to define waveforms.
#
#   VOLUME: function that dictates output volume in one of three modes.
#       Duration:   function shape between x = 0 and x = 1 dictates volume over duration of the requested time alive.
#       Fixed:      function shape between x = 0 and x = 1 dictates volume over duration of one second
#

import numpy, sys, pyaudio, wav

#   use this to stream in real time instead of just write the data.
#https://stackoverflow.com/questions/31674416/python-realtime-audio-streaming-with-pyaudio-or-something-else



'''
defines how a "Sample" should be used within an instrument.
'''
class Sample:
    #set these per song
    beatsPerMinute = 120    #common bpm
    sampleRate = 44100      #most common sample rate
    noteDuration = 1/4      #quarter note duration.
    A4 = 440                #base frequency for establishing pitch.
    # [function definition (int frame, int )]
    waveFormsFuncs = []
    # literal array holding sample's play data
    WaveForm = []

    def __init__(self, frequency = '440', songParams = [120,44100] ):

    def
