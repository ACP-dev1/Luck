"""Diagnostik til timing luck-papiret: positionsoverlap og drawdown pr. episode."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np, pandas as pd
from analyse import indlaes, regimescore, koer

EPISODER = {
    "2008 (okt 2007 - mar 2009)": ("2007-10-01", "2009-03-31"),
    "COVID (feb - apr 2020)":     ("2020-02-01", "2020-04-30"),
    "2022 (jan - okt 2022)":      ("2022-01-01", "2022-10-31"),
}


def positioner(p, score, handelsdag, graense=2):
    dag = p.groupby([p.index.year, p.index.month]).cumcount() + 1
    rebal = (dag == handelsdag).values
    pos = pd.Series(np.nan, index=p.index)
    pos[rebal] = np.where(score[rebal] >= graense, 1.0, 0.0)
    return pos.ffill().shift(1)


def drawdown(x):
    k = x.cumsum()
    return (k - k.cummax()).min()


if __name__ == "__main__":
    p, m = indlaes()
    score = regimescore(p, m)

    # 1. Hvor ofte holder to varianter samme position?
    P = pd.DataFrame({k: positioner(p, score, k) for k in range(1, 22)}).dropna()
    par = [(P[a] == P[b]).mean() for a in P for b in P if a < b]
    print(f"gennemsnitligt positionsoverlap mellem to varianter: {np.mean(par):.3f}")
    print(f"laveste overlap mellem to varianter:                 {min(par):.3f}\n")

    # 2. Antal regimeskift pr. variant
    skift = P.diff().abs().sum()
    print(f"regimeskift over perioden: min {skift.min():.0f}, "
          f"median {skift.median():.0f}, max {skift.max():.0f}\n")

    # 3. Drawdown pr. episode, paa tvaers af de 21 varianter
    afkast = {k: koer(p, score, k) for k in range(1, 22)}
    passiv = np.log(p["offensiv"]).diff().dropna()

    raekker = []
    for navn, (start, slut) in EPISODER.items():
        dd = [drawdown(x.loc[start:slut]) for x in afkast.values()]
        raekker.append(dict(episode=navn,
                            dd_min=min(dd), dd_median=float(np.median(dd)),
                            dd_max=max(dd), spredning=float(np.std(dd)),
                            passiv=drawdown(passiv.loc[start:slut])))
    T = pd.DataFrame(raekker).set_index("episode")
    print(T.round(3))
    T.to_csv("output/drawdown_pr_episode.csv")
