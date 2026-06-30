import requests
import pandas as pd
import os
import glob
import time
from datetime import datetime
import sys

# ============================================================
# CONFIGURATIE
# ============================================================
QUESTDB_HOST = "192.168.10.33"   # IP van je HP server
QUESTDB_PORT = 9000                # Standaard QuestDB HTTP poort
QUESTDB_TABLE = "ticks"            # Bestaande tabel naam
DATA_ROOT = r"C:\projecten\forexdata"

# ============================================================

BASE_URL = f"http://{QUESTDB_HOST}:{QUESTDB_PORT}"

def questdb_sql(query):
    """Voer een SQL query uit op QuestDB via REST API."""
    url = f"{BASE_URL}/exec"
    params = {"query": query}
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"❌ QuestDB query fout: {e}")
        return None

def get_existing_years(pair):
    """Bepaal welke jaren al in de database zitten voor het opgegeven paar."""
    print(f"\n🔍 Checking table '{QUESTDB_TABLE}' for {pair}...")
    
    # Check of tabel bestaat
    schema = questdb_sql(f"SELECT * FROM {QUESTDB_TABLE} LIMIT 1")
    if schema is None or "error" in schema:
        print(f"⚠️ Tabel '{QUESTDB_TABLE}' bestaat mogelijk nog niet of is leeg.")
        return set()
    
    # Query voor min/max datum voor dit symbool
    result = questdb_sql(
        f"SELECT MIN(ts) as min_ts, MAX(ts) as max_ts, COUNT(*) as total FROM {QUESTDB_TABLE} WHERE symbol='{pair}'"
    )
    
    if result and "dataset" in result and len(result["dataset"]) > 0:
        row = result["dataset"][0]
        min_ts = row[0]
        max_ts = row[1]
        total = row[2]
        if total > 0:
            print(f"   Tabel gevonden met bestaande data voor {pair}!")
            print(f"   Min datum: {min_ts}")
            print(f"   Max datum: {max_ts}")
            print(f"   Totaal rijen: {total:,}")
        else:
            print(f"   Tabel '{QUESTDB_TABLE}' is leeg of bevat nog geen data voor {pair}.")
            return set()
        
        # Haal alle unieke jaren op voor dit symbool
        years_result = questdb_sql(
            f"SELECT DISTINCT year(ts) as yr FROM {QUESTDB_TABLE} WHERE symbol='{pair}' ORDER BY yr"
        )
        if years_result and "dataset" in years_result:
            years = {int(row[0]) for row in years_result["dataset"]}
            print(f"   Jaren aanwezig voor {pair}: {sorted(years)}")
            return years
    
    return set()

def check_table_schema():
    """Toon het schema van de bestaande tabel."""
    print(f"\n📋 Schema van '{QUESTDB_TABLE}':")
    schema = questdb_sql(f"SELECT * FROM {QUESTDB_TABLE} LIMIT 1")
    if schema and "columns" in schema:
        for col in schema["columns"]:
            print(f"   {col['name']:20} {col['type']}")
    else:
        print("   (Tabel niet gevonden of leeg)")

def suggest_import_plan(pair):
    """Bepaal welke jaren geïmporteerd moeten worden."""
    CSV_DIR = os.path.join(DATA_ROOT, pair)
    
    print("\n" + "="*60)
    print(f"📊 DIAGNOSE: QuestDB Import Plan voor {pair}")
    print("="*60)
    
    check_table_schema()
    existing_years = get_existing_years(pair)
    
    # Haal alle beschikbare jaren uit de CSV bestanden
    pattern = os.path.join(CSV_DIR, f"{pair}_tick_UTC+0_00_*-Parse.csv")
    files = sorted(glob.glob(pattern))
    
    csv_years = {}
    for f in files:
        basename = os.path.basename(f)
        year_str = basename.split("_")[4].split("-")[0]
        year = int(year_str)
        csv_years[year] = f
    
    print(f"\n📁 CSV bestanden beschikbaar in {CSV_DIR}:")
    print(f"   Jaren: {sorted(csv_years.keys())}")
    
    if not existing_years:
        print(f"\n⚠️ Geen bestaande data gevonden voor '{pair}' in '{QUESTDB_TABLE}'.")
        print(f"   ALLE jaren moeten geïmporteerd worden!")
        missing_years = sorted(csv_years.keys())
    else:
        missing_years = sorted(set(csv_years.keys()) - existing_years)
        print(f"\n✅ Jaren al in database: {sorted(existing_years)}")
        if missing_years:
            print(f"\n❌ Jaren die ontbreken: {missing_years}")
        else:
            print(f"\n🎉 Alle jaren zijn al aanwezig in de database voor {pair}!")
    
    # Toon bestandsgroottes
    if missing_years:
        print(f"\n📦 Te importeren bestanden:")
        total_size = 0
        for yr in missing_years:
            fpath = csv_years[yr]
            size_mb = os.path.getsize(fpath) / (1024*1024)
            total_size += size_mb
            print(f"   {yr}: {os.path.basename(fpath)} ({size_mb:,.1f} MB)")
        print(f"   Totaal: {total_size:,.1f} MB")
        
        print("\n📝 Volgende stap:")
        print(f"   Run 'python questdb_import.py {pair}' om de ontbrekende jaren te importeren.")
        print(f"   Voor alle jaren: python questdb_import.py {pair} --all")
    
    return missing_years, csv_years

def test_connection():
    """Test of QuestDB bereikbaar is."""
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ QuestDB bereikbaar op {BASE_URL}")
        return True
    except Exception as e:
        print(f"❌ Kan QuestDB niet bereiken op {BASE_URL}")
        print(f"   Fout: {e}")
        return False

def main():
    pairs = ["AUDUSD", "EURUSD", "GBPUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]
    
    pair = "EURUSD" # default
    args = sys.argv[1:]
    
    if args and args[0].upper() in pairs:
        pair = args[0].upper()
        args = args[1:]

    print("="*60)
    print(f"🔧 QuestDB Diagnose Tool voor {pair} Tick Data")
    print("="*60)
    
    if test_connection():
        suggest_import_plan(pair)

if __name__ == "__main__":
    main()
