import musx

def melody_composer(score, melody, tempo, lokey=60, hikey=84, transpose_key=0, chan=0):
    """
    Expects a measure that has a tuple of (keynum, length_in_quarternotes)
    Composes the melody within the [lokey, hikey] range. Will eventually transpose the key to create a different section
    tempo is in bpm
    Don't put the lokey or hikey to be a very small range, recommend 2 octaves
    """
    quarter_note_length = 60 / tempo

    for note in melody:
        pitch = note[0]
        length = note[1] * quarter_note_length
        if pitch == -1:
            yield length
            continue
        while pitch < lokey:
            pitch += 12
        while pitch > hikey:
            pitch -= 12

        # Makes the higher notes slightly louder
        amp = musx.rescale(pitch, lokey, hikey, 0.3, 0.7, 'exp') + .2
        note = musx.Note(score.now, duration=length, pitch=pitch,
                         amplitude=amp, instrument=chan)
        score.add(note)
        yield length


def chordal_composer(score, chords, inversions, tempo, time_sig, rhy_interest=0, chan=0):
    """


    Args:
        score ([type]): [description]
        chords ([type]): List of list of Pitch objects
        inversions ([type]): List of inversion, parallel to chords
        tempo ([type]): bpm
        has_pickup(boolean): whether the first chord should be just nothing
        lokey (int, optional): [description]. Defaults to 36.
        hikey (int, optional): [description]. Defaults to 60.
        transpose_key (int, optional): [description]. Defaults to 0.
        chan (int, optional): [description]. Defaults to 0.

    Yields:
        [type]: [description]
    """
    quarter_note_length = 60 / tempo
    measure_length = time_sig[0] * 4 / time_sig[1]
    length = measure_length * quarter_note_length

    rhythmic_addon = 0
    for chord in chords:

        # Reset length if rhythmic interest was added
        if rhythmic_addon != 0:
            length -= rhythmic_addon
            rhythmic_addon = 0

        # Makes the inversions slightly softer
        inversion = inversions[chords.index(chord)]
        amp = musx.rescale(inversion, 0, 3, 0.5, 0.7, 'exp') + .2
        # Create rhythmic interest by delaying or anticipating the next chord slightly
        if musx.odds(rhy_interest):
            if musx.odds(.5):
                # delay next chord by adding an extra eighth note
                rhythmic_addon = .5 * quarter_note_length
                length += .5 * quarter_note_length
            else:
                # anticipate next chord by note reducing length of this chord by eighth note
                rhythmic_addon = -.5 * quarter_note_length
                length -= .5 * quarter_note_length

        for note in chord:
            pitch = note.keynum()
            note = musx.Note(score.now, duration=length, pitch=pitch,
                             amplitude=amp, instrument=chan)
            score.add(note)
        yield length


def bass_composer(score, chords, tempo, time_sig, amp=0.7, lokey=28, hikey=48, chan=5):
    quarter_note_length = 60 / tempo
    measure_length = time_sig[0] * 4 / time_sig[1]
    length = measure_length * quarter_note_length
    
    for chord in chords:
        # find the lowest note in the chord
        # TODO: Add some excitement to the bass
        basspitch = None
        for pitch in chord:
            if basspitch is None :
                basspitch = pitch
            if pitch.keynum() < basspitch.keynum():
                basspitch = pitch
        keynum = basspitch.keynum()
        while keynum < lokey:
            keynum += 12
        while keynum > hikey:
            keynum -= 12
        note = musx.Note(score.now, duration=length, pitch=keynum,
                            amplitude=amp, instrument=chan)
        score.add(note)
        yield length
