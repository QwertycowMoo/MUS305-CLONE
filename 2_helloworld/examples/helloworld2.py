from musx import Note, Score, Seq, MidiFile
from musx.midi import gm

def playstring(score, string, rhy, dur, amp, chan):
    for k in map(ord, string):
        note = Note(time=score.now, pitch=k, amplitude=amp, duration=dur, instrument=chan)
        score.add(note)
        yield rhy

if __name__ == '__main__':
    string = "Hello World!".upper()*2
    seq = Seq()
    metaseq = MidiFile.metatrack(ins = {0: gm.Xylophone})
    sco = Score(out=seq)

    sco.compose([
        playstring(sco, string, .25/2, .25, .75, 0), 
        playstring(sco, string.lower(), .25, .25, .75, 9),
        playstring(sco, string*4, .3, .35, .75, 1),
        playstring(sco, string*3, .31, .3123, .75, 0)
        ])
    # write the midi file
    MidiFile("helloworld.mid", [metaseq, seq]).write().print()

