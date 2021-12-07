import sys
from musx.midi.midievent import MidiEvent
from musx.midi.midimsg import note_on, note_off
import threading
import musx
import time


def play_midi(seq, port, block=True):
    """
    Plays a Note or MidiEvent sequence out an open rtmidi output port. If
    the sequence contains notes they are first converted into midi events
    before playback.
      
    Parameters
    ----------
    seq : Seq
        A sequence of Note or MidiEvent objects.
    port : rtmidi.MidiOut
        An open rtmidi MidiOut object.
    block : bool
        If true then midi_play() will block for the duration of the playback.
    """
    if not seq.events:
        raise ValueError(f"no midi events to play")
    if not 'rtmidi' in sys.modules:
        raise RuntimeError(f"module rtmidi is not loaded")
    if not isinstance(port, sys.modules['rtmidi'].MidiOut):
        raise TypeError(f"port is not an instance of rtmidi.MidiOut")
    if isinstance(seq[0], musx.Note):
        seq = _notes_to_midi(seq)
    player = threading.Thread(target=_midi_player, args=(seq.events, port))#, daemon=True
    # start the playback
    player.start()
    if block:
        # wait until playback is complete before returning from function
        player.join()


def _notes_to_midi(seq):
    """
    Converts a sequence of notes into a sequence of time-ordered midi messages.
    
    Parameters
    ----------
    seq : Seq
        A sequence containing Note objects.
    """
    midi = musx.Seq()
    for note in seq:
        key = int(note.pitch if isinstance( note.pitch, (int, float)) else note.pitch.keynum())
        vel = int(note.amplitude * 127)
        chan = note.instrument
        on  = MidiEvent(note_on(chan, key, vel), note.time)
        off = MidiEvent(note_off(chan, key, 127), note.time + note.duration)
        midi.add(on)
        midi.add(off)
    return midi

        
def _midi_player(midi, port):
    """
    Thread function that plays a list of midi messages out the port.

    Parameters
    ----------
    midi : list
        A time sorted list of MidiEvent objects
    port : rtmidi.Port
        An open rtmidi output port.
    """
    length = len(midi)
    # get time of next message
    nexttime = midi[0].time
    thistime = nexttime
    i = 0
    while i < length:
        if midi[i].time == thistime:
            #print(f'playing {seq[i]}')
            port.send_message(midi[i].message)
            i += 1
            continue
        # if here then sleep because midi[i] is later than thistime
        nexttime = midi[i].time
        #print(f'waiting {nexttime-thistime}')
        time.sleep(nexttime - thistime) 
        thistime = nexttime