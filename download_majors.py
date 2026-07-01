import os
import sys
import time
import glob
from datetime import datetime
import pandas as pd
from findatapy.market import Market, MarketDataRequest
from findatapy.util.dataconstants import DataConstants

# Avoid Dukascopy 503 rate-limiting and connection blocks by disabling multithreading and increasing timeout
DataConstants.dukascopy_multithreading = False
DataConstants.dukascopy_mini_timeout_seconds = 30


DATA_ROOT = r"C:\projecten\forexdata"

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def get_months_for_year(year):
    """Return a list of (month_num, start_str, end_str) for a given year up to today."""
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
            # Current month: end at current day
            end_str = f"{curr_day:02d} {MONTH_NAMES[m-1]} {year}"
        else:
            # Normal month: end at 1st of next month (exclusive)
            if m < 12:
                end_str = f"01 {MONTH_NAMES[m]} {year}"
            else:
                end_str = f"01 Jan {year + 1}"
                
        months.append((m, start_str, end_str))
    return months

def format_and_swap_df(df):
    """Format index to ISO 8601 with 3 decimals and swap columns to match historical conventions."""
    if df is None or df.empty:
        return None
        
    # Find columns by suffix
    bid_col = [c for c in df.columns if c.endswith('.bid')][0]
    ask_col = [c for c in df.columns if c.endswith('.ask')][0]
    bidv_col = [c for c in df.columns if c.endswith('.bidv')][0]
    askv_col = [c for c in df.columns if c.endswith('.askv')][0]
    
    out_df = pd.DataFrame(index=df.index)
    
    # Format UTC time index: YYYY-MM-DDTHH:MM:SS.fff+00:00
    out_df['UTC'] = df.index.strftime('%Y-%m-%dT%H:%M:%S.%f').str[:-3] + '+00:00'
    
    # Swap mapping:
    # AskPrice -> Bid Price
    # BidPrice -> Ask Price
    # AskVolume -> Bid Volume
    # BidVolume -> Ask Volume
    out_df['AskPrice'] = df[bid_col]
    out_df['BidPrice'] = df[ask_col]
    out_df['AskVolume'] = df[bidv_col]
    out_df['BidVolume'] = df[askv_col]
    
    return out_df

def download_month(market, pair, year, month_num, start_date, finish_date, temp_file_path):
    """Download a single month chunk with retries."""
    print(f"    -> Downloading {start_date} to {finish_date}...", flush=True)
    
    md_request = MarketDataRequest(
        start_date=start_date,
        finish_date=finish_date,
        category="fx",
        fields=["bid", "ask", "bidv", "askv"],
        freq="tick",
        data_source="dukascopy",
        tickers=[pair],
    )
    
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            t0 = time.time()
            df = market.fetch_market(md_request)
            elapsed = time.time() - t0
            
            if df is not None and not df.empty:
                print(f"      Downloaded {len(df):,} rows in {elapsed:.1f}s. Formatting and swapping...", flush=True)
                formatted_df = format_and_swap_df(df)
                
                if formatted_df is not None:
                    formatted_df.to_csv(temp_file_path, index=False)
                    print(f"      Saved to {os.path.basename(temp_file_path)}", flush=True)
                    return True
                else:
                    print("      Error: Formatted DataFrame was empty.", flush=True)
            else:
                # Some periods (e.g. weekend or future days) might return empty
                print("      Warning: Received empty DataFrame.", flush=True)
                # Write header only
                empty_df = pd.DataFrame(columns=['UTC', 'AskPrice', 'BidPrice', 'AskVolume', 'BidVolume'])
                empty_df.to_csv(temp_file_path, index=False)
                return True
                
        except Exception as e:
            print(f"      Attempt {attempt}/{max_retries} failed: {e}", flush=True)
            if attempt < max_retries:
                sleep_sec = attempt * 5
                print(f"      Sleeping {sleep_sec}s before retry...", flush=True)
                time.sleep(sleep_sec)
            else:
                print("      Max retries reached. Failing this month.", flush=True)
                return False
    return False

import gzip

def merge_monthly_files(temp_files, final_csv_path):
    """Merge temp month files into a single year compressed file (.csv.gz), skipping headers on subsequent files."""
    print(f"    Merging {len(temp_files)} monthly files into {os.path.basename(final_csv_path)}...", flush=True)
    t0 = time.time()
    
    with gzip.open(final_csv_path, 'wt', encoding='utf-8') as outfile:
        first_written = False
        for month_file in temp_files:
            if not os.path.exists(month_file):
                continue
                
            with open(month_file, 'r', encoding='utf-8') as infile:
                if not first_written:
                    # Write everything including header
                    outfile.write(infile.read())
                    first_written = True
                else:
                    # Skip the header line
                    infile.readline()
                    outfile.write(infile.read())
                    
    print(f"    Merged and compressed successfully in {time.time()-t0:.1f}s.", flush=True)

def process_pair_year(market, pair, year):
    """Download and build the file for a single pair and year."""
    pair_dir = os.path.join(DATA_ROOT, pair)
    os.makedirs(pair_dir, exist_ok=True)
    
    final_csv_path = os.path.join(pair_dir, f"{pair}_tick_UTC+0_00_{year}-Parse.csv.gz")
    
    # Check if final merged file already exists
    if os.path.exists(final_csv_path):
        print(f"  Year {year} already fully downloaded and merged. Skipping.", flush=True)
        return True
        
    # Get month ranges to download
    months = get_months_for_year(year)
    
    temp_files = []
    all_success = True
    
    print(f"\n--- Processing {pair} for Year {year} ---", flush=True)
    
    for m, start_str, end_str in months:
        temp_file_path = os.path.join(pair_dir, f"tmp_{pair}_{year}_{m:02d}.csv")
        temp_files.append(temp_file_path)
        
        # Check if already downloaded
        if os.path.exists(temp_file_path):
            print(f"  Month {m} already downloaded. Skipping download.", flush=True)
            continue
            
        success = download_month(market, pair, year, m, start_str, end_str, temp_file_path)
        if not success:
            all_success = False
            print(f"  Error: Failed to download month {m}.", flush=True)
            break
            
        # Polite sleep to avoid hitting rate limits
        time.sleep(2)
        
    if all_success:
        # Merge them
        merge_monthly_files(temp_files, final_csv_path)
        
        # Clean up temp files
        print("    Cleaning up temporary files...", flush=True)
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        print("    Cleanup finished.", flush=True)
        return True
    else:
        print(f"  Warning: Skipping merge for {pair} {year} due to download failures.", flush=True)
        return False

def main():
    pairs = ["AUDUSD", "EURUSD", "GBPUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY"]
    years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
    
    # Allow filtering via CLI arguments
    if len(sys.argv) > 1:
        custom_pairs = [p.upper() for p in sys.argv[1:] if p.upper() in pairs]
        if custom_pairs:
            pairs = custom_pairs
            print(f"Custom pairs filtered: {pairs}")
            
    print("Initializing findatapy Market (single-threaded for Dukascopy stability)...", flush=True)
    market = Market(market_data_generator=None)
    
    overall_start = time.time()
    
    for pair in pairs:
        for year in years:
            success = process_pair_year(market, pair, year)
            if not success:
                print(f"Aborting run for {pair} due to error in year {year}.", flush=True)
                break
                
    print(f"\nAll done! Total time: {(time.time() - overall_start) / 60.0:.2f} minutes.", flush=True)

if __name__ == "__main__":
    main()
