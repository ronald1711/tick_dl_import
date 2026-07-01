# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tooling to download, decompress, quality-assess, and import historical Forex tick data (2004–2026) from Dukascopy for 7 major currency pairs (AUDUSD, EURUSD, GBPUSD, NZDUSD, USDCAD, USDCHF, USDJPY) into a QuestDB database. There is no test suite, package manifest, or build step — this is a collection of standalone Python scripts run directly with `python <script>.py`. Comments and CLI output are in Dutch.

## Pipeline & Commands

The pipeline runs in stages, each a separate script:

1. **Download** (`download_majors.py`): fetches missing 2020–2026 data via `findatapy`'s Dukascopy source (older years assumed already present locally). Resumable — already-downloaded months are skipped.
   ```bash
   python download_majors.py GBPUSD   # single pair
   python download_majors.py          # all pairs
   ```
2. **Decompress** (`decompress_majors.py`, `decompress_gbpusd.py`): unpacks `.csv.zst` archives from a source drive into per-pair CSV files, multi-threaded per pair, pairs processed sequentially to limit disk thrashing.
3. **Quality assessment** (`assess_majors.py`, `assess_usdjpy.py`): samples the first 1M rows of each year's CSV, detects the Ask/Bid column swap, computes spread/gaps/jumps/zero-volume stats. Produces `<PAIR>_quality_results.{csv,md}` and `data_quality_assessment_<PAIR>.md`.
4. **QuestDB diagnose** (`questdb_diagnose.py`): reports which pair/year combinations already exist in QuestDB and their row counts.
   ```bash
   python questdb_diagnose.py
   ```
5. **Import** (`questdb_import.py` for the remote HP server, `questdb_import_local.py` when running directly on the server): reads CSVs chunk-by-chunk, reformats them, and uploads via QuestDB's `/imp` HTTP endpoint once per year. Never overwrites years already present unless told to.
   ```bash
   python questdb_import.py EURUSD              # missing years only
   python questdb_import.py EURUSD --all         # all years
   python questdb_import.py EURUSD 2015 2016     # specific years
   ```
   `questdb_import_local.py` has identical logic/CLI but points at `127.0.0.1` and `DATA_ROOT = /mnt/ssd/forexdata` instead of the remote server/Windows path — keep the two files in sync when changing import logic.

   `questdb_import_ilp_local.py` is a faster local-only alternative: same CLI/pair logic, but streams each chunk directly to QuestDB via the ILP protocol (`questdb.ingress.Sender`, HTTP transport on port 9000) instead of writing a temp CSV and POSTing it to `/imp`. About 60% faster locally (~110k rows/s vs ~70k rows/s) since there's no temp-file round-trip and no server-side CSV reparsing — but it requires `pandas`, `pyarrow`, and the `questdb` client package, and only makes sense when the script runs on the same host as QuestDB (compression/HTTP overhead tradeoffs assume no real network in between). Its `get_existing_years()` checks per-year row counts (partition-pruned) instead of a full-table `DISTINCT year(ts)` scan, since the latter times out once the table passes ~1-2 billion rows.

   **Known issue**: `--all` always reimports every locally available year regardless of what's already in QuestDB, and QuestDB has no `DELETE` support (in any edition) to clean up accidental duplicates afterward — the only fix is rebuilding the whole table via `CREATE TABLE ... AS SELECT DISTINCT`. Check `questdb_diagnose.py` or a per-year `SELECT count() FROM ticks WHERE symbol='<PAIR>' AND ts IN '<year>'` before running `--all` on a pair/year that might already be loaded. See `QUESTDB_IMPORT_README.md` for a documented instance of this (USDCAD 2005) and its impact (tick-count/volume aggregates 2x for that year; OHLC prices unaffected).

`smoke_test_findatapy.py` and `smoke_compare.py` are one-off exploratory scripts used to characterize the Dukascopy `findatapy` output format against the existing historical CSV convention — not part of the regular pipeline.

## Critical Data Quirk: Ask/Bid Column Swap

Dukascopy's raw CSV files have the `AskPrice`/`BidPrice` columns consistently swapped (`AskPrice` actually holds the bid, and vice versa). Every assessment and import script detects and corrects this automatically — when touching this logic, preserve the correction rather than "fixing" it away. USDCHF additionally contains the 2015 SNB Black Swan move and out-of-order rows in 2010 that must be sorted.

Pip factor: USDJPY uses `0.01` per pip; all other pairs use `0.0001` (see `pip_factor_for()` in `assess_majors.py`).

## QuestDB Schema

Single table `ticks`, partitioned by day, timestamp column `ts`:
```sql
ticks (
    symbol   SYMBOL,
    ts       TIMESTAMP,
    bid      DOUBLE,
    ask      DOUBLE,
    spread   DOUBLE,
    volume   DOUBLE
) timestamp(ts) PARTITION BY DAY;
```
`spread` and `volume` are computed at import time (`ask - bid`, `AskVolume + BidVolume` after the swap correction).

## Config Constants

Scripts hardcode config at the top of the file rather than reading env vars/config files:
- `DATA_ROOT`: local CSV directory root (differs between the Windows dev machine, `C:\projecten\forexdata`, and the Linux server, `/mnt/ssd/forexdata` in `questdb_import_local.py`).
- `QUESTDB_HOST` / `QUESTDB_PORT`: `192.168.10.33:9000` (HP server) for remote scripts, `127.0.0.1:9000` for local-server scripts.
- Import chunk size and per-year sleep are tuned in `questdb_import.py` (`CHUNK_SIZE`, `SLEEP_BETWEEN_YEARS`).

When adding a new environment variant of a script, check `DATA_ROOT`/`QUESTDB_HOST` first — this is the main thing that changes between machines.

## Dependencies

Uses `pandas`, `numpy`, `requests`, `zstandard`, and `findatapy` (for Dukascopy downloads only — not installed in this environment; only relevant to `download_majors.py`/`smoke_test_findatapy.py`). No dependency manifest exists; install ad hoc as needed.
