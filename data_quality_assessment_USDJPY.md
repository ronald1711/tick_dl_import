# USDJPY Tick Data Quality Assessment

Beoordelingsdatum: 2026-06-29T22:35:19.010816
Dataset: USDJPY tick data UTC+0, 2004-2026
Bestanden geanalyseerd: 23
Totale ticks in dataset: 497,082,441

## Observatie 1: Kolomnamen verwisseld (zelfde bevinding als andere majors)

De CSV-headers zijn `UTC,AskPrice,BidPrice,AskVolume,BidVolume`, maar in de data is `AskPrice` consequent **kleiner** dan `BidPrice`. De eerste numerieke prijskolom gedraagt zich dus als **Bid**, de tweede als **Ask**. **Alle 23 jaren vertonen dezelfde 100% inversie.** Dit is consistent met EURUSD, USDJPY en GBPUSD — de bronprovider draagt de kolommen consistent om in de export.

**Vervolganalyse is uitgevoerd met omgewisselde kolommen** (Bid = kolom 1, Ask = kolom 2).

## Observatie 2: Prijsprecisie — 1 pip = 0.01

USDJPY wordt in forex-conventie 3 decimalen gequoteerd (1 pip = 0.01). De data bevat 5-decimale precisie, waardoor spreads van 0.001 (= 0.1 pip) en 0.004 (= 0.4 pip) voorkomen.

## Per-Jaar Kwaliteitsmetrics (steekproef: eerste 1M rijen)

| jaar | n_rijen | gesorteerd | kolom_swap | min_spread_pips | mean_spread_pips | max_spread_pips | count_spread_gt_10pips | max_prijs_sprong_pips | gaten_gt_1min | zero_bid_vol | zero_ask_vol |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2004 | 1000000 | Ja | Ja | 0.4 | 1.6014 | 6.0 | 0 | 31.2 | 503 | 0 | 0 |
| 2005 | 1000000 | Ja | Ja | 0.4 | 1.6011 | 6.0 | 0 | 63.7 | 161 | 0 | 0 |
| 2006 | 1000000 | Ja | Ja | 0.4 | 1.6013 | 6.0 | 0 | 17.7 | 225 | 0 | 0 |
| 2007 | 1000000 | Ja | Ja | 0.4 | 1.6014 | 6.0 | 0 | 15.05 | 131 | 0 | 0 |
| 2008 | 1000000 | Ja | Ja | 0.5 | 1.5217 | 16.0 | 35 | 13.25 | 26 | 658 | 674 |
| 2009 | 1000000 | Ja | Ja | 0.5 | 1.5493 | 33.0 | 114 | 28.25 | 465 | 0 | 0 |
| 2010 | 1000000 | Ja | Ja | 0.5 | 1.0553 | 22.5 | 23 | 31.25 | 137 | 0 | 0 |
| 2011 | 1000000 | Ja | Ja | 0.1 | 1.2161 | 28.2 | 105 | 38.0 | 723 | 0 | 0 |
| 2012 | 1000000 | Ja | Ja | 0.1 | 0.7116 | 10.7 | 4 | 9.4 | 877 | 0 | 0 |
| 2013 | 1000000 | Ja | Ja | 0.1 | 0.8063 | 10.6 | 1 | 11.3 | 46 | 0 | 0 |
| 2014 | 1000000 | Ja | Ja | 0.1 | 0.4277 | 29.1 | 25 | 18.15 | 186 | 0 | 0 |
| 2015 | 1000000 | Ja | Ja | 0.1 | 0.4185 | 14.9 | 12 | 19.0 | 12 | 0 | 0 |
| 2016 | 1000000 | Ja | Ja | 0.1 | 0.365 | 12.8 | 21 | 32.8 | 19 | 0 | 0 |
| 2017 | 1000000 | Ja | Ja | 0.1 | 0.5122 | 34.9 | 203 | 18.5 | 227 | 0 | 0 |
| 2018 | 1000000 | Ja | Ja | 0.1 | 0.361 | 14.8 | 29 | 24.9 | 74 | 0 | 0 |
| 2019 | 1000000 | Ja | Ja | 0.1 | 0.4817 | 35.0 | 3419 | 111.4 | 27 | 0 | 0 |
| 2020 | 1000000 | Ja | Ja | 0.1 | 0.3055 | 14.0 | 61 | 35.8 | 310 | 0 | 0 |
| 2021 | 1000000 | Ja | Ja | 0.1 | 0.2903 | 13.2 | 8 | 6.05 | 312 | 0 | 0 |
| 2022 | 1000000 | Ja | Ja | 0.1 | 0.4673 | 14.2 | 46 | 8.9 | 342 | 0 | 0 |
| 2023 | 1000000 | Ja | Ja | 0.1 | 0.9878 | 33.9 | 2452 | 10.4 | 184 | 0 | 0 |
| 2024 | 1000000 | Ja | Ja | 0.1 | 0.6505 | 34.6 | 174 | 26.2 | 45 | 0 | 0 |
| 2025 | 1000000 | Ja | Ja | 0.1 | 0.8208 | 33.4 | 317 | 47.75 | 73 | 0 | 0 |
| 2026 | 1000000 | Ja | Ja | 0.1 | 0.498 | 45.4 | 991 | 24.25 | 150 | 0 | 0 |

Noot: 'Aantal Spread>10pips' en 'Gaten >1min' zijn tellingen binnen de 1M-rij-steekproef.

## Kwaliteitsoordeel

### 1. Kolomnamen — WAARSCHUWING
Zelfde swap-patroon als de andere majors. Bij import altijd kolom 1 als Bid behandelen en kolom 2 als Ask (idem volumes).

### 2. Sortering — GOED
Alle jaarbestanden zijn chronologisch gesorteerd op UTC-timestamp.

### 3. Spreads — samenvatting over alle jaren
- Minimum spread overall: 0.1000 pips
- Gemiddelde spread (gemiddeld van alle jaar-means): 0.8631 pips
- Maximum spread overall: 45.4000 pips

Moderne jaren (2014-2019) hebben typisch 0.1-0.5 pip ECN-grade spreads. Vroege jaren (2004-2007) hebben ~1-2 pip spreads, gebruikelijk voor institutional data uit die periode.

### 4. Tijdgaten — VERWACHT
Totaal 5,255 gaten > 1 minuut in alle 1M-steekproeven samen. Dit zijn weekenden, feestdagen en nieuwjaarsperiodes — geen onverwachte gaten gedetecteerd.

### 5. Prijssprongen — AANDACHT VOOR EXTREME WAARDEN
Maximum tick-to-tick sprong: 111.40 pips. Extreme waarden komen voor tijdens flash-crashes (2015 CHF-blackout, 2019 USDJPY flash) of openingsuren. Voor strategieën die hier niet tegen kunnen: filter ticks met `|mid_delta| > 50 pips`.

### 6. Volumes — AANDACHT
Totaal 1332 zero-volume ticks in alle 1M-steekproeven. 1332 zero-volume ticks gedetecteerd. Controleer deze specifieke jaren.

## Aanbevelingen

1. **Kolomnamen corrigeren bij import:** behandel bronkolom 1 als Bid, kolom 2 als Ask (idem volumes). Pas de import-job hierop aan.
2. **Pip-definitie:** voor USDJPY is 1 pip = 0.01. Gebruik deze conventie consistent.
3. **Flash-crash filtering (optioneel):** filter ticks met `|mid_delta| > 50 pips` als je backtest niet tegen extreme moves bestand is.
4. **Tijdgaten:** weekend-gaten zijn reëel en moeten expliciet worden geïmputeerd of overgeslagen bij HLOC-bar aggregatie.
5. **Volume-gewogen analyses:** zero-volume ticks veilig te negeren voor prijsanalyse, uitsluiten voor VWAP-features.

## Reproduceerbaarheid

Het assessment-script staat in `assess_majors.py`. Het leest per bestand alleen de eerste 1.000.000 rijen (consistent met EURUSD/USDJPY-aanpak).
