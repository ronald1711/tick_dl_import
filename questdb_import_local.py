import requests
import pandas as pd
import os
import glob
import time
import io
import sys
import re
from datetime import datetime

# ============================================================
# CONFIGURATIE (LOKAAL OP DE SERVER)
# ============================================================
QUESTDB_HOST = "127.0.0.1"
QUESTDB_PORT = 9000
QUESTDB_TABLE = "ticks"
DATA_ROOT = "/mnt/ssd/forexdata"

CHUNK_SIZE = 1_000_000  # Grotere chunks voor sneller lokaal formatteren
SLEEP_BETWEEN_YEARS = 3

BASE_URL = f"http://{QUESTDB_HOST}:{QUESTDB_PORT}"

def questdb_sql(query):
    url = f"{BASE_URL}/exec"
    try:
        resp = requests.get(url, params={"query": query}, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"   [ERROR] SQL fout: {e}")
        return None

def get_existing_years(pair):
    result = questdb_sql(
        f"SELECT DISTINCT year(ts) as yr FROM {QUESTDB_TABLE} WHERE symbol='{pair}' ORDER BY yr"
    )
    if result and "dataset" in result and result["dataset"]:
        return {int(row[0]) for row in result["dataset"]}
    return set()

def parse_imp_response(text):
    """Parse QuestDB /imp text response to check for errors."""
    lines = text.strip().split('\r\n')
    for line in lines:
        if "Errors" in line:
            match = re.search(r'Errors\s+\|\s+(\d+)', line)
            if match:
                errors = int(match.group(1))
                return errors == 0, errors
    return True, 0  # Assume success if no Errors line found

def import_csv_to_questdb(filepath, year, table_name, pair):
    filename = os.path.basename(filepath)
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    
    temp_csv_path = filepath + ".import_ready"
    
    print(f"\n{'='*60}")
    print(f"[Import] Voorbereiden: {filename} ({file_size_mb:,.1f} MB)")
    print(f"{'='*60}")
    
    start_time = time.time()
    chunk_num = 0
    total_rows = 0
    
    # Schrijf de header naar het tijdelijke bestand
    header_cols = ["symbol", "ts", "bid", "ask", "spread", "volume"]
    pd.DataFrame(columns=header_cols).to_csv(temp_csv_path, index=False)
    
    # Lees en formatteer chunk-by-chunk naar het tijdelijke bestand
    for chunk in pd.read_csv(filepath, chunksize=CHUNK_SIZE):
        chunk_num += 1
        
        # Reset index to 0-based to prevent alignment issues in pandas
        chunk = chunk.reset_index(drop=True)
        
        # Bouw DataFrame met QuestDB kolommen
        df_out = pd.DataFrame()
        df_out["symbol"] = [pair] * len(chunk)
        # Snelle string-vervanging (+00:00 naar Z) is ~9x sneller dan datetimes parsen + strftime
        df_out["ts"] = chunk["UTC"].str.replace("+00:00", "Z", regex=False)
        df_out["bid"] = chunk["AskPrice"]      # CSV "AskPrice" = eigenlijk Bid
        df_out["ask"] = chunk["BidPrice"]      # CSV "BidPrice" = eigenlijk Ask
        df_out["spread"] = df_out["ask"] - df_out["bid"]
        df_out["volume"] = chunk["AskVolume"] + chunk["BidVolume"]
        
        # Voeg toe aan tijdelijk bestand zonder header
        df_out.to_csv(temp_csv_path, mode='a', header=False, index=False)
        
        total_rows += len(chunk)
        print(f"   Geformatteerd: {total_rows:,} rijen...", end='\r', flush=True)
        
    format_time = time.time() - start_time
    temp_size_mb = os.path.getsize(temp_csv_path) / (1024 * 1024)
    print(f"\n   [OK] Formatteren voltooid in {format_time:.1f}s (Tijdelijk bestand: {temp_size_mb:,.1f} MB)")
    print(f"   [Import] Starten upload naar QuestDB via één enkele verbinding...", flush=True)
    
    # Upload het geformatteerde bestand in één keer
    url = f"{BASE_URL}/imp"
    params = {
        "name": table_name,
        "timestamp": "ts",
        "overwrite": "false",
    }
    
    max_retries = 3
    upload_success = False
    
    for attempt in range(1, max_retries + 1):
        try:
            upload_start = time.time()
            with open(temp_csv_path, 'rb') as f:
                files = {"data": (filename, f, "text/csv")}
                # Grote timeout (10 min) voor de upload
                resp = requests.post(url, params=params, files=files, timeout=600)
                resp.raise_for_status()
                
            success, errors = parse_imp_response(resp.text)
            if success and resp.status_code == 200:
                upload_time = time.time() - upload_start
                print(f"   [OK] QuestDB upload voltooid in {upload_time:.1f}s!")
                upload_success = True
                break
            else:
                print(f"   [Warning] QuestDB meldde {errors} errors (Poging {attempt}/{max_retries})")
                print(f"   Response: {resp.text[:300]}")
        except Exception as e:
            print(f"   [ERROR] Upload fout (Poging {attempt}/{max_retries}): {e}")
            
        if attempt < max_retries:
            sleep_time = attempt * 10
            print(f"   Wachten {sleep_time}s voor volgende poging...")
            time.sleep(sleep_time)
            
    # Verwijder tijdelijk bestand
    if os.path.exists(temp_csv_path):
        try:
            os.remove(temp_csv_path)
        except Exception as e:
            print(f"   [Warning] Kon tijdelijk bestand niet verwijderen: {e}")
            
    if not upload_success:
        print(f"   [CRITICAL] Upload mislukt na {max_retries} pogingen.")
        sys.exit(1)
        
    elapsed = time.time() - start_time
    print(f"   [Done] Klaar met {year}: {total_rows:,} rijen geïmporteerd in {elapsed:.1f}s "
          f"({total_rows/elapsed:,.0f} rijen/s)")
    
    return total_rows

