# In this homework you will compose a short midi composition whose pitch
# (and any other sound attributes you want to include) is controlled by
# 'sonifying' python strings, where each ascii codepoint (character) in a
# string is treated as a midi key number. This works because the standard
# ascii character set (0-127) maps directly onto midi keynums =:).
# See:  https://commons.wikimedia.org/wiki/File:ASCII-Table-wide.svg

# Use this link to learn about the common musx imports listed below.
# https://musx-admin.github.io/musx/index.html
from musx import Score, Seq, Note, MidiFile, rescale
from musx.midi import gm
import argparse


# define a composer (generator) that will add notes to our score.
def playstring(score, string, rhy, dur, amp, chan=0):
    for char in map(ord, string):
        # create a note to play each asci code point as a MIDI key number
        # with a specified onset, duration and amplitude.
        p =  rescale(char, 0, 127, 10, 80)
        note = Note(time=score.now, duration=dur, pitch=p, amplitude=amp, instrument=chan)
        # add the note at the current time in the score
        score.add(note)
        # yield back the time to wait until the composer is called again.
        yield rhy

def playbassstring(score, string, rhy, dur, amp, chan=0):
    # copy of play string except the pitch is 127-char
    for char in map(ord, string):
        p =  rescale(char, 0, 127, 34, 50)
        note = Note(time=score.now, duration=dur, pitch=p, amplitude=amp, instrument=chan)
       
        score.add(note)

        yield rhy

if __name__ == '__main__':
    #
    # parser = argparse.ArgumentParser(description='hello world')
    # parser.add_argument("-c", "--chan", help="Which MIDI channel to play sonification on", default=1, type=int)
    # channel = parser.parse_args()
    # print(channel)

    # allocate a sequence to hold our notes
    seq = Seq()
    # Found that we only need one score and one sequence. Instead, we give multiple generators to the same score
    # Score has a sequence that is then played later
    # invertSeq = Seq()
    # TODO: Need to make a new Seq() with tempo and instrument data?



    # allocate a score and give it the sequence 
    score = Score(out=seq)
    meta = MidiFile.metatrack(ins={0: gm.ElectricPiano1, 1:gm.ElectricBass_pick})
    # scoreInv = Score(out=invertSeq)
    # our text to play
    text = "Hello World!Hello World!Hello World!Hello World!Hello World!"
    basstext = "Hello World!Hello World!Hello World!Hello World!"
    text = text.upper()
    basstext = basstext.upper()
    # tell the score to use our composer to create the composition.
    score.compose([playstring(score, text, .4, .25, .75),playbassstring(score, basstext, .5, .25, .75)])
    # write the midi file
    MidiFile("helloworld.mid", [meta, seq]).write()
    # print out the sequence
    seq.print()
    # success!
    print("Wrote helloworld.mid")


# TODO:
# upper case the string to move it to lower midi notes
# print the seq and/or midi file
# add a chan argument to helloworld and play drum map
# add metaseq with instruments
# add several composers