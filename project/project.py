# What if we had a farming game that was set inside a computer where you had to take care of your bits and such
# Like farmville except there's fun CS related effects and ailments like segfaults
# Or you're taking care of notes and the ones that you plant have an effect on the soundtrack
from musx.gens import markov_analyze
import rtmidi
import musx
from play_realtime_midi import play_midi
import copy
import pprint
from composers import melody_composer, chordal_composer, bass_composer

# Real time midi out to Ableton
ableton_midiout = rtmidi.MidiOut()
outports = ableton_midiout.get_ports()
ableton_midiout.open_port(outports.index("AbletonIn 1"))

SCALES = ['C', 'G', 'D', 'A', 'E', 'B', 'F#',
          'C#', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F']
MAJOR_SCALE_INTERVALS = [2, 2, 1, 2, 2, 2, 1]
MINOR_SCALE_INTERVALS = [2, 1, 2, 2, 1, 2, 2]
LYDIAN_SCALE_INTERVALS = [2, 2, 2, 1, 2, 2, 1]


def create_chord_scale(sharps, scale):
    # Possible that we implement complexity here?
    scale = create_scale(sharps, scale)
    chords = []
    for i in range(8):
        chord = scale[i:i+8:2]  # Move by thirds
        chord = [musx.Pitch.from_keynum(chord_note) for chord_note in chord]
        chords.append(chord)
    return chords


def create_scale(sharps, scale):
    root = SCALES[sharps]
    # Start on the 4th octave always
    root_keynum = musx.keynum(root + "4")
    # Create a 2 octave scale
    scale = musx.scale(root_keynum, 16, scale)
    return scale


def harmonize(notes, chord_scale, notelen_param=0, harm_interest=0):
    """
    Notes are the notes in one measure, where a measure is the time between strong beats
    Larger notelen_param, the more the length of the note matters, 0 for just pitches themselves
    No tonal harmony param, just try to do bass well with voicelead_bass()
    """
    # See which chord fits the notes the best
    return_chord = []
    penalty = 100000000  # A large number
    for chord in chord_scale:
        chord_penalty = find_penalty(notes, chord, notelen_param)
        if chord_penalty < penalty:
            penalty = chord_penalty
            return_chord = list(chord)
    if musx.odds(harm_interest):
        # Pick the one either a third or fifth away, since we are doing this modally
        if musx.odds(.5):
            # Need to make a copy of the chord so that inversions do not screw up the original chords
            return_chord = list(
                chord_scale[(chord_scale.index(return_chord) + 2) % len(chord_scale)])
        else:
            return_chord = list(
                chord_scale[(chord_scale.index(return_chord) + 4) % len(chord_scale)])
    return return_chord


def find_penalty(notes, chord, notelen_param):
    # notes is list of tuples
    # chord is a bunch of Pitches
    penalty = 0
    for note in notes:
        notelen = note[1]
        try:
            pitch = musx.Pitch.from_keynum(note[0])
            min_distance = min([abs(chord_note.pnum() - pitch.pnum())
                                for chord_note in chord])
            if notelen_param:
                penalty += min_distance * notelen_param * notelen
            else:
                penalty += min_distance
        except ValueError:
            continue
    return penalty


def split_melody(melody, time_sig):
    """Splits the melody into measure for harmonize() to work on

    Args:
        melody ([type]): list of tuples of notes
        time_sig ([type]): Fraction object
    """
    # If a note flows over the measure, we split it into two notes for each measure so it can still be harmonized
    measure_time = time_sig[0] * 4 / time_sig[1]
    measures = []
    aggr_time = 0
    measure = []
    for note in melody:
        note_len = note[1]
        aggr_time += note_len
        if aggr_time > measure_time:
            # cut the note into two parts
            time_diff = aggr_time - measure_time
            split_note = (note[0], note_len - time_diff)
            measure.append(split_note)
            measures.append(copy.copy(measure))
            flowover = (note[0], time_diff)
            aggr_time = time_diff
            measure = [flowover]
            continue
        measure.append(note)
        if aggr_time == measure_time:
            measures.append(copy.copy(measure))
            measure = []
            aggr_time = 0
    if len(measure) > 0:
        measures.append(copy.copy(measure))
    return measures


def voicelead_chords(harmonized_chords, voicelead_rand=0):
    """Voicelead param will try to move the bass as little as possible. More voicelead param leads to more randomness of how the bass moves
      Parallel array to harmonized chords that will tell how many inversions to apply onto the chord
      First chord will never be inverted

    Args:
        harmonized_chords ([type]): [description]
        voicelead_rand (int, optional): Defaults to 0. Goes between 0 and 1. 0.2 sounds pretty good

    Returns:
        [type]: [description]
    """

    num_inversions = [0]
    bassnote = harmonized_chords[0][0]
    for chord in harmonized_chords[1:]:
        # If odds are less than voicelead_param, then its random choice of inversion
        if musx.odds(voicelead_rand):
            # randomizer to just choose an inversion
            num_inversions.append(musx.between(0, 4))
        else:
            # if not random, try to voice lead with little movement as possible
            distances = [abs(bassnote.keynum() - chordnote.keynum())
                         for chordnote in chord]
            # Append to the end of list where num inversions is where
            num_inversions.append(distances.index(min(distances)))
    return num_inversions


def create_b_melody(original_melody, length, similarity=1, slowdown=0, transposition=0):
    """Uses markov_analyze to create a B section in a different key, then harmonizes it. 
    Similarity is markov depth of the analysis. Higher makes it more similar to the A melody
    Length is number of measures
    Higher level function will handle splitting the melody into measures and taking care of unfilled last measure
    Args:
        length (int): length of b section
        similarity (int, optional): Defaults to 1, markov parameter for similarity to original melody
        slowdown (int, optional): Chance to double the length of a note, adds rhythmic interest
        transposition (int, optional): how many semitones to transpose this melody
    a prime melody can just use b_melody with original melody length, high similarity, and no slowdown
    """
    # No way for less than first order markov chain right?
    rules = musx.markov_analyze(original_melody, similarity)
    markov_chain = musx.markov(rules)
    b_melody = []
    b_melody_length = 0
    for note in markov_chain:
        # Slow down b section

        if musx.odds(slowdown/10):
            note = (note[0] + transposition, note[1] * 2)
        else:
            note = (note[0] + transposition, note[1])
        b_melody_length += note[1]
        if b_melody_length > length:
            break
        b_melody.append(note)
    return b_melody


def rotate_chord(chord, inversion):
    # make copy of the chord so original chord list does not get messed up
    return_chord = list(chord)
    for i in range(inversion):
        return_chord[i] = musx.Pitch.from_keynum(chord[i].keynum() + 12)
    return return_chord


def invert_chords(chords, inversions, transpose_key=0, lokey=44, hikey=72):
    for i, chord in enumerate(chords):
        inversion = inversions[i]
        chord = rotate_chord(chord, inversion)
        chord = [musx.Pitch.from_keynum(
            chord_note.keynum() + transpose_key) for chord_note in chord]
        if chord[0].keynum() < lokey:
            chord = [musx.Pitch.from_keynum(
                chord_note.keynum() + 12) for chord_note in chord]
        while chord[3].keynum() > hikey:
            chord = [musx.Pitch.from_keynum(
                chord_note.keynum() - 12) for chord_note in chord]
        chords[i] = chord
    return chords


def gen_counter_scale(num_sharps, scale_type, start):
    """Will yield one note at a time"""
    index = start
    direction = musx.pick(1, -1)  # Whether going up or down
    inarow = 0
    scale = create_scale(num_sharps, scale_type)
    while True:
        yield scale[index]
        index += direction
        inarow += 1
        if musx.odds(inarow/8) or index == len(scale) - 1 or index == 0:
            direction = -direction
            inarow = 0


def create_countermelody(root_pos_chords, notes_per_measure, num_sharps, scale, time_sig):

    def gen_notes(num_notes):
        start = musx.pick(7, 9, 11)
        counter_gen = gen_counter_scale(num_sharps, scale, start)
        generated_melody = []
        for i in range(num_notes):
            generated_melody.append(next(counter_gen))
        return generated_melody

    countermelody = []
    measure_length = time_sig[0]
    # create a scale generator, then call next to fill in the number of notes
    # start on the first, third, or fifth of the scale in the middle of the scale
    gm_index = 0
    if notes_per_measure < measure_length:
        # start on second note and play number of notes, fill in the rest with rests
        # generate four notes to be used
        four_notes = gen_notes(4)
        for measure in root_pos_chords:
            countermelody.append((-1, 1))
            for _ in range(notes_per_measure):
                countermelody.append((four_notes[gm_index], 1))
                gm_index += 1
                if gm_index > 3:
                    four_notes = gen_notes(4)
                    gm_index = 0
            for _ in range(measure_length - 1 - notes_per_measure):
                countermelody.append((-1, 1))
    else:
        # Start on first note and do a scale with each note equal to measure_length/num_notes
        for measure in root_pos_chords:
            notes = gen_notes(notes_per_measure)
            for n in notes:
                countermelody.append((n, 4/notes_per_measure))
    return countermelody


if __name__ == "__main__":
    # Addon TODO: Create randomize all parameters and make composition
    # Addon TODO: Harmonize the melody using the other not used synth
    # Addon TODO: Create a melody in 3/4 and 2/4
    pp = pprint.PrettyPrinter()

    ### INTIALIZATION ###
    # Pure Imagination from willy wonka
    melody = [(-1, 2), (60, 1), (63, 1),
              (70, 2), (60, 1), (63, 1),
              (70, 2), (60, 1), (63, 1),
              (74, 1.5), (75, 0.5), (74, 0.5), (75, 0.5), (74, 0.5), (75, 0.5),
              (74, 0.5), (70, 0.5), (67, 2), (60, 0.5), (63, 0.5),
              (67, 2), (68, 1), (70, 1),
              (67, 2), (65, 1), (63, 1),
              (62, 0.5), (63, 0.5), (62, 0.5), (63, 0.5), (62, 1), (58, 5)]
    num_sharps = -3
    tempo = 95
    time_sig = (4, 4)
    has_pickup = True
    # Little melody I made up
    # melody = [(-1, 2), (70, 1), (69, 1),
    #           (65, 1), (65, 0.5), (62, 0.5), (65, 0.5), (67, 1),
    #           (62, 2.5), (70, 1), (69, 1),
    #           (65, 1), (65, 0.5), (62, 0.5), (65, 0.5), (67, 1),
    #           (74, 2.5), (75, 1), (74, 1),
    #           (67, 2), (75, 1), (74, 1),
    #           (69, 2), (72, 1), (74, 1),
    #           (70, 8)]
    # time_sig = (4, 4)
    # num_sharps = -2  # key signature of the melody, similar to how musicxml does it
    # has_pickup = True
    # tempo = 120

    ### A SECTION ###
    print("A Section")
    chord_scale = create_chord_scale(num_sharps, MAJOR_SCALE_INTERVALS)
    melody_length = 0
    for note in melody:
        melody_length += note[1]
    print(melody_length)
    chords = []
    for measure in split_melody(melody, time_sig):
        # allow for pickup by checking if first note is a rest, don't harmonize it
        if measure[0][0] == -1:
            # pickup measure
            continue
        chords.append(harmonize(measure, chord_scale, harm_interest=.1))
    # Give root position chord to sparkle generator
    countermelody = create_countermelody(
        chords, 4, num_sharps, MAJOR_SCALE_INTERVALS, time_sig)
    print(countermelody)
    inversions = voicelead_chords(chords, voicelead_rand=0.2)
    chords = invert_chords(chords, inversions)

    ### B SECTION ###
    #   b_melody transposed into the fifth below, subtract a sharp
    print("B Section")
    # quantize b section length to the nearest bar
    b_melody_length = time_sig[0] * round((melody_length / 2) / time_sig[0])
    print("b_melody", b_melody_length)
    b_melody = create_b_melody(
        melody, b_melody_length, similarity=1, slowdown=3, transposition=-7)
    b_sharps = num_sharps - 1

    b_chord_scale = create_chord_scale(b_sharps, MAJOR_SCALE_INTERVALS)
    b_chords = []
    for measure in split_melody(b_melody, time_sig):
        b_chords.append(harmonize(measure, b_chord_scale, harm_interest=.1))
    b_inversions = voicelead_chords(b_chords, voicelead_rand=0.2)
    b_chords = invert_chords(b_chords, b_inversions,
                             transpose_key=-7, lokey=52, hikey=79)

    ### A PRIME SECTION ###
    print("A' Section")
    # create_b_melody(melody, melody_length, similarity=10)
    a_prime_melody = melody
    a_prime_chords = []
    for measure in split_melody(a_prime_melody, time_sig):
        a_prime_chords.append(
            harmonize(measure, chord_scale, harm_interest=.1))

    a_prime_inversions = voicelead_chords(a_prime_chords, voicelead_rand=0.6)
    a_prime_chords = invert_chords(a_prime_chords, a_prime_inversions)
    # start times
    start_time = 0
    b_start_time = melody_length * 60 / tempo
    a_prime_start_time = b_start_time + b_melody_length * 60 / tempo

    ### COMPOSE ###
    melody_seq = musx.Seq()
    score = musx.Score(out=melody_seq)
    if has_pickup:
        start_time = (time_sig[0] * 4 /
                      time_sig[1]) * (60 / tempo)
    score.compose([[0, melody_composer(score, melody, tempo, chan=0)],
                   [start_time, chordal_composer(
                       score, chords, inversions, tempo, time_sig, rhy_interest=0, chan=3)],
                   [start_time, bass_composer(
                       score, chords, tempo, time_sig, chan=5)],
                   [start_time, melody_composer(
                       score, countermelody, tempo, lokey=81, hikey=108, chan=4)],
                   [b_start_time, melody_composer(
                       score, b_melody, tempo, chan=1)],
                   [b_start_time, chordal_composer(
                       score, b_chords, inversions, tempo, time_sig, rhy_interest=0, chan=2)],
                   [b_start_time, bass_composer(
                       score, b_chords, tempo, time_sig, chan=5)],
                   [a_prime_start_time, melody_composer(
                       score, a_prime_melody, tempo, chan=0)],
                   [a_prime_start_time, chordal_composer(
                       score, a_prime_chords, a_prime_inversions, tempo, time_sig, rhy_interest=.3, chan=3)],
                   [a_prime_start_time,
                       bass_composer(score, a_prime_chords, tempo, time_sig, chan=5)]
                   ])
    pp.pprint(chords)
    pp.pprint(b_chords)
    pp.pprint(a_prime_chords)
    play_midi(melody_seq, ableton_midiout, block=True)

    # harmony_seq.print()
    # while True:
    #     hardpad_midiout.send_message(musx.note_on(144, 60, 100))
    #     time.sleep(1)
    #     hardpad_midiout.send_message(musx.note_off(128, 60, 0))
    #     time.sleep(1)
    #     pass
