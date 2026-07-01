import glob
import os
import sys
import time
import requests
import pandas as pd
from questdb.ingress import Sender

# ============================================================
# CONFIGURATIE (LOKAAL OP DE SERVER, VIA ILP I.P.V. /imp HTTP CSV)
# ============================================================
QUESTDB_HOST = "127.0.0.1"
QUESTDB_PORT = 9000
QUESTDB_TABLE = "ticks"
DATA_ROOT = "/mnt/ssd/forexdata"

# ILP over HTTP: geen tijdelijk CSV-bestand, geen dubbele schijf-I/O, geen
# server-side CSV-reparse/schema-detectie zoals bij /imp. Alleen zinvol
# lokaal (127.0.0.1) waar netwerkbandbreedte geen bottleneck is.
QUESTDB_ILP_CONF = f"http::addr={QUESTDB_HOST}:{QUESTDB_PORT};"

CHUNK_SIZE = 1_000_000
SLEEP_BETWEEN_YEARS = 3
MAX_RETRIES = 3

BASE_URL = f"http://{QUESTDB_HOST}:{QUESTDB_PORT}"


def questdb_sql(query, timeout=15):
    try:
        resp = requests.get(f"{BASE_URL}/exec", params={"query": query}, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"   [ERROR] SQL fout: {e}")
        return None


def get_existing_years(pair, candidate_years):
    """Check per jaar (partition-pruned, snel) i.p.v. een dure full-table
    DISTINCT year(ts) scan die op een tabel van miljarden rijen timeout geeft."""
    existing = set()
    for year in candidate_years:
        result = questdb_sql(
            f"SELECT count() FROM {QUESTDB_TABLE} WHERE symbol='{pair}' AND ts IN '{year}'"
        )
        if result and "dataset" in result and result["dataset"] and result["dataset"][0][0] > 0:
            existing.add(year)
    return existing


def import_csv_to_questdb(filepath, year, pair, sender):
    filename = os.path.basename(filepath)
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)

    print(f"\n{'='*60}")
    print(f"[Import] Streamen via ILP: {filename} ({file_size_mb:,.1f} MB)")
    print(f"{'='*60}")

    start_time = time.time()
    total_rows = 0

    for chunk in pd.read_csv(filepath, chunksize=CHUNK_SIZE):
        chunk = chunk.reset_index(drop=True)

        df_out = pd.DataFrame()
        df_out["symbol"] = [pair] * len(chunk)
        # ILP vereist datetime64[ns, UTC] (niet de [us] resolutie van pandas 3.x default)
        df_out["ts"] = pd.to_datetime(chunk["UTC"], utc=True).astype("datetime64[ns, UTC]")
        df_out["bid"] = chunk["AskPrice"]      # CSV "AskPrice" = eigenlijk Bid
        df_out["ask"] = chunk["BidPrice"]      # CSV "BidPrice" = eigenlijk Ask
        df_out["spread"] = df_out["ask"] - df_out["bid"]
        df_out["volume"] = chunk["AskVolume"] + chunk["BidVolume"]

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                sender.dataframe(df_out, table_name=QUESTDB_TABLE, at="ts", symbols=["symbol"])
                sender.flush()
                break
            except Exception as e:
                print(f"\n   [Warning] ILP-fout (Poging {attempt}/{MAX_RETRIES}): {e}")
                if attempt == MAX_RETRIES:
                    print(f"   [CRITICAL] Versturen mislukt na {MAX_RETRIES} pogingen.")
                    sys.exit(1)
                time.sleep(attempt * 5)

        total_rows += len(chunk)
        print(f"   Verstuurd: {total_rows:,} rijen...", end='\r', flush=True)

    elapsed = time.time() - start_time
    print(f"\n   [Done] Klaar met {year}: {total_rows:,} rijen geïmporteerd in {elapsed:.1f}s "
          f"({total_rows/elapsed:,.0f} rijen/s)")

    return total_rows


def main():
    pairs = ["AUDUSD", "EURUSD", "GBPUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]

    pair = "EURUSD"  # default
    args = sys.argv[1:]

    if args and args[0].upper() in pairs:
        pair = args[0].upper()
        args = args[1:]

    CSV_DIR = os.path.join(DATA_ROOT, pair)

    print("="*60)
    print(f"[QuestDB ILP] {pair} Tick Data Importer (Local Server Mode)")
    print("="*60)
    print(f"Server: {BASE_URL} (ILP via HTTP, poort {QUESTDB_PORT})")
    print(f"Tabel: {QUESTDB_TABLE}")
    print(f"CSV dir: {CSV_DIR}")
    print(f"Symbol: {pair} (expliciet)")
    print("="*60)

    try:
        requests.get(f"{BASE_URL}/", timeout=5)
        print("[OK] QuestDB bereikbaar")
    except Exception as e:
        print(f"[ERROR] Kan QuestDB niet bereiken: {e}")
        sys.exit(1)

    csv_files = sorted(glob.glob(os.path.join(CSV_DIR, f"{pair}_tick_UTC+0_00_*-Parse.csv")))

    available_years = {}
    for f in csv_files:
        basename = os.path.basename(f)
        year_str = basename.split("_")[4].split("-")[0]
        year = int(year_str)
        available_years[year] = f

    if len(args) > 0:
        if args[0] == "--all":
            target_years = sorted(available_years.keys())
        else:
            target_years = []
            for arg in args:
                if arg.isdigit():
                    target_years.append(int(arg))
    else:
        existing_years = get_existing_years(pair, sorted(available_years.keys()))
        print(f"\n[Stats] {pair} jaren al in database: {sorted(existing_years) if existing_years else 'Geen'}")
        target_years = sorted(set(available_years.keys()) - existing_years)

    if not target_years:
        print(f"\n[Done] Geen jaren om te importeren voor {pair}!")
        print(f"   Gebruik: python questdb_import_ilp_local.py {pair} --all  (voor alle jaren)")
        print(f"   Of: python questdb_import_ilp_local.py {pair} 2015 2016  (specifieke jaren)")
        return

    print(f"\n[Import] Te importeren jaren voor {pair}: {target_years}")
    print(f"\n[Tip] Druk op Ctrl+C om te pauzeren/annuleren.\n")

    grand_total = 0
    start_all = time.time()

    with Sender.from_conf(QUESTDB_ILP_CONF) as sender:
        for year in target_years:
            if year not in available_years:
                print(f"[Warning] Geen CSV bestand gevonden voor jaar {year}")
                continue

            filepath = available_years[year]
            imported = import_csv_to_questdb(filepath, year, pair, sender)
            grand_total += imported

            if year != target_years[-1]:
                print(f"   [Pause] Pauze van {SLEEP_BETWEEN_YEARS}s...")
                time.sleep(SLEEP_BETWEEN_YEARS)

    elapsed_all = time.time() - start_all
    print(f"\n{'='*60}")
    print(f"[Done] IMPORT COMPLEET!")
    print(f"{'='*60}")
    print(f"Totale rijen geïmporteerd: {grand_total:,}")
    print(f"Totale tijd: {elapsed_all:.1f}s ({grand_total/elapsed_all:,.0f} rijen/s)")
    print(f"\nVerificatie:")

    existing_years = get_existing_years(pair, target_years)
    print(f"   {pair} jaren nu in database (van deze run): {sorted(existing_years)}")


if __name__ == "__main__":
    main()
