import pythonosc.udp_client
import threading, time
import musx

# Support for sending OSC messages in realtime.

class OscMessage(musx.Event):
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
        self.data = [*data]
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


## Add your code here!

        
if __name__ == '__main__':
    print('Hiho!')
