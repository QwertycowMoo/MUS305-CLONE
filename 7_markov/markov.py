from musx import Score, MidiFile, Note, Seq
from musx.midi import gm
from musx.gens import markov
import random

# Have multiple composers that are always the same length
# The higher order (3,4,5) composers are going to call the simpler composers so that we have all the textures of the previous ones
# Heirarchy is:
# 1. single turn
# 2. double turns going outwards from single turn
# 3. more turns going outwards from double turns
# 4. octave quarter notes on some note
# 5. Maybe some triplet figure
def turn(score, startPitch, modify, rhy, amp, length, chan=0, rev=False):
    # the length of this function is the total number of notes, not the number of beats to fill
    # Same with rhy, expects individual note length not length of beat in the x_order_turn functions
    turn_data = []
    if not rev:
        turn_data = [startPitch + modify, startPitch + modify + 1, startPitch + modify, startPitch + modify - 1]
    else:
        turn_data = [startPitch - modify, startPitch - modify - 1, startPitch - modify, startPitch - modify + 1]
    for i in range(length):
        pitch = turn_data[i % len(turn_data)]
        # Duration of the note is going to be same as rhy
        note = Note(score.now, rhy, pitch=pitch, amplitude=amp, instrument=chan)
        score.add(note)
        yield rhy

def first_order_turn(score, startPitch, rhy, amp, length, chan=0):
    turn_length = length * 4
    turn_rhy = rhy / 4
    turn_gen = turn(score, startPitch, 0, turn_rhy, amp, turn_length)
    for r in turn_gen:
        yield r


def second_order_turn(score, startPitch, rhy, amp, length, chan=0):
    turn_length = length * 4
    turn_rhy = rhy / 4
    turn_gen1 = turn(score, startPitch, 4, turn_rhy, amp, turn_length)
    turn_gen2 = turn(score, startPitch, 4, turn_rhy, amp, turn_length, rev=True)
    score.compose(first_order_turn(score, startPitch, rhy, amp, length, chan))
    for r in zip(turn_gen1, turn_gen2):
        yield r[0]
    

def third_order_turn(score, startPitch, rhy, amp, length, chan=0):
    turn_length = length * 6
    turn_rhy = rhy / 6
    turn_gen1 = turn(score, startPitch, 8, turn_rhy, amp, turn_length)
    turn_gen2 = turn(score, startPitch, 8, turn_rhy, amp, turn_length, rev=True)
    score.compose(second_order_turn(score, startPitch, rhy, amp, length, chan))
    for r in zip(turn_gen1, turn_gen2):
        yield r[0]

def fourth_order_turn(score, startPitch, rhy, amp, length, chan=0):
    turn_length = length * 3
    turn_rhy = rhy / 3
    turn_gen1 = turn(score, startPitch, 14, turn_rhy, amp, turn_length)
    turn_gen2 = turn(score, startPitch, 14, turn_rhy, amp, turn_length, rev=True)
    score.compose(third_order_turn(score, startPitch, rhy, amp, length, chan))
    for r in zip(turn_gen1, turn_gen2):
        yield r[0]

def fifth_order_turn(score, startPitch, rhy, amp, length, chan=0):
    turn_length = length * 8
    turn_rhy = rhy / 8
    turn_gen1 = turn(score, startPitch, 20, turn_rhy, amp, turn_length)
    turn_gen2 = turn(score, startPitch, 20, turn_rhy, amp, turn_length, rev=True)
    score.compose(fourth_order_turn(score, startPitch, rhy, amp, length, chan))
    for r in zip(turn_gen1, turn_gen2):
        yield r[0]

def markov_composer(score, startingPitch, rhy, amp, section_length, channels):
    # Needs a list of channels to give to the orders so that each order has a diff instrument
    # Will go through the list sequentially for the channels
    # Basically have a markov rule that has composers as its outcomes
    # Textural piece?
    rules = {(0, 0): [first_order_turn],
            (0, first_order_turn): [first_order_turn],
            (first_order_turn, first_order_turn): [[first_order_turn, 2], [second_order_turn, 2], 0],
            (first_order_turn, second_order_turn): [second_order_turn, third_order_turn],
            (second_order_turn, second_order_turn): [[second_order_turn, 2], [third_order_turn, 2], first_order_turn],
            (second_order_turn, third_order_turn): [[third_order_turn, 2], [fourth_order_turn, 2], second_order_turn],
            (third_order_turn, third_order_turn): [[third_order_turn, 2], [fourth_order_turn, 2], second_order_turn],
            (third_order_turn, fourth_order_turn): [[fourth_order_turn, 2], [fifth_order_turn, 2], third_order_turn],
            (fourth_order_turn, fourth_order_turn): [fourth_order_turn, [fifth_order_turn, 2], [third_order_turn, 2]],
            (fourth_order_turn, fifth_order_turn): [fourth_order_turn, [fifth_order_turn, 3]],
            (fifth_order_turn, fifth_order_turn): [fifth_order_turn, [fourth_order_turn, 3]],
            (fifth_order_turn, fourth_order_turn): [fourth_order_turn, fifth_order_turn, [third_order_turn, 3]],
            (fourth_order_turn, third_order_turn): [third_order_turn, second_order_turn],
            (third_order_turn, second_order_turn): [second_order_turn, first_order_turn],
            (second_order_turn, first_order_turn): [first_order_turn, 0],
            (first_order_turn, 0): [0]
            }
    markov_chain = markov(rules)
    for i, composer in enumerate(markov_chain):
        print(composer)
        # have a root rhythm that the composers will derive their own rhythm from
        # length is going to be number of notes within one "measure"
        if composer == 0:
            break
        chan = channels
        if isinstance(channels, list):
            chan = channels[i % len(channels)]
        score.compose(composer(score, startingPitch, rhy, amp, section_length, chan))
        yield rhy * section_length

if __name__ == "__main__":
    
    seq = Seq()
    score = Score(out=seq)
    meta = MidiFile.metatrack(ins={0: gm.Accordion, 1: gm.ElectricPiano2})
    channels = [0, 1]
    score.compose([markov_composer(score, 60, .8, .8, 2, channels)])
    MidiFile("markov.mid", [meta, seq]).write()
    # seq.print()