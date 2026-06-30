"""
Decomprimeer GBPUSD .zst archief naar CSV in C:\projecten\forexdata\GBPUSD.

ThreadPoolExecutor: bottleneck is disk-I/O, dus threads zijn prima
vermijdt ook de multiprocessing spawn-guard issues op Windows.
"""
import zstandard
import os
import glob
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

SRC_DIR = r"E:\majors\GBPUSD"
DST_DIR = r"C:\projecten\forexdata\GBPUSD"
os.makedirs(DST_DIR, exist_ok=True)

files = sorted(glob.glob(os.path.join(SRC_DIR, "*.csv.zst")))
print(f"Gevonden: {len(files)} bestanden in {SRC_DIR}")

def decompress(src):
    name = os.path.basename(src)
    dst = os.path.join(DST_DIR, name[: -len(".zst")])  # strip .zst suffix
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


def main():
    t_start = time.time()
    results = []
    # 6 workers: disk-head seeks beperken, maar wel concurrency op I/O
    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(decompress, f): f for f in files}
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            name, status = r[0], r[1]
            if status == "ok":
                _, _, dst_size, elapsed, ratio = r
                print(
                    f"  [OK ] {name:>55}  -> {dst_size/1024/1024:>7.1f} MB"
                    f"  ({elapsed:5.1f}s, {ratio:.1f}x)",
                    flush=True,
                )
            elif status == "skip":
                print(f"  [SKIP] {name}  (reeds uitgepakt)", flush=True)
            else:
                print(f"  [ERR] {name}: {r[2]}", flush=True)

    total_elapsed = time.time() - t_start
    ok_count = sum(1 for r in results if r[1] == "ok")
    skip_count = sum(1 for r in results if r[1] == "skip")
    err_count = sum(1 for r in results if r[1] == "error")
    total_size_mb = sum(r[2] for r in results if r[1] == "ok") / 1024 / 1024
    print(f"\nKlaar in {total_elapsed:.1f}s")
    print(f"  ok={ok_count}  skip={skip_count}  err={err_count}  totaal uitgepakt: {total_size_mb:.1f} MB")


if __name__ == "__main__":
    main()