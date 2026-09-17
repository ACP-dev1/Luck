from hent import yahoo, gem

# Offensiv: bredt aktieindeks. Defensiv: korte statsobligationer.
TICKERS = ["SPY", "SHY"]

if __name__ == "__main__":
    df = yahoo(TICKERS, start="2003-01-01")   # SHY noteret fra juli 2002
    df = df.rename(columns={"spy": "offensiv", "shy": "defensiv"}).dropna()
    gem(df, "priser.csv")