def main():
    pairs = ["AUDUSD", "EURUSD", "GBPUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]
    
    pair = "EURUSD" # default
    args = sys.argv[1:]
    
    if args and args[0].upper() in pairs:
        pair = args[0].upper()
        args = args[1:]
        
    CSV_DIR = os.path.join(DATA_ROOT, pair)

    print("="*60)
    print(f"[QuestDB] {pair} Tick Data Importer (Local Server Mode)")
    print("="*60)
    print(f"Server: {BASE_URL}")
    print(f"Tabel: {QUESTDB_TABLE}")
    print(f"CSV dir: {CSV_DIR}")
    print(f"Symbol: {pair} (expliciet)")
    print("="*60)
    
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"[OK] QuestDB bereikbaar")
    except Exception as e:
        print(f"[ERROR] Kan QuestDB niet bereiken: {e}")
        sys.exit(1)
    
    existing_years = get_existing_years(pair)
    print(f"\n[Stats] {pair} Jaren al in database: {sorted(existing_years) if existing_years else 'Geen'}")
    
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
        target_years = sorted(set(available_years.keys()) - existing_years)
    
    if not target_years:
        print(f"\n[Done] Geen jaren om te importeren voor {pair}!")
        print(f"   Gebruik: python questdb_import_local.py {pair} --all  (voor alle jaren)")
        print(f"   Of: python questdb_import_local.py {pair} 2015 2016  (specifieke jaren)")
        return
    
    print(f"\n[Import] Te importeren jaren voor {pair}: {target_years}")
    print(f"\n[Tip] Druk op Ctrl+C om te pauzeren/annuleren.\n")
    
    grand_total = 0
    start_all = time.time()
    
    for year in target_years:
        if year not in available_years:
            print(f"[Warning] Geen CSV bestand gevonden voor jaar {year}")
            continue
        
        filepath = available_years[year]
        imported = import_csv_to_questdb(filepath, year, QUESTDB_TABLE, pair)
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
    
    existing_years = get_existing_years(pair)
    print(f"   {pair} Jaren nu in database: {sorted(existing_years)}")
    
    result = questdb_sql(f"SELECT COUNT(*) as total FROM {QUESTDB_TABLE} WHERE symbol='{pair}'")
    if result and "dataset" in result:
        total = result["dataset"][0][0]
        print(f"   Totaal {pair} rijen in tabel: {total:,}")

if __name__ == "__main__":
    main()
