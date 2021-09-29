from musx import Score, MidiFile, Note, Seq
from musx.midi import gm
import random

def circlefifthsgen(score, startingPitch, rhy, dur, amp, length=12, rangeHigh=48, chan=0):
    # generate a bassline that goes around the circle of fifths
    # Also give it a range so that it flips up or down if it goes to high/low
    for i in range(length):
        pitch = startingPitch + i*5
        
        while (pitch > rangeHigh):
            pitch -= 12
        note = Note(score.now, dur, pitch=pitch, amplitude=amp, instrument=chan)
        score.add(note)
        if rhy is list:
            yield rhy[i]
        else:
            yield rhy

def voiceleading(score, starting_pitches, composer_dur, rhy, amp, range_low=60, range_high=84, chan=0):
    # Given a set of starting pitches, randomly move the notes up/down/same with stepwise motion
    # combined with the circle of fifth should lead to some cool resolutions - it doesnt but maybe we could work with it

    # Maybe weight the notes in some way
    # Later project could be taking this idea and giving weights to where it would go kinda markov chain-lie
    # Would need a function to find notes of a scale, then weight movement based on those keynums

    # Flaws with the current design: when we get two notes that eventually coincide to the same note
    #       we can get a lot of dissonance because they may go seperate directions and create minor seconds/major seconds within chord
    current_dur = 0
    rhy_iter = iter(rhy)
    first_pass = True
    # Change this list to change chance of moving the pitches
    # Maybe line envelope
    change_values = [-2, -2, -1, -1, -1, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2]
    # weighted choose function in musx
    while current_dur < composer_dur:
        note_dur = rhy
        if isinstance(rhy, list):
            try:
                note_dur = next(rhy_iter)
                current_dur += note_dur
            except StopIteration:
                # Keep looping through the rhythm list and reset it
                # Loop only stops when composer duration is reached
                rhy_iter = iter(rhy)
                note_dur = next(rhy_iter)
                current_dur += note_dur
        else:
            current_dur += rhy

        for i, pitch in enumerate(starting_pitches):

            newpitch = pitch
            if not first_pass:
                change_index = random.randint(0, len(change_values) - 1)
                newpitch = pitch + change_values[change_index]
                # keep the newpitch within the range
                while newpitch > range_high:
                    newpitch -= 12
                while newpitch < range_low:
                    newpitch += 12
            
            note = Note(time=score.now, duration=note_dur, pitch=newpitch, amplitude=amp, instrument=chan)
            score.add(note)
            starting_pitches[i] = newpitch
        first_pass = False
        yield note_dur
        
if __name__ == "__main__":
    seq = Seq()
    score = Score(out=seq)
    meta = MidiFile.metatrack(ins={0: gm.ElectricBass_finger, 1: gm.ElectricPiano2})
    starting_pitches = [65, 69, 72, 74]
    score.compose([circlefifthsgen(score, 41, 2, 2, .7), voiceleading(score, starting_pitches, 24, [1.25, .75], 1, 1, chan=1)])
    MidiFile("randchords.mid", [meta, seq]).write()
    seq.print()
