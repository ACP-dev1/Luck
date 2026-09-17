from hent import fred, gem
import pandas as pd

SERIER = ["T10Y2Y", "UNRATE"]

if __name__ == "__main__":
    dele = [fred(s) for s in SERIER]
    df = dele[0]
    for d in dele[1:]:
        df = df.merge(d, on="dato", how="outer")
    df = df.sort_values("dato")
    df.columns = ["dato"] + ["kurve_haeldning", "arbejdsloeshed"]
    gem(df, "makro.csv")
