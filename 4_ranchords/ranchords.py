from musx import Score, Seq, Note, MidiFile
from musx.midi import gm
from random import randint

def ranchords(num, low, high):
    for i in range(num):
        chordType = randint(0, 3)
        if chordType == 0:
            # diminished
            highkey = high - 5
            startkey = randint(low, highkey)
            yield [startkey, startkey + 3, startkey + 6]
        elif chordType == 1:
            # minor
            highkey = high - 6
            startkey = randint(low, highkey)
            yield [startkey, startkey + 3, startkey + 7]
        elif chordType == 2:
            # major
            highkey = high - 6
            startkey = randint(low, highkey)
            yield [startkey, startkey + 4, startkey + 7]
        elif chordType == 2:
            # augmented
            highkey = high - 7
            startkey = randint(low, highkey)
            yield [startkey, startkey + 4, startkey + 8]

def playranchords(score, chords, rhy, dur, amp, chan=0):
    for chord in chords:
        note1 = Note(time=score.now, duration=dur, pitch=chord[0], amplitude=amp, instrument=chan)
        note2 = Note(time=score.now, duration=dur, pitch=chord[1], amplitude=amp, instrument=chan)
        note3 = Note(time=score.now, duration=dur, pitch=chord[2], amplitude=amp, instrument=chan)      
        score.add(note1)
        score.add(note2)
        score.add(note3)
        yield rhy

if __name__ == '__main__':

    print([c for c in ranchords(22, 60, 80)])

    # make a midi file that uses your ranchords()
    # ...
    seq = Seq()
    score = Score(out=seq)
    meta = MidiFile.metatrack(ins={0: gm.ElectricPiano1})
    score.compose([playranchords(score, ranchords(22,60,80), .4, .4, .5)])
    MidiFile("randchords.mid", [meta, seq]).write()
