#   Instrument file
#
# uses one or more sample definitions to "play" itself.
#
#
# contains array of samples, volume is split evenly among them.
#
#

from Sample import *
import numpy as np
import struct


class Instrument:
    Samples = []
    name = "pyxer-synth"

    def __init__(self, name = "pyxer-synth"):
        self.Samples = []
        self.generateCEG()
        self.name = name


    def generateCEG(self, octave = 4,typ='sin'):
        '''
        produces a single sample of the given waveform with 3 WaveFormFunctions
        '''
        #assume A4 is base octave at 440 hz. everything works off of assuming A4 is 440
        #will produce C4, E4, G4 if octave is 4
        C = 440 * math.pow(2, (((octave-4)*12+3.0)/12.0))
        E = 440 * math.pow(2, (((octave-4)*12+6.0)/12.0))
        G = 440 * math.pow(2, (((octave-4)*12+10.0)/12.0))
        #now we have the frequencies we need to give to our Sample.
        SAM = Sample()
        SAM.noteDuration = 4
        SAM.addFunc(C,typ,0.7)
        SAM.addFunc(E,typ,0.65)
        SAM.addFunc(G,typ,0.6)
        self.Samples.append(SAM)
        print("done")





    def play(self,frame):
        '''
        returns the frame from playing this instrument.
        '''
        val = 0
        for sam in self.Samples:
            val += sam.play(440,frame)
        return val

    def writeToFileTest(self, seconds = 4):
        rate = self.Samples[0].sampleRate
        G = wave.open(self.name + ".wav", "w")
        G.setnchannels(1)
        G.setsampwidth(2)
        G.setframerate(rate)
        data = []
        for i in range(rate * seconds):
            data.append(self.play(i))
        print(data)
        self.write(G,data)
        # G.writeframesraw(data)
        G.close()

    def write(self, afile,data):
        for val in data:
            afile.writeframesraw(struct.pack('<h',int(val * 32767)))
        afile.writeframes('')
