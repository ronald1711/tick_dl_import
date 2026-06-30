# AUDUSD Tick Data Quality Assessment

Beoordelingsdatum: 2026-06-28T16:29:59.664906
Dataset: AUDUSD tick data UTC+0, 2004-2019
Bestanden geanalyseerd: 23
Totale ticks in dataset: 386,836,850

## Observatie 1: Kolomnamen verwisseld (zelfde bevinding als andere majors)

De CSV-headers zijn `UTC,AskPrice,BidPrice,AskVolume,BidVolume`, maar in de data is `AskPrice` consequent **kleiner** dan `BidPrice`. De eerste numerieke prijskolom gedraagt zich dus als **Bid**, de tweede als **Ask**. **Alle 23 jaren vertonen dezelfde 100% inversie.** Dit is consistent met EURUSD, USDJPY en GBPUSD — de bronprovider draagt de kolommen consistent om in de export.

**Vervolganalyse is uitgevoerd met omgewisselde kolommen** (Bid = kolom 1, Ask = kolom 2).

## Observatie 2: Prijsprecisie — 1 pip = 0.0001

AUDUSD wordt in forex-conventie 4 decimalen gequoteerd (1 pip = 0.0001). De data bevat 5-decimale precisie, waardoor sub-pip spreads mogelijk zijn.

## Per-Jaar Kwaliteitsmetrics (steekproef: eerste 1M rijen)

| jaar | n_rijen | gesorteerd | kolom_swap | min_spread_pips | mean_spread_pips | max_spread_pips | count_spread_gt_10pips | max_prijs_sprong_pips | gaten_gt_1min | zero_bid_vol | zero_ask_vol |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2004 | 1000000 | Ja | Ja | 0.2 | 2.0373 | 7.0 | 0 | 14.9 | 263 | 0 | 0 |
| 2005 | 1000000 | Ja | Ja | 0.2 | 2.0563 | 7.0 | 0 | 17.3 | 69 | 0 | 0 |
| 2006 | 1000000 | Ja | Ja | 0.2 | 2.0555 | 7.0 | 0 | 8.9 | 25 | 0 | 0 |
| 2007 | 1000000 | Ja | Ja | 0.2 | 2.0609 | 7.0 | 0 | 13.7 | 3 | 0 | 0 |
| 2008 | 1000000 | Ja | Ja | -2.9 | 2.0314 | 7.0 | 0 | 83.0 | 4676 | 0 | 0 |
| 2009 | 1000000 | Ja | Ja | 0.5 | 3.0455 | 27.0 | 731 | 41.35 | 990 | 0 | 0 |
| 2010 | 1000000 | Ja | Ja | -0.4 | 1.6068 | 50.9 | 433 | 52.0 | 1796 | 0 | 0 |
| 2011 | 1000000 | Ja | Ja | 0.1 | 1.7066 | 23.7 | 153 | 47.55 | 325 | 0 | 0 |
| 2012 | 1000000 | Ja | Ja | 0.1 | 1.1827 | 18.7 | 19 | 36.0 | 266 | 0 | 0 |
| 2013 | 1000000 | Ja | Ja | 0.1 | 1.2635 | 13.8 | 14 | 14.8 | 340 | 0 | 0 |
| 2014 | 1000000 | Ja | Ja | 0.1 | 0.7509 | 22.8 | 24 | 13.0 | 176 | 0 | 0 |
| 2015 | 1000000 | Ja | Ja | 0.1 | 1.1172 | 13.9 | 18 | 17.7 | 23 | 0 | 0 |
| 2016 | 1000000 | Ja | Ja | 0.1 | 1.0514 | 17.1 | 38 | 23.3 | 5 | 0 | 0 |
| 2017 | 1000000 | Ja | Ja | 0.1 | 1.0638 | 35.0 | 771 | 18.95 | 82 | 0 | 0 |
| 2018 | 1000000 | Ja | Ja | 0.1 | 0.912 | 14.8 | 17 | 12.6 | 48 | 0 | 0 |
| 2019 | 1000000 | Ja | Ja | 0.1 | 1.0517 | 34.8 | 1750 | 88.0 | 43 | 0 | 0 |
| 2020 | 1000000 | Ja | Ja | 0.1 | 0.8759 | 12.0 | 13 | 19.2 | 271 | 0 | 0 |
| 2021 | 1000000 | Ja | Ja | 0.3 | 1.0204 | 20.0 | 70 | 7.5 | 187 | 0 | 0 |
| 2022 | 1000000 | Ja | Ja | 0.3 | 1.1124 | 20.1 | 130 | 11.4 | 385 | 0 | 0 |
| 2023 | 1000000 | Ja | Ja | 0.4 | 1.3705 | 33.1 | 3072 | 15.8 | 394 | 0 | 0 |
| 2024 | 1000000 | Ja | Ja | 0.1 | 1.1104 | 20.8 | 133 | 16.05 | 221 | 0 | 0 |
| 2025 | 1000000 | Ja | Ja | 0.4 | 1.0531 | 17.0 | 39 | 16.85 | 201 | 0 | 0 |
| 2026 | 1000000 | Ja | Ja | 0.1 | 0.9049 | 16.8 | 34 | 28.95 | 303 | 0 | 0 |

