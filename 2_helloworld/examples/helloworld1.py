from musx import Score, Seq, Note, MidiFile
from musx.midi import gm

def playstring(score, string, rhy, dur, amp, chan):
    for k in map(ord, string):
        note = Note(time=score.now, pitch=k, amplitude=amp, duration=dur, instrument = chan)
        score.add(note)
        yield rhy

if __name__ == '__main__':
    #ms = MidiFile.metatrack(ins={0: AcousticGrandPiano, 1: Violin})
    seq = Seq()
    score = Score(out=seq)
    string = "Anna Civic Kayak Level Madam Mom Noon Racecar Radar Redder Refer Repaper Rotator Rotor Sagas Solos Stats Tenet Wow".upper()
    score.compose([playstring(score, string, .25, .25, .75, 0),
                   playstring(score, string, .3333333, .25, .75, 9)])
    MidiFile("helloworld.mid", seq).write().print()


# TODO:
# upper case the string to move it to lower mi di notes
# rename function to playstring(queue, string, ...)
# print the midi file
# add a chan argument to helloworld and play drum map
# add metaseq with instruments
# add several composers
