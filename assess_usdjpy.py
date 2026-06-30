"""
USDJPY Tick Data Quality Assessment

Doet een 1M-rij steekproef per jaarbestand, net als de EURUSD-assessment,
en berekent:
- sortering
- kolomverwisseling (Ask hoort > Bid te zijn)
- spread stats (in pips; USDJPY: 1 pip = 0.01 voor 3-decimaal, 0.001 voor 5-decimaal)
- extreme prijssprongen
- tijdgaten > 1 minuut
- zero-volume ticks

Schrijft resultaten naar USDJPY_quality_results.csv
"""
import pandas as pd
import glob
import os
import sys
from datetime import datetime

CSV_DIR = r"C:\projecten\forexdata\USDJPY"
SAMPLE_SIZE = 1_000_000  # eerste N rijen per jaar, conform EURUSD-aanpak
PIP_THRESHOLD_LARGE = 10.0  # pips
PRICE_JUMP_THRESHOLD_PIPS = 30.0  # meldingsdrempel voor "grote" sprongen

results = []
files = sorted(glob.glob(os.path.join(CSV_DIR, "*.csv")))
if not files:
    print(f"Geen CSV-bestanden gevonden in {CSV_DIR}")
    sys.exit(1)

print(f"{len(files)} bestanden gevonden. Start analyse...")
print(f"{'='*100}")

for f in files:
    year = os.path.basename(f).split("_")[-1].split("-")[0]
    print(f"\n>> Verwerken {os.path.basename(f)} ...")
    try:
        # Alleen de eerste SAMPLE_SIZE rijen inlezen; scheelt enorm bij 2GB+ bestanden
        df = pd.read_csv(
            f,
            nrows=SAMPLE_SIZE,
            dtype={
                "AskPrice": "float64",
                "BidPrice": "float64",
                "AskVolume": "float64",
                "BidVolume": "float64",
            },
            low_memory=False,
        )
    except Exception as e:
        print(f"   ! Fout bij inlezen: {e}")
        continue

    n_rows = len(df)

    # Tijdstempel parsen
    df["_ts"] = pd.to_datetime(df["UTC"], utc=True, errors="coerce")
    df = df.dropna(subset=["_ts", "AskPrice", "BidPrice"])

    # Check kolomverwisseling: als AskPrice in de header,
    # dan moet het ECHTE ask-prijs zijn (dus > BidPrice).
    # In de EURUSD-data bleek dit omgewisseld. Hetzelfde check hier.
    raw_ask_gt_bid = (df["AskPrice"] > df["BidPrice"]).sum()
    raw_ask_lt_bid = (df["AskPrice"] < df["BidPrice"]).sum()
    swapped = raw_ask_lt_bid > raw_ask_gt_bid  # als meer rijen Ask < Bid, dan zijn kolommen verwisseld

    # Werk met de "effectieve" kolommen
    if swapped:
        bid = df["AskPrice"].values  # eerste kolom gedraagt zich als Bid
        ask = df["BidPrice"].values  # tweede kolom gedraagt zich als Ask
        bid_vol = df["AskVolume"].values
        ask_vol = df["BidVolume"].values
    else:
        bid = df["BidPrice"].values
        ask = df["AskPrice"].values
        bid_vol = df["BidVolume"].values
        ask_vol = df["AskVolume"].values

    spread = ask - bid  # altijd >= 0 als Ask > Bid

    # USDJPY forex-conventie: 1 pip = 0.01 (3 decimalen).
    # De data bevat 5-decimale precisie, dus een spread van 0.010 wordt gerapporteerd
    # als 1.0 pip. We gebruiken vaste pip=0.01 voor consistentie met forex-conventie.
    pip = 0.01

    spread_pips = spread / pip

    # Prijs-sprong per tick: |delta mid|
    mid = (ask + bid) / 2.0
    price_jumps_pips = pd.Series(mid).diff().abs() / pip
    max_price_jump_pips = float(price_jumps_pips.max()) if len(price_jumps_pips) > 1 else 0.0

    # Tijdgaten > 1 minuut
    ts = df["_ts"].values
    if len(ts) > 1:
        ts_series = pd.Series(ts)
        deltas_sec = ts_series.diff().dt.total_seconds()
        gaps_over_1min = int((deltas_sec > 60).sum())
    else:
        gaps_over_1min = 0

    # Zero-volume tellingen
    zero_bid_vol = int((bid_vol == 0).sum())
    zero_ask_vol = int((ask_vol == 0).sum())

    # Sortering check: is UTC monotoon stijgend?
    is_sorted = bool(ts_series.is_monotonic_increasing) if len(ts) > 1 else True

    # Aggregaten
    row = {
        "jaar": year,
        "bestand": os.path.basename(f),
        "n_rijen": n_rows,
        "gesorteerd": "Ja" if is_sorted else "Nee",
        "kolom_swap": "Ja" if swapped else "Nee",
        "pip_factor": pip,
        "min_spread_pips": float(round(spread_pips.min(), 4)),
        "mean_spread_pips": float(round(spread_pips.mean(), 4)),
        "max_spread_pips": float(round(spread_pips.max(), 4)),
        "count_spread_gt_10pips": int((spread_pips > 10).sum()),
        "max_prijs_sprong_pips": round(max_price_jump_pips, 2),
        "gaten_gt_1min": gaps_over_1min,
        "zero_bid_vol": zero_bid_vol,
        "zero_ask_vol": zero_ask_vol,
    }
    results.append(row)

    print(f"   rijen={n_rows:>9,}  swap={row['kolom_swap']}  "
          f"spread[min/mean/max]={row['min_spread_pips']}/{row['mean_spread_pips']}/{row['max_spread_pips']} pips  "
          f"gaten>1m={row['gaten_gt_1min']}  max_jump={row['max_prijs_sprong_pips']} pips")

# Schrijf CSV met resultaten
out_csv = os.path.join(os.path.dirname(CSV_DIR), "USDJPY_quality_results.csv")
df_out = pd.DataFrame(results)
df_out.to_csv(out_csv, index=False, encoding="utf-8")
print(f"\n{'='*100}")
print(f"Resultaten geschreven naar: {out_csv}")

# Pretty markdown tabel
out_md = os.path.join(os.path.dirname(CSV_DIR), "USDJPY_quality_results.md")
with open(out_md, "w", encoding="utf-8") as fh:
    fh.write("# USDJPY Quality Results (1M sample per jaar)\n\n")
    fh.write(f"Gegenereerd: {datetime.now().isoformat()}\n\n")
    cols_to_show = [
        "jaar", "n_rijen", "gesorteerd", "kolom_swap", "pip_factor",
        "min_spread_pips", "mean_spread_pips", "max_spread_pips",
        "count_spread_gt_10pips", "max_prijs_sprong_pips",
        "gaten_gt_1min", "zero_bid_vol", "zero_ask_vol",
    ]
    fh.write("| " + " | ".join(cols_to_show) + " |\n")
    fh.write("|" + "|".join(["---"] * len(cols_to_show)) + "|\n")
    for r in results:
        fh.write("| " + " | ".join(str(r[c]) for c in cols_to_show) + " |\n")
print(f"Markdown tabel geschreven naar: {out_md}")
print("\nKlaar.")