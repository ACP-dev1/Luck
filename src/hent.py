"""Faelles hentefunktioner. Koeres foer analyse.py."""
import io, os
import pandas as pd
import requests

os.makedirs("data/raw", exist_ok=True)


def fred(serie):
    """Henter en FRED-serie som DataFrame. Ingen API-noegle noedvendig."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={serie}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = ["dato", serie]
    df["dato"] = pd.to_datetime(df["dato"])
    df[serie] = pd.to_numeric(df[serie], errors="coerce")
    return df.dropna()


def yahoo(tickers, start="1990-01-01"):
    """Daglige lukkekurser, udbyttejusterede, for en liste af tickers.

    Erstatter den tidligere stooq-funktion, som svarer 404 paa kald uden
    browser-header. yfinance haandterer det selv og henter alle tickers i
    ét kald.
    """
    import yfinance as yf
    data = yf.download(tickers, start=start, auto_adjust=True,
                       progress=False, group_by="column")
    luk = data["Close"] if "Close" in data else data
    if isinstance(luk, pd.Series):
        luk = luk.to_frame(tickers if isinstance(tickers, str) else tickers[0])
    luk = luk.reset_index()
    luk.columns = ["dato"] + [str(c).lower() for c in luk.columns[1:]]
    luk["dato"] = pd.to_datetime(luk["dato"])
    manglende = [t for t in tickers if t.lower() not in luk.columns]
    if manglende:
        print("advarsel: ingen data for", manglende)
    return luk


def statistikbank(tabel, forespoergsel):
    """Nationalbankens statistikbank (PxWeb).

    OBS: verificer tabelkode og variabelnavne i browseren foerst --- aabn
    https://nationalbanken.statistikbank.dk/<TABEL>, vaelg dine serier, og
    brug 'API'-knappen til at faa den praecise forespoergsel.
    """
    url = f"https://nationalbanken.statistikbank.dk/api/v1/da/{tabel}"
    r = requests.post(url, json=forespoergsel, timeout=90)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text), sep=";")


def gem(df, filnavn):
    sti = os.path.join("data/raw", filnavn)
    df.to_csv(sti, index=False)
    print(f"gemte {sti}  ({len(df)} raekker, "
          f"{df['dato'].min().date()} til {df['dato'].max().date()})")
