"""
Decomprimeer alle resterende majors uit E:\\majors naar C:\\projecten\\forexdata.

Loopt over alle subdirs van E:\\majors, decomprimeert de .zst archieven,
en slaat <pair>_tick_UTC+0_00_<jaar>-Parse.csv op in C:\\projecten\\forexdata\\<pair>.

Pares die al zijn uitgepakt (EURUSD, GBPUSD, USDJPY) worden overgeslagen.
Per paar wordt 6-threaded decompressie gebruikt; paren worden sequentieel
verwerkt om disk-head thrashing te beperken.
"""
import zstandard
import os
import glob
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

SRC_ROOT = r"E:\majors"
DST_ROOT = r"C:\projecten\forexdata"
THREADS_PER_PAIR = 6


def decompress(src, dst):
    name = os.path.basename(src)
    if os.path.exists(dst):
        return (name, "skip", os.path.getsize(dst), 0.0, 0.0)
    t0 = time.time()
    try:
        with open(src, "rb") as fin, open(dst, "wb") as fout:
            dctx = zstandard.ZstdDecompressor()
            dctx.copy_stream(fin, fout)
        elapsed = time.time() - t0
        src_size = os.path.getsize(src)
        dst_size = os.path.getsize(dst)
        ratio = dst_size / src_size if src_size else 0
        return (name, "ok", dst_size, elapsed, ratio)
    except Exception as e:
        return (name, "error", str(e), 0.0, 0.0)


def process_pair(pair):
    src_dir = os.path.join(SRC_ROOT, pair)
    dst_dir = os.path.join(DST_ROOT, pair)
    os.makedirs(dst_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src_dir, "*.csv.zst")))
    if not files:
        return pair, 0, 0, 0, 0
    print(f"\n=== {pair}: {len(files)} bestanden ===", flush=True)
    pair_t0 = time.time()
    ok = skip = err = 0
    total_out = 0
    with ThreadPoolExecutor(max_workers=THREADS_PER_PAIR) as ex:
        futures = []
        for f in files:
            name = os.path.basename(f)
            dst = os.path.join(dst_dir, name[: -len(".zst")])
            futures.append(ex.submit(decompress, f, dst))
        for fut in as_completed(futures):
            r = fut.result()
            status = r[1]
            if status == "ok":
                _, _, dst_size, elapsed, ratio = r
                ok += 1
                total_out += dst_size
                print(f"  [OK ] {r[0]:>55}  -> {dst_size/1024/1024:>7.1f} MB"
                      f"  ({elapsed:5.1f}s, {ratio:.1f}x)", flush=True)
            elif status == "skip":
                skip += 1
                print(f"  [SKIP] {r[0]} (reeds aanwezig)", flush=True)
            else:
                err += 1
                print(f"  [ERR] {r[0]}: {r[2]}", flush=True)
    pair_elapsed = time.time() - pair_t0
    print(f"  -> {pair}: {pair_elapsed:.1f}s  ok={ok}  skip={skip}  err={err}  "
          f"uitgepakt: {total_out/1024/1024:.1f} MB", flush=True)
    return pair, ok, skip, err, total_out


def main():
    pairs = sorted(p.name for p in os.scandir(SRC_ROOT) if p.is_dir())
    print(f"Gevonden paren in {SRC_ROOT}: {pairs}")

    # Sla paren over waar alle bestanden al zijn uitgepakt
    todo = []
    for p in pairs:
        src_files = sorted(glob.glob(os.path.join(SRC_ROOT, p, "*.csv.zst")))
        if not src_files:
            continue
        dst_csvs = glob.glob(os.path.join(DST_ROOT, p, "*.csv"))
        if len(dst_csvs) >= len(src_files):
            print(f"[skip] {p}: al uitgepakt ({len(dst_csvs)}/{len(src_files)})")
            continue
        todo.append(p)
    print(f"Te verwerken: {todo}")

    if not todo:
        print("Niets te doen.")
        return

    grand_t0 = time.time()
    grand_ok = grand_skip = grand_err = 0
    grand_bytes = 0
    for p in todo:
        _, ok, skip, err, total = process_pair(p)
        grand_ok += ok
        grand_skip += skip
        grand_err += err
        grand_bytes += total

    grand_elapsed = time.time() - grand_t0
    print(f"\n{'='*70}")
    print(f"KLAAR in {grand_elapsed:.1f}s")
    print(f"  paren verwerkt: {len(todo)}")
    print(f"  ok={grand_ok}  skip={grand_skip}  err={grand_err}")
    print(f"  totaal uitgepakt: {grand_bytes/1024/1024/1024:.2f} GB")


if __name__ == "__main__":
    main()