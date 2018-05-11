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

import numpy as np
import sys
import pyaudio, wave, math
import struct

#   use this to stream in real time instead of just write the data.
#https://stackoverflow.com/questions/31674416/python-realtime-audio-streaming-with-pyaudio-or-something-else



'''
defines how a "Sample" should be used within an instrument.
'''
class Sample:
    #set these per song per note
    beatsPerMinute = 120    #common bpm
    sampleRate = 44100      #most common sample rate. Sample never changes it.
    noteDuration = 1        #note duration. defaults to quarter notes. 1 = quarter note.
    A4 = 440                #base frequency for establishing pitch.
    frequency = A4          #note frequency

    #beatLengthSeconds is the literal number of seconds the sample lasts for.
    #it's based on the note type (quarter/half/eight/etc) and the bpm.
    def beatLengthSeconds(self):
        # (S/M) / (B/M) * Beats = S/M*M/B*B = Seconds
        return float(60.0/float(self.beatsPerMinute) * float(self.noteDuration))

    #beatRateLength is the number of samples we write to. eg. if we have 60 bpm,
    # it means a quarter note takes 1 second worth of time, which is multiplied
    # by the sample rate to determine how many samples need to be written.
    def beatRateLength(self):
        #samplerate = frames per second
        #beatlengthseconds = Seconds
        # F/S * S = Frames
        return int(self.sampleRate * self.beatLengthSeconds())

    # [function definition (self, int frame, long currentframetotal)]
    waveFormsFuncs = []
    # literal array holding sample's play data
    waveForm = []

    def __init__(self, frequency = '440', duration  = 1.0, songParams = [60,44100] ):
        self.beatsPerMinute = songParams[0]
        self.sampleRate=songParams[1]
        self.frequency = frequency
        self.noteDuration = duration

    def addFunc(self,freq,typ='sin',volume = 1):
        '''
        adds a waveformfunction to the funcs array of the given form and frequency
        '''
        F = WaveFormFunction(freq, typ)
        F.setConstantVolume(volume)
        self.waveFormsFuncs.append(F)




    def writeToWaveForm(self, instrumentFrequency, previousFrames = 0):
        '''
        for each frame, execute waveformfuncs and add them to the current frame, reducing volume based on number of funcs.
        pass in previous frames so that the func can use them if need be for matching previous note end.
        '''
        vol = 1.0/len(self.waveFormsFuncs)
        LENGTH = self.beatRateLength()
        #verify appropriate length in waveForm array
        while (len(self.waveForm) < LENGTH):
            self.waveForm.append(0)
        for i in range(LENGTH):
            for WFF in self.waveFormsFuncs:
                self.waveForm[i] += vol * WFF.playFunction(WFF, (i+previousFrames) *self.frequency/self.A4 * instrumentFrequency/A4, self.sampleRate) * WFF.volFunction(WFF,  (i+previousFrames) *self.frequency/self.A4 * instrumentFrequency/self.A4, self.sampleRate)


    def play(self, instrumentFrequency, frame):
        vol = 1.0/len(self.waveFormsFuncs)
        val = 0.0
        # print(self.A4)
        # print(self.frequency)
        # print(instrumentFrequency)
        # print(frame)
        frm = frame *float(self.frequency)/float(self.A4) * float(instrumentFrequency)/float(self.A4)
        for WFF in self.waveFormsFuncs:
            val += vol * WFF.playFunction(WFF, frm , self.sampleRate) * WFF.volFunction(WFF,  frm, self.sampleRate)
        return val


    '''
        frame = current frame on the note.
        currentframe = within the context of the song, this is the total number of frames so far.
    '''
class WaveFormFunction:
    volFunction = ''
    playFunction = ''
    FREQ = ''
    sourcepath = ''
    source = []
    sourcerate = ''
    def __init__(self, frq = 440, typ="sin"):
        self.FREQ = frq
        self.volFunction = self.getConstantVol(0.8)
        self.playFunction = self.getSimpleWave(typ)

    def setConstantVolume(self,volume):
        self.volFunction = self.getConstantVol(volume)

    def getConstantVol(self,volume):
        def lambdaVolume(self,frame = 0, rate =0):
            return volume
        return lambdaVolume

    def setLFOVolume(self,midpoint =0.6,sinamplitude =0.5, freq = 11, overdrive = False):
        def lambdaLFO(self, frame = 0, rate = 0):
            x = midpoint + sinamplitude*SimpleSine(freq, frame, rate)
            if (x > 1.0 and not overdrive):
                x = 1.0
            if (x < 0):
                x = 0
            return x
        return lambdaLFO


    def setFrequency(self, frq):
        self.FREQ = frq


    '''
    use to obtain a basic wave form function.
    '''
    def getSimpleWave(self,typ = "sin", option = math.sin(math.pi / 4)):
        if ("sin" in typ):
            def lambdaSine(self, frame, rate):
                return SimpleSine(self.FREQ, frame, rate)
            return lambdaSine
        if ("sqr" in typ):
            def lambdaSqr(self, frame, rate):
                return SimpleSquare(self.FREQ, frame, rate)
            return lambdaSqr
        if ("rect" in typ):
            def lambdaRect(self, frame, rate):
                return SimpleRectangle(self.FREQ, frame, rate, option)
            return lambdaRect

    def getSourceWave(self):
        def lambdaSource(self,frame,rate):
            frm = int(frame * self.sourcerate / rate )
            if (frm >= len(self.source)):
                return 0.0
            return self.source[frm]
        return lambdaSource

    def useSourceFile(self,sourcep):
        #using solution from https://stackoverflow.com/questions/7769981/how-to-convert-wave-file-to-float-amplitude
        self.sourcepath = sourcep
        w = wave.open(self.sourcepath)
        print("opened file succesfully")
        #populate source array with values direct from the wav file
        astr = w.readframes(w.getnframes())
        # convert binary chunks to short
        a = struct.unpack("%ih" % (w.getnframes()* w.getnchannels()), astr)
        self.source = [float(val) / math.pow(2, 15) for val in a]
        self.sourcerate = w.getframerate()
        #modify playFunction to utilize this info.
        self.playFunction = self.getSourceWave()





#simple sine. produces a sin wave frame value based on frame number, frequency, and sample rate
def SimpleSine(frequency,frame, rate):
    return math.sin(frequency * frame * (2* math.pi / rate))

#simple square wave. output ranges between 0 and 1
def SimpleSquare(frequency, frame, rate):
    return 1.0 if (math.sin(frequency * frame * 2 * math.pi / rate) > 0) else 0

#
def SimpleRectangle(frequency, frame, rate, cutoff = math.sin(math.pi / 4)):
    return 1.0 if (math.sin(frequency * frame * 2 * math.pi / rate) > cutoff) else 0





#