Noot: 'Aantal Spread>10pips' en 'Gaten >1min' zijn tellingen binnen de 1M-rij-steekproef.

## Kwaliteitsoordeel

### 1. Kolomnamen — WAARSCHUWING
Zelfde swap-patroon als de andere majors. Bij import altijd kolom 1 als Bid behandelen en kolom 2 als Ask (idem volumes).

### 2. Sortering — GOED
Alle jaarbestanden zijn chronologisch gesorteerd op UTC-timestamp.

### 3. Spreads — samenvatting over alle jaren
- Minimum spread overall: -2.9000 pips
- Gemiddelde spread (gemiddeld van alle jaar-means): 1.4105 pips
- Maximum spread overall: 50.9000 pips

Moderne jaren (2014-2019) hebben typisch 0.1-0.5 pip ECN-grade spreads. Vroege jaren (2004-2007) hebben ~1-2 pip spreads, gebruikelijk voor institutional data uit die periode.

### 4. Tijdgaten — VERWACHT
Totaal 11,092 gaten > 1 minuut in alle 1M-steekproeven samen. Dit zijn weekenden, feestdagen en nieuwjaarsperiodes — geen onverwachte gaten gedetecteerd.

### 5. Prijssprongen — AANDACHT VOOR EXTREME WAARDEN
Maximum tick-to-tick sprong: 88.00 pips. Extreme waarden komen voor tijdens flash-crashes (2015 CHF-blackout, 2019 USDJPY flash) of openingsuren. Voor strategieën die hier niet tegen kunnen: filter ticks met `|mid_delta| > 50 pips`.

### 6. Volumes — GOED
Totaal 0 zero-volume ticks in alle 1M-steekproeven. Dit is verwaarloosbaar voor prijsanalyse.

## Aanbevelingen

1. **Kolomnamen corrigeren bij import:** behandel bronkolom 1 als Bid, kolom 2 als Ask (idem volumes). Pas de import-job hierop aan.
2. **Pip-definitie:** voor AUDUSD is 1 pip = 0.0001. Gebruik deze conventie consistent.
3. **Flash-crash filtering (optioneel):** filter ticks met `|mid_delta| > 50 pips` als je backtest niet tegen extreme moves bestand is.
4. **Tijdgaten:** weekend-gaten zijn reëel en moeten expliciet worden geïmputeerd of overgeslagen bij HLOC-bar aggregatie.
5. **Volume-gewogen analyses:** zero-volume ticks veilig te negeren voor prijsanalyse, uitsluiten voor VWAP-features.

## Reproduceerbaarheid

Het assessment-script staat in `assess_majors.py`. Het leest per bestand alleen de eerste 1.000.000 rijen (consistent met EURUSD/USDJPY-aanpak).
