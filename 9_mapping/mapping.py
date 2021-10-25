from musx.midi import gm
import requests
import pandas as pd
import matplotlib.pyplot as plt
from musx import Seq, Score, MidiFile, Note, rescale
import argparse
# Idea: look at the stock market and flag patterns? Maybe have it be fractal in some way
# Make some melodies by quantzing to the nearest _
# Make some harmonies by accessing tickers and such
# API to grab stock info
# Ok this api is bad, its wrong but the musical part still works well


def get_ticker(symbol):
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


def stock_composer(score, ticker, numweeks, lowk=48, hik=90, dur=0.5, amp=0.5, chan=0):
    df = get_ticker(ticker)
    # Gets the last (numweeks) weeks of closing price of the stock
    data = df["4. close"][-numweeks:]
    datamax = max(data)
    datamin = min(data)
    # rescale data into scale
    for p in data:
        keynum = rescale(p, datamin, datamax, lowk, hik)
        # TODO: rescale notes into a lydian (or other) scale
        note = Note(score.now, duration=dur, pitch=keynum,
                    amplitude=amp, instrument=chan)
        score.add(note)
        yield dur


if __name__ == "__main__":
    parser = argparse.ArgumentParser("create music out of stocks")
    parser.add_argument('tickers', metavar='T', default='AAPL',
                        nargs='+', help='A list of stock tickers')
    args = parser.parse_args()

    seq = Seq()
    score = Score(out=seq)
    meta = MidiFile.metatrack(ins={0: gm.Celesta})
    for ticker in args.tickers:
        score.compose([0, stock_composer(score, ticker, 100)])
    MidiFile("mapping_2.mid", [meta, seq]).write()
    seq.print()
