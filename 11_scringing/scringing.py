from typing import List
import pythonosc.udp_client
import threading
import time
from musx import Score, Seq, Event, hertz


# Support for sending OSC messages in realtime.

class OscMessage(Event):
    """
    A class to represent OSC messages.

    Parameters
    ----------
    addr : string
        An OSC address (a string identifier starting with '/', for example "/musx").
    time : float | int
        The start time of the event.
    *data : variadic args
        A sequence of zero or more values that constitute the message's data.
    """

    def __init__(self, addr, time, *data):
        super().__init__(time)
        self.addr = addr
        self.data = [time, *data]

    def __str__(self):
        return f"<OscMessage: '{self.addr}' {self.data} {hex(id(self))}>"
    __repr__ = __str__


def oscplayer(oscseq, oscout):
    """
    Send OSC messages in real time from a thread.

    Parameters
    ----------
    oscseq : Seq
        A Seq containing a time sorted list of OscMessages.
    oscport : pythonosc.udp_client.SimpleUDPClient
        An open OSC output port.
    """
    messages = oscseq.events
    length = len(messages)
    thistime = messages[0].time
    nexttime = thistime
    i = 0
    while i < length:
        if messages[i].time == thistime:
            #print(f'playing {messages[i]}')
            oscout.send_message(messages[i].addr, messages[i].data)
            i += 1
            continue
        # if here then midi[i] is later than thistime so sleep
        nexttime = messages[i].time
        #print(f'waiting {nexttime-thistime}')
        time.sleep(nexttime - thistime)
        thistime = nexttime


# Add your code here!
def gong_test(score, chords: List[List[int]], chord_repeat: int, base_quarter_note):
    # Takes the minimum of chords * chord_repeat or measures
    # Expects the first note to be long
    # Compass by Disasterpeace as the inspiration
    # Take any chord >2 notes, fit it to that kind of rhythm
    # First note is 1.5 beats
    # Slide up is .5
    # Arrival note is at 2 beats
    # climb downwards equally all notes until arrival of the the next chord
    # Its in 3/2 so subdivide
    for chord in chords:
        
        for i in range(chord_repeat):
            score_time = 0
            root = OscMessage("/musx", score.now, 1.7 *
                              base_quarter_note, chord[0], .7)
            score_time += 1.7 * base_quarter_note
            score.add(root)
            # run up to top of chord
            for note in chord[1:-1]:
                note_length = (.3 * base_quarter_note) / (len(chord) - 1)
                run_note = OscMessage(
                    "/musx", score.now + score_time, note_length, note, .5)
                score.add(run_note)
                score_time += note_length
            # walk down chord
            for note in chord[-1:1:-1]:
                note_length = (4 * base_quarter_note) / (len(chord) - 1)
                walk_note = OscMessage(
                    "/musx", score.now + score_time, note_length, note, .65)
                score.add(walk_note)
                score_time += note_length
            print(score_time)
            yield score_time


if __name__ == '__main__':
    oscout = pythonosc.udp_client.SimpleUDPClient("127.0.0.1", 57120)
    oscseq = Seq()
    score = Score(out=oscseq)
    chords = [hertz([48, 60, 64, 67, 71, 74]), hertz([48, 60, 62, 64, 67, 71])]

    score.compose(gong_test(score, chords, 2, .7))
    player = threading.Thread(target=oscplayer, args=(oscseq, oscout))
    print(oscseq)
    player.start()
