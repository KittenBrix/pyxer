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
        return int(this.sampleRate * this.beatLengthSeconds())

    # [function definition (self, int frame, long currentframetotal)]
    waveFormsFuncs = []
    # literal array holding sample's play data
    waveForm = []

    def __init__(self, frequency = '440', duration  = 1.0, songParams = [60,44100] ):
        self.beatsPerMinute = songParams[0]
        self.sampleRate=songParams[1]
        self.frequency = frequency
        self.noteDuration = duration


    def writeToWaveForm(self, previousFrames = 0):
        '''
        for each frame, execute waveformfuncs and add them to the current frame, reducing volume based on number of funcs.
        pass in previous frames so that the func can use them if need be for matching previous note end.
        '''
        vol = 1.0/len(self.waveFormsFuncs)
        for i in range(self.beatRateLength()):
            for WFF in self.waveFormsFuncs:
                self.waveForm[i] += vol * WFF.playFunction( i, self.sampleRate) * WFF.volFunction(i, self.sampleRate)






    '''
        frame = current frame on the note.
        currentframe = within the context of the song, this is the total number of frames so far.
    '''
class WaveFormFunction:
    volFunction = getConstantVol(1)
    playFunction = getSimpleSin()
    FREQ = 440

    def __init__(self, frq, typ="sin"):
        self.FREQ = frq
        volFunction = getConstantVol(0.8)
        playFunction = getSimpleWave(typ)

    def setConstantVolume(volume):
        volFunction = getConstantVol(volume)

    def getConstantVol(volume):
        def lambdaVolume(self,frame = 0, rate =0):
            return volume
        return lambdaVolume

    def setFrequency(self, frq):
        self.FREQ = frq


    '''
    use to obtain a basic wave form function.
    '''
    def getSimpleWave(typ = "sin", option = math.sin(math.pi / 4)):
        if (typ.contains("sin")):
            def lambdaSine(self, frame, rate):
                return SimpleSine(self.FREQ, frame, rate)
            return lambdaSine
        if (typ.contains("sqr")):
            def lambdaSqr(self, frame, rate):
                return SimpleSquare(self.FREQ, frame, rate)
            return lambdaSqr
        if (typ.contains("rect")):
            def lambdaRect(self, frame, rate):
                return SimpleRectangle(self.FREQ, frame, rate, option)
            return lambdaRect


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
