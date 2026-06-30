"""
Smoke test voor findatapy met Dukascopy bron.

Doel: ontdekken
- werkt de Dukascopy source voor tick data?
- welke kolommen/format levert het?
- wat is de timestamp-conventie?
- hoeveel rijen per dag?
"""
import sys
import time

t0 = time.time()
print("Initialiseren Market...", flush=True)
from findatapy.market import Market, MarketDataRequest

market = Market(market_data_generator=None)

md_request = MarketDataRequest(
    start_date="02 Jan 2020",
    finish_date="03 Jan 2020",
    category="fx",
    fields=["bid", "ask", "bidv", "askv"],
    freq="tick",
    data_source="dukascopy",
    tickers=["EURUSD"],
)

print("Download start (Dukascopy, EURUSD, 2020-01-02, tick)...", flush=True)
df = market.fetch_market(md_request)

elapsed = time.time() - t0
print(f"\nKlaar in {elapsed:.1f}s")
print(f"DataFrame shape: {df.shape}")
print(f"Index name: {df.index.name}, dtype: {df.index.dtype}")
print(f"Kolommen: {list(df.columns)}")
print(f"Index range: {df.index.min()}  ..  {df.index.max()}")
print()
print("Eerste 5 rijen:")
print(df.head())
print()
print("Laatste 5 rijen:")
print(df.tail())
print()
print("dtypes:")
print(df.dtypes)
print()
print("Stats (numeriek):")
print(df.describe())