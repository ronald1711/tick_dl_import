import os
import sys
import gzip
import shutil
import time
import glob

# ============================================================
# CONFIGURATIE
# ============================================================
DATA_ROOT = "/mnt/ssd/forexdata"  # Aanpassen voor Windows of Linux

# Als de map niet bestaat op Linux, probeer de Windows default
if not os.path.exists(DATA_ROOT) and os.path.exists(r"C:\projecten\forexdata"):
    DATA_ROOT = r"C:\projecten\forexdata"

def compress_file(src_path, dst_path):
    """Comprimeert een bestand naar gzip indeling."""
    with open(src_path, 'rb') as f_in:
        with gzip.open(dst_path, 'wb', compresslevel=6) as f_out:
            shutil.copyfileobj(f_in, f_out)

def main():
    print("="*60)
    print("Forex Data Gzip Compressor")
    print("="*60)
    print(f"Data root: {DATA_ROOT}")
    print("="*60)
    
    if not os.path.exists(DATA_ROOT):
        print(f"[ERROR] Data root map {DATA_ROOT} bestaat niet!")
        sys.exit(1)
        
    # Zoek alle -Parse.csv bestanden in alle submappen
    # Excludeer reeds gecomprimeerde bestanden en kwaliteitsrapporten
    csv_pattern = os.path.join(DATA_ROOT, "*", "*_tick_UTC+0_00_*-Parse.csv")
    csv_files = glob.glob(csv_pattern)
    
    # Zoek eventueel ook naar 1m bestanden
    csv_1m_pattern = os.path.join(DATA_ROOT, "*", "*_1m_*-Parse.csv")
    csv_files.extend(glob.glob(csv_1m_pattern))
    csv_1m_pattern2 = os.path.join(DATA_ROOT, "*", "*_1m_*.csv")
    csv_files.extend([f for f in glob.glob(csv_1m_pattern2) if not f.endswith(".csv.gz")])
    
    # Filter unieke bestanden en zorg dat we geen kwaliteitsrapporten (.md/csv resultaten) meepakken
    csv_files = sorted(list(set([f for f in csv_files if os.path.isfile(f)])))
    
    if not csv_files:
        print("Geen ongecomprimeerde CSV-bestanden gevonden om te verwerken.")
        return
        
    print(f"Gevonden bestanden voor compressie: {len(csv_files)}")
    for f in csv_files:
        print(f" - {os.path.basename(f)} ({os.path.getsize(f)/(1024*1024):.1f} MB)")
        
    confirm = input("\nWil je doorgaan met de compressie? (y/n): ")
    if confirm.lower() != 'y':
        print("Geannuleerd door gebruiker.")
        return
        
    total_saved = 0
    t_start = time.time()
    
    for src in csv_files:
        dst = src + ".gz"
        src_name = os.path.basename(src)
        src_size = os.path.getsize(src)
        src_size_mb = src_size / (1024 * 1024)
        
        print(f"\n[Compress] Verwerken: {src_name} ({src_size_mb:.1f} MB)...")
        t0 = time.time()
        
        try:
            compress_file(src, dst)
            dst_size = os.path.getsize(dst)
            dst_size_mb = dst_size / (1024 * 1024)
            elapsed = time.time() - t0
            
            saved_mb = src_size_mb - dst_size_mb
            total_saved += saved_mb
            
            ratio = (dst_size / src_size) * 100
            print(f"   [OK] Gecomprimeerd naar {os.path.basename(dst)} ({dst_size_mb:.1f} MB) in {elapsed:.1f}s")
            print(f"   Ratio: {ratio:.1f}% (Besparing: {saved_mb:.1f} MB)")
            
            # Verwijder het originele bestand na succesvolle compressie
            os.remove(src)
            print("   [OK] Origineel bestand verwijderd.")
            
        except Exception as e:
            print(f"   [ERROR] Fout tijdens compressie van {src_name}: {e}")
            if os.path.exists(dst):
                try:
                    os.remove(dst)
                except:
                    pass
                    
    total_elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print("COMPRESSIE VOLTOOID!")
    print(f"{'='*60}")
    print(f"Totale tijd: {total_elapsed/60:.1f} minuten")
    print(f"Totale schijfruimte bespaard: {total_saved/1024:.2f} GB")

if __name__ == "__main__":
    main()
