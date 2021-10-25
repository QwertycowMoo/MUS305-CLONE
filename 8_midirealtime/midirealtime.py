import rtmidi
import musx
import time
import threading
import argparse


midiout = rtmidi.MidiOut()
outports = midiout.get_ports()
midiin = rtmidi.MidiIn()
inports = midiin.get_ports()
waittime = 2
print("available output ports:", outports)
print("available input ports:", inports)

midiout.open_port(outports.index("mio 1"))
# midiout.open_port(outports.index("AbletonIn 1"))
midiin.open_port(inports.index("mio 0"))
# midiin.open_port(inports.index("MK-249C USB MIDI keyboard 2")) 



def midi_callback(message, data):
    rootmsg = message[0]
    if rootmsg[0] == 144:
        midiout.send_message(musx.note_on(rootmsg[0], rootmsg[1], rootmsg[2]))
    elif rootmsg[0] == 128:
        midiout.send_message(musx.note_off(rootmsg[0], rootmsg[1], rootmsg[2]))
    replay = threading.Thread(target=resend_midi, args=(rootmsg, waittime))
    replay.start()

def resend_midi(msg, waittime):
    # Assumes that threading is already started
    time.sleep(waittime)
    if msg[0] == 144:
        midiout.send_message(musx.note_on(msg[0], msg[1], msg[2]))
    elif msg[0] == 128:
        time.sleep(0.3)
        midiout.send_message(musx.note_off(msg[0], msg[1], msg[2]))

midiin.set_callback(midi_callback)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="set bpm and measure length")
    parser.add_argument('--bpm', type=int, help='beats per minute', default=120)
    parser.add_argument('--measures', type=int, help="number of measures before repeat", default=2)
    parser.add_argument('--tstop', type=int, help="top number of time signature", default=4)
    args = parser.parse_args()
    print(args)
    bps = args.bpm / float(60)
    num_beats = args.measures * args.tstop
    waittime = num_beats / bps
    print(waittime)
    while True:
        pass