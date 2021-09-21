from sys import warnoptions
from musx import Score, Seq, Note, MidiFile, paint
from musx.midi import gm

def clapper(trope, repeat, reverse=False, wraparound=False):
    index = 0
    offset = 0
    wraps = len(trope)

    if wraparound:
        wraps += 1
    for j in range(wraps):
        for k in range(len(trope)):
            for i in range(repeat):
                layer = []
                layer.append(trope[(index % len(trope))])
                layer.append(trope[(index + offset) % len(trope)])

                yield layer
                index += 1
        if reverse:
            offset -= 1
        else:
            offset += 1

def clapperComposer(score, pitchTrope, rhy, dur, amp, chan=0, repeatTrope=1, reverse=False, wraparound=False):
    rhythms = iter(rhy)
    for pitch1, pitch2 in clapper(pitchTrope, repeatTrope, reverse, wraparound):
        note1 = Note(time=score.now, duration=dur, pitch=pitch1, amplitude=amp, instrument=chan)
        note2 = Note(time=score.now, duration=dur, pitch=pitch2, amplitude=amp, instrument=chan)
        score.add(note1)
        score.add(note2)
        try:
            yield next(rhythms)
        except StopIteration:
            return

if __name__ == '__main__':
    seq = Seq()
    score = Score(out=seq)
    meta = MidiFile.metatrack(ins={0: gm.ElectricPiano2, 1: gm.ElectricBass_finger})
    primary_trope = [58, 61, 65, 53, 55, 56, 60]
    rhythm_trope = [0.5, 1, 0.5, 0.25, 0.25, 0.5, 1]
    bassline = paint.brush(score, pitch=[34, 46, 46, 34, 46, 46, 34, 46], duration=.5, rhythm=.5, end=64, instrument=1, amplitude=.6)
    rhythm1 = []
    rhythm2 = []
    for rhy1, rhy2 in clapper(rhythm_trope, 1, wraparound=True):
        rhythm1.append(rhy1)
        rhythm2.append(rhy2)
    
    print(rhythm1, rhythm2)

    score.compose([[0, bassline],
        [0,clapperComposer(score, primary_trope, rhythm1, .5, .7, wraparound=True)],
        [0, clapperComposer(score, primary_trope, rhythm2, .5, .7, wraparound=True)],
        [32,clapperComposer(score, primary_trope, rhythm1, .5, .7, reverse=True, wraparound=True)],
        [32, clapperComposer(score, primary_trope, rhythm2, .5, .7, reverse=True, wraparound=True)]])
    MidiFile("clapper.mid", [meta, seq]).write()
    seq.print()
    print("Wrote clapper.mid")

