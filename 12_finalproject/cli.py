import argparse
import musx

def parseargs():
    def timesig(s):
        # Custom tuple type for argparse
        try:
            top, bottom = map(int, s.split("/"))
            return (top, bottom)
        except:
            raise argparse.ArgumentTypeError("Time Signature must be top/bottom")
    

    parser = argparse.ArgumentParser("Create a composition from a melody")
    # TODO: Specify which params are required
    parser.add_argument("--random", type=bool, default=False, help="Randomizes all parameters")
    parser.add_argument("--scale", type=int, default=0, help="scale type, either 0, 1, 2 for Major, Minor, Lydian")
    parser.add_argument("--timesig", type=timesig, default="4/4", help="time signature, in form top/bottom")
    parser.add_argument("--tempo", type=int, default="120", help="tempo of the composition")
    parser.add_argument("--key", type=int, default=0, help="key of the melody, in number of sharps")
    parser.add_argument("--pickup", type=bool, default=False, help="Whether the melody has a pickup")
    parser.add_argument("--a_harm", type=float, default=0.2, help="A section harmonic interest, how 'correct' chords are")
    parser.add_argument("--a_vlead", type=float, default=0.2, help="A section voiceleading randomness, jumping of chords")
    parser.add_argument("--a_cmelnum", type=int, default=0, help="number of notes in countermelody, 0 means no countermelody")
    parser.add_argument("--a_cmelhi", type=int, default=108, help="Highest key number in A section countermelody")
    parser.add_argument("--a_cmello", type=int, default=81, help="Lowest key number in A section countermelody")
    parser.add_argument("--a_rhy", type=float, default=0.2, help="A section rhythmic interest, how often chords fall on offbeats")
    parser.add_argument("--a_hi", type=int, default=84, help="Highest key number in A section")
    parser.add_argument("--a_lo", type=int, default=60, help="Lowest key number in A section")
    parser.add_argument("--a_melchan", type=int, default=0, help="A section melody midi channel")
    parser.add_argument("--a_harmchan", type=int, default=3, help="A section harm midi channel")
    parser.add_argument("--a_cntchan", type=int, default=4, help="A section countermelody midi channel")
    
    parser.add_argument("--b_len", type=int, default=-1, help="B Section length in measures, -1 is half of A melody length")
    parser.add_argument("--b_sim", type=int, default=1, help="B Section similarity to A, markov order")
    parser.add_argument("--b_slow", type=float, default=0.3, help="B Section melody slowdown, rhythmic interest for melody")
    parser.add_argument("--b_trans", type=int, default=-7, help="B Section transposition in semitones. Defaults to a fifth down")
    parser.add_argument("--b_key", type=int, default=100, help="B Section key, in number of sharps. Defaults to a fifth down, 100 as flag value")
    parser.add_argument("--b_harm", type=float, default=0.2, help="B section harmonic interest, how 'correct' chords are")
    parser.add_argument("--b_vlead", type=float, default=0.2, help="B section voiceleading randomness, jumping of chords")
    parser.add_argument("--b_cmelnum", type=int, default=0, help="number of notes in B countermelody, 0 means no countermelody")
    parser.add_argument("--b_cmelhi", type=int, default=115, help="Highest key number in B section countermelody")
    parser.add_argument("--b_cmello", type=int, default=88, help="Lowest key number in B section countermelody")
    parser.add_argument("--b_rhy", type=float, default=0.2, help="B section rhythmic interest, how often chords fall on offbeats")
    parser.add_argument("--b_hi", type=int, default=79, help="Highest key number in B section")
    parser.add_argument("--b_lo", type=int, default=52, help="Lowest key number in B section")
    parser.add_argument("--b_melchan", type=int, default=1, help="B section melody midi channel")
    parser.add_argument("--b_harmchan", type=int, default=2, help="B section harm midi channel")
    parser.add_argument("--b_cntchan", type=int, default=4, help="B section countermelody midi channel")
    
    parser.add_argument("--ap_harm", type=float, default=0.2, help="A' section harmonic interest, how 'correct' chords are")
    parser.add_argument("--ap_vlead", type=float, default=0.4, help="A section voiceleading randomness, jumping of chords")
    parser.add_argument("--ap_cmelnum", type=int, default=2, help="number of notes in countermelody, 0 means no countermelody")
    parser.add_argument("--ap_cmelhi", type=int, default=108, help="Highest key number in A' section countermelody")
    parser.add_argument("--ap_cmello", type=int, default=81, help="Lowest key number in A' section countermelody")
    parser.add_argument("--ap_rhy", type=float, default=0.2, help="A' section rhythmic interest, how often chords fall on offbeats")
    parser.add_argument("--ap_hi", type=int, default=84, help="Highest key number in A' section")
    parser.add_argument("--ap_lo", type=int, default=60, help="Lowest key number in A' section")
    parser.add_argument("--ap_melchan", type=int, default=0, help="A' section melody midi channel")
    parser.add_argument("--ap_harmchan", type=int, default=3, help="A' section harm midi channel")
    parser.add_argument("--ap_cntchan", type=int, default=4, help="A' section countermelody midi channel")
    
    args = parser.parse_args()
    if args.random:
        args.scale = musx.between(0, 3)
        args.tempo = musx.between(40, 200)
        args.a_harm = musx.lowran()
        args.a_vlead = musx.lowran()
        args.a_cmelnum = musx.between(0, 12)
        args.a_rhy = musx.lowran()
        args.a_melchan = musx.pick(0, 1)
        args.a_harmchan = musx.pick(2, 3)
        
        args.b_len = musx.between(1, 16)
        args.b_sim = musx.between(0, 8)
        args.b_slow = musx.lowran()
        args.b_trans = -4 #musx.between(-7, 7)
        # TODO: find out b key based on transposition
        transpose = args.b_trans
        if transpose < 0:
            transpose = 12 + transpose
            
        fifths = 0
        sharps = 0
        while fifths != transpose:
            fifths = (fifths + 7) % 12
            sharps += 1
        args.b_key = args.key + sharps
        if args.b_key > 7:
            args.b_key = args.b_key - 12

        args.b_harm = musx.lowran()
        args.b_vlead = musx.lowran()
        args.b_cmelnum = musx.between(0, 12)
        args.b_rhy = musx.lowran()
        args.b_melchan = musx.pick(0, 1)
        args.b_harmchan = musx.pick(2, 3)
        
        args.ap_harm = musx.lowran()
        args.ap_vlead = musx.lowran()
        args.ap_cmelnum = musx.between(0, 12)
        args.ap_rhy = musx.lowran()
        args.ap_melchan = musx.pick(0, 1)
        args.ap_harmchan = musx.pick(2, 3)
        
    print(args)
    return args