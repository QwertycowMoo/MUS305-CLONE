from musx import Score, Seq, Note, MidiFile, paint
from musx.midi import gm
if __name__ == '__main__':
    seq = Seq()
    score = Score(out=seq)
    meta = MidiFile.metatrack(ins={0: gm.ElectricPiano2, 1: gm.Cello, 2: gm.Celesta, 3: gm.FrenchHorn})
    
    c7spray = paint.spray(score, pitch=60, duration=1.5, rhythm=.15, band=[0,4,7,11,12,16,19], end=54)
    c7brush = paint.brush(score, pitch=[96, 95, 91, 88], duration=2, rhythm=.15, end=27, instrument=2, amplitude=.35)
    hornPoly = paint.spray(score, pitch=60, band=[[12,16],[11,14],[9,12],[7,11]], rhythm=.6, end=24, instrument=3, amplitude=.35)
    c_longbass = paint.brush(score, pitch=[36, 31, 40, 35], rhythm=3, end=24, instrument=1)
    f_longbass = paint.brush(score, pitch=[29, 33, 40, 36, 29, 33, 40, 43], rhythm=[2.4, .6, 2.4, .6, 2.4, .6, 2.4, .6], end=24, instrument=1)
    score.compose([[0,c7spray], [3,c_longbass], [27, f_longbass], [27, c7brush], [27, hornPoly]])
    MidiFile("paint.mid", [meta, seq]).write()

    print("Wrote paint.mid")
