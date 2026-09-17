"""Timing luck: samme regimestrategi paa 21 forskellige rebalanceringsdage."""
import numpy as np, pandas as pd

PRISER = "data/raw/priser.csv"   # kolonner: dato, offensiv, defensiv
MAKRO  = "data/raw/makro.csv"    # kolonner: dato, kurve_haeldning, arbejdsloeshed


def indlaes():
    p = pd.read_csv(PRISER, parse_dates=["dato"]).set_index("dato").sort_index()
    m = pd.read_csv(MAKRO, parse_dates=["dato"]).set_index("dato").sort_index()
    m = m[~m.index.duplicated(keep="last")]

    # Kurvehaeldningen er markedsdata og kendes samme dag.
    kurve = m["kurve_haeldning"].dropna()

    # Arbejdsloesheden offentliggoeres foerst maaneden efter referencemaaneden,
    # saa datoen skubbes frem for at undgaa lookahead.
    arbejds = m["arbejdsloeshed"].dropna()
    arbejds.index = arbejds.index + pd.DateOffset(months=1)
    arbejds = arbejds[~arbejds.index.duplicated(keep="last")].sort_index()

    ud = pd.DataFrame(index=p.index)
    ud["kurve_haeldning"] = kurve.reindex(p.index, method="ffill")
    ud["arbejdsloeshed"] = arbejds.reindex(p.index, method="ffill")
    return p, ud


def regimescore(p, m):
    s1 = (m["kurve_haeldning"] > 0).astype(int)
    s2 = (m["arbejdsloeshed"].diff(252) < 0).astype(int)
    s3 = (p["offensiv"] > p["offensiv"].rolling(200).mean()).astype(int)
    return (s1 + s2 + s3).rename("score")


def koer(p, score, handelsdag, graense=2):
    r = np.log(p).diff()
    dag_i_maaned = p.groupby([p.index.year, p.index.month]).cumcount() + 1
    rebal = (dag_i_maaned == handelsdag).values

    pos = pd.Series(np.nan, index=p.index)
    pos[rebal] = np.where(score[rebal] >= graense, 1.0, 0.0)
    pos = pos.ffill().shift(1)

    return (pos * r["offensiv"] + (1 - pos) * r["defensiv"]).dropna()


def noegletal(x):
    kurve = x.cumsum()
    return dict(sharpe=x.mean() / x.std() * np.sqrt(252),
                drawdown=(kurve - kurve.cummax()).min(),
                aarligt=x.mean() * 252)


if __name__ == "__main__":
    p, m = indlaes()
    score = regimescore(p, m)

    ud = {k: noegletal(koer(p, score, k)) for k in range(1, 22)}
    T = pd.DataFrame(ud).T
    T.index.name = "handelsdag"
    print(T.round(3), "\n")
    print(T.agg(["min", "median", "max", "std"]).round(3), "\n")

    # Sammenligning: passiv offensiv position hele perioden
    passiv = np.log(p["offensiv"]).diff().dropna()
    print("passiv benchmark:", {k: round(v, 3) for k, v in noegletal(passiv).items()})

    T.to_csv("output/timing_luck.csv")
