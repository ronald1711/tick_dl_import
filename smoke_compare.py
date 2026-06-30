"""
Vergelijking rooktest-output met bestaande EURUSD 2020-data formaat.
Welke harmonisatie is nodig om consistent te zijn met 2004-2019 data?
"""
import pandas as pd
import sys

# Lees bestaande 2019 EURUSD als referentie
print("=== Bestaand formaat (EURUSD 2019 eerste 5 rijen) ===")
df_old = pd.read_csv(
    r"C:\projecten\forexdata\EURUSD\EURUSD_tick_UTC+0_00_2019-Parse.csv",
    nrows=5,
)
print(df_old.to_string())
print()

# Nu rooktest-output herschrijven naar een zelfde-vormige CSV
# (bid en ask omwisselen om de oude swap-conventie te matchen)
print("=== Herschreven naar 'swap-conventie' (kolommen Ask/Bid omgedraaid) ===")
print("URS.bid   -> BidPrice (oude 'AskPrice' kolom)")
print("EURUSD.ask -> AskPrice (oude 'BidPrice' kolom)")
print()

# We gebruiken de in-memory DataFrame van findatapy niet hier;
# laat de smoke test een kleine CSV uitschrijven
# maar in dit geval herschrijven we alleen fictief om te tonen
print("Voorbeeld herschreven rij:")
print("UTC,AskPrice,BidPrice,AskVolume,BidVolume")
print("2020-01-02T00:00:01.022+00:00,1.12189,1.12188,0.94,2.25")
print()
print("Let op: findatapy levert bid/ask SCHOON (ask > bid).")
print("Bestaande data heeft kolommen SWAPPED. Om consistent te zijn met")
print("oude bestanden moeten we bij het wegschrijven bid en ask omwisselen,")
print("of anders de oude data opruimen. Eerstgenoemde is minste werk.")