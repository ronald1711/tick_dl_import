import os
import sys
import time
import argparse
from datetime import datetime
import pandas as pd
from findatapy.market import Market, MarketDataRequest
from findatapy.util.dataconstants import DataConstants

# Voorkom Dukascopy 503 rate-limiting en timeouts
DataConstants.dukascopy_multithreading = False
DataConstants.dukascopy_mini_timeout_seconds = 30

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def get_months_for_year(year):
    """Geeft een lijst van (month_num, start_str, end_str) voor het gegeven jaar tot vandaag."""
    current_time = datetime.now()
    curr_year = current_time.year
    curr_month = current_time.month
    curr_day = current_time.day
    
    months = []
    for m in range(1, 13):
        if year > curr_year:
            break
        if year == curr_year and m > curr_month:
            break
            
        start_str = f"01 {MONTH_NAMES[m-1]} {year}"
        
        if year == curr_year and m == curr_month:
            end_str = f"{curr_day:02d} {MONTH_NAMES[m-1]} {year}"
        else:
            if m < 12:
                end_str = f"01 {MONTH_NAMES[m]} {year}"
            else:
                end_str = f"01 Jan {year + 1}"
                
        months.append((m, start_str, end_str))
    return months

def format_and_swap_df(df):
    """Formatteert index naar UTC string en wisselt kolommen om conform Dukascopy/historical conventie."""
    if df is None or df.empty:
        return None
        
    bid_col = [c for c in df.columns if c.endswith('.bid')][0]
    ask_col = [c for c in df.columns if c.endswith('.ask')][0]
    bidv_col = [c for c in df.columns if c.endswith('.bidv')][0]
    askv_col = [c for c in df.columns if c.endswith('.askv')][0]
    
    out_df = pd.DataFrame(index=df.index)
    
    # Gebruik snelle string manipulatie i.p.v. strftime voor ticks
    out_df['UTC'] = df.index.strftime('%Y-%m-%dT%H:%M:%S.%f').str[:-3] + '+00:00'
    
    # Kolomverwisseling (AskPrice hoort > BidPrice te zijn)
    out_df['AskPrice'] = df[bid_col]
    out_df['BidPrice'] = df[ask_col]
    out_df['AskVolume'] = df[bidv_col]
    out_df['BidVolume'] = df[askv_col]
    
    return out_df

def resample_ticks_to_1m(df):
    """Resamepletick DataFrame naar 1-minuut OHLCV bars op basis van mid-price."""
    if df is None or df.empty:
        return None
        
    # Bereken mid price en totaal volume
    mid = (df['AskPrice'] + df['BidPrice']) / 2.0
    volume = df['AskVolume'] + df['BidVolume']
    
    # Resample
    ohlc = mid.resample('1min').ohlc()
    vol_sum = volume.resample('1min').sum()
    
    resampled = pd.DataFrame(index=ohlc.index)
    resampled['UTC'] = ohlc.index.strftime('%Y-%m-%dT%H:%M:%S.000000Z')
    resampled['Open'] = ohlc['open']
    resampled['High'] = ohlc['high']
    resampled['Low'] = ohlc['low']
    resampled['Close'] = ohlc['close']
    resampled['Volume'] = vol_sum
    
    # Verwijder lege periodes (zoals weekenden)
    resampled = resampled.dropna(subset=['Open'])
    return resampled

def download_month(market, symbol, start_date, finish_date, temp_file_path, freq):
    """Downloadt een enkele maand met retries."""
    print(f"    -> Downloaden {start_date} tot {finish_date}...", flush=True)
    
    md_request = MarketDataRequest(
        start_date=start_date,
        finish_date=finish_date,
        fields=["bid", "ask", "bidv", "askv"],
        freq="tick",
        data_source="dukascopy",
        tickers=[symbol],
        vendor_tickers=[symbol], # Omzeilt de findatapy category mapping
    )
    
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            t0 = time.time()
            df = market.fetch_market(md_request)
            elapsed = time.time() - t0
            
            if df is not None and not df.empty:
                print(f"      Gedownload: {len(df):,} ticks in {elapsed:.1f}s. Formatteren...", flush=True)
                formatted_df = format_and_swap_df(df)
                
                if formatted_df is not None:
                    if freq == '1m':
                        print("      Resamplen naar 1-minuut bars...", flush=True)
                        resampled_df = resample_ticks_to_1m(formatted_df)
                        if resampled_df is not None:
                            resampled_df.to_csv(temp_file_path, index=False)
                            print(f"      1m bars opgeslagen in {os.path.basename(temp_file_path)}", flush=True)
                            return True
                        else:
                            print("      Error: Resampling resulteerde in lege DataFrame.", flush=True)
                    else:
                        formatted_df.to_csv(temp_file_path, index=False)
                        print(f"      Ticks opgeslagen in {os.path.basename(temp_file_path)}", flush=True)
                        return True
                else:
                    print("      Error: Geformatteerde DataFrame was leeg.", flush=True)
            else:
                print("      Warning: Lege DataFrame ontvangen (bijv. weekend of feestdag).", flush=True)
                # Schrijf lege header
                cols = ['UTC', 'Open', 'High', 'Low', 'Close', 'Volume'] if freq == '1m' else ['UTC', 'AskPrice', 'BidPrice', 'AskVolume', 'BidVolume']
                empty_df = pd.DataFrame(columns=cols)
                empty_df.to_csv(temp_file_path, index=False)
                return True
                
        except Exception as e:
            print(f"      Poging {attempt}/{max_retries} mislukt: {e}", flush=True)
            if attempt < max_retries:
                sleep_sec = attempt * 10
                print(f"      Wachten {sleep_sec}s voor volgende poging...", flush=True)
                time.sleep(sleep_sec)
            else:
                print("      Max pogingen bereikt. Maand overgeslagen.", flush=True)
                return False
    return False

def merge_monthly_files(temp_files, final_csv_path):
    """Voegt de maandbestanden samen tot één jaarbestand."""
    print(f"    Samenvoegen van {len(temp_files)} maandbestanden naar {os.path.basename(final_csv_path)}...", flush=True)
    t0 = time.time()
    
    with open(final_csv_path, 'w', encoding='utf-8') as outfile:
        first_written = False
        for month_file in temp_files:
            if not os.path.exists(month_file):
                continue
                
            with open(month_file, 'r', encoding='utf-8') as infile:
                if not first_written:
                    outfile.write(infile.read())
                    first_written = True
                else:
                    infile.readline() # Skip header
                    outfile.write(infile.read())
                    
    print(f"    Samenvoeging voltooid in {time.time()-t0:.1f}s.", flush=True)

def process_symbol_year(market, symbol, year, freq, data_root):
    """Verwerkt een enkel symbool en jaar."""
    symbol_dir = os.path.join(data_root, symbol)
    os.makedirs(symbol_dir, exist_ok=True)
    
    suffix = "1m" if freq == "1m" else "tick_UTC+0_00"
    final_csv_path = os.path.join(symbol_dir, f"{symbol}_{suffix}_{year}-Parse.csv" if freq == "tick" else f"{symbol}_{suffix}_{year}.csv")
    
    # Skip als het eindsplitsingsbestand al bestaat (voor eerdere jaren)
    if os.path.exists(final_csv_path) and year < datetime.now().year:
        print(f"  Jaar {year} is al volledig gedownload en samengevoegd. Overslaan.", flush=True)
        return True
        
    months = get_months_for_year(year)
    temp_files = []
    all_success = True
    
    print(f"\n--- Verwerken {symbol} voor Jaar {year} ({freq}) ---", flush=True)
    
    for m, start_str, end_str in months:
        temp_file_path = os.path.join(symbol_dir, f"tmp_{freq}_{symbol}_{year}_{m:02d}.csv")
        temp_files.append(temp_file_path)
        
        if os.path.exists(temp_file_path):
            print(f"  Maand {m} al aanwezig. Overslaan.", flush=True)
            continue
            
        success = download_month(market, symbol, start_str, end_str, temp_file_path, freq)
        if not success:
            all_success = False
            print(f"  [ERROR] Fout bij downloaden van maand {m}.", flush=True)
            break
            
        time.sleep(2)  # Vriendelijke pauze tussen downloads
        
    if all_success:
        merge_monthly_files(temp_files, final_csv_path)
        print("    Tijdelijke bestanden opruimen...", flush=True)
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        print("    Opruimen voltooid.", flush=True)
        return True
    else:
        print(f"  [WARNING] Samenvoegen voor {symbol} {year} overgeslagen wegens fouten.", flush=True)
        return False

def main():
    parser = argparse.ArgumentParser(description="Dukascopy Forex & Commodities Tick/1m Downloader")
    parser.add_argument("--symbols", required=True, help="Comma-gescheiden lijst van symbolen, bijv. GBPUSD,XAUUSD,BRENTUSD")
    parser.add_argument("--freq", choices=["tick", "1m"], default="tick", help="Resolutie: tick of 1m bars")
    parser.add_argument("--years", help="Comma-gescheiden lijst van specifieke jaren, bijv. 2024,2025")
    parser.add_argument("--start-year", type=int, help="Startjaar (optioneel)")
    parser.add_argument("--end-year", type=int, help="Eindjaar (optioneel)")
    parser.add_argument("--data-root", default="/mnt/ssd/forexdata", help="Doelmap voor opslag (default: /mnt/ssd/forexdata)")
    
    args = parser.parse_args()
    
    symbols = [s.strip().upper() for s in args.symbols.split(",")]
    
    # Bepaal de jaren
    if args.years:
        years = sorted([int(y.strip()) for y in args.years.split(",")])
    elif args.start_year and args.end_year:
        years = list(range(args.start_year, args.end_year + 1))
    else:
        # Standaard laatste 2 jaar voor ticks, 5 jaar voor 1m (inclusief huidig jaar)
        curr_year = datetime.now().year
        if args.freq == '1m':
            years = list(range(curr_year - 4, curr_year + 1))
        else:
            years = list(range(curr_year - 1, curr_year + 1))
            
    print("="*60)
    print("Dukascopy Data Downloader (Local Server)")
    print("="*60)
    print(f"Symbolen: {symbols}")
    print(f"Resolutie: {args.freq}")
    print(f"Jaren: {years}")
    print(f"Doelmap: {args.data-root}")
    print("="*60)
    
    print("Initializing findatapy Market (single-threaded for stability)...", flush=True)
    market = Market(market_data_generator=None)
    
    overall_start = time.time()
    
    for symbol in symbols:
        for year in years:
            success = process_symbol_year(market, symbol, year, args.freq, args.data_root)
            if not success:
                print(f"Download afgebroken voor {symbol} in jaar {year} wegens netwerk/downloadfout.", flush=True)
                break
                
    elapsed = (time.time() - overall_start) / 60.0
    print(f"\nAlles voltooid! Totale tijd: {elapsed:.2f} minuten.")

if __name__ == "__main__":
    main()
