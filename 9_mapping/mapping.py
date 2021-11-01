from musx.midi import gm
import requests
import pandas as pd
import matplotlib.pyplot as plt
from musx import Seq, Score, MidiFile, Note, rescale, interp
import argparse
# Idea: look at the stock market and flag patterns? Maybe have it be fractal in some way
# Make some melodies by quantzing to the nearest _
# Make some harmonies by accessing tickers and such
# API to grab stock info
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
LYDIAN_SCALE = [0, 2, 4, 6, 7, 9, 11]
MIXO_SCALE = [0, 2, 4, 6, 7, 9, 10]

def get_ticker(symbol):
    # Ok this api is bad, its wrong but the musical part still works well
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey=YVQ7A0RO2S5WP0D9'
    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame(data["Weekly Time Series"])
    df = df.T
    df.index.name = "Date"
    df.reset_index(inplace=True)
    df.pop("1. open")
    df.pop("2. high")
    df.pop("3. low")
    df.pop("5. volume")
    df["4. close"] = pd.to_numeric(df["4. close"])
    return df.iloc[::-1]


def stock_composer(score, ticker, numweeks, scale, lowk=48, hik=90, dur=0.5, chan=0):
    df = get_ticker(ticker)
    # Gets the last (numweeks) weeks of closing price of the stock
    data = df["4. close"][-numweeks:]
    datamax = max(data)
    datamin = min(data)
    # rescale data into scale
    for p in data:
        keynum = rescale(p, datamin, datamax, lowk, hik)
        
        # if not len(scale) == 0: maybe have a choice for microtonal things?
        keynum = quantize_to_scale(keynum, lowk, scale)
        # scale amplitude as well
        amp = rescale(p, datamin, datamax, 0.2, 0.9)
        # TODO: rescale notes into a lydian (or other) scale
        note = Note(score.now, duration=dur, pitch=keynum,
                    amplitude=amp, instrument=chan)
        score.add(note)
        yield dur

def quantize_to_scale(keynum, root, scale):
    
    difference = keynum - root
    div, mod = divmod(difference, 12)
    quantize = take_closest(scale, mod)
    quan_diff = quantize - mod
    return keynum + quan_diff

# Code from stack overflow but I ran out of time so I'm using it
# By Lauritz V. Thaulow, runs in O(logn) time because sorted
from bisect import bisect_left

def take_closest(myList, myNumber):
    """
    Assumes myList(scale list) is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
        return after
    else:
        return before

if __name__ == "__main__":
    parser = argparse.ArgumentParser("create music out of stocks")
    parser.add_argument('tickers', metavar='T', default='AAPL',
                        nargs='+', help='A list of stock tickers')
    args = parser.parse_args()

    seq = Seq()
    score = Score(out=seq)
    meta = MidiFile.metatrack(ins={0: gm.Celesta, 1: gm.ElectricPiano1, 2: gm.ElectricPiano2, 3: gm.FX1_rain, 4: gm.FX3_crystal})
    for i, ticker in enumerate(args.tickers):
        score.compose([0, stock_composer(score, ticker, 100, LYDIAN_SCALE, dur=0.25, chan=i)])
    MidiFile("mapping.mid", [meta, seq]).write()
    seq.print()
