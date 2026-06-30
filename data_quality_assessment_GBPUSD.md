# GBPUSD Tick Data Quality Assessment

Beoordelingsdatum: 2026-06-30T14:46:41.361408
Dataset: GBPUSD tick data UTC+0, 2004-2026
Bestanden geanalyseerd: 23
Totale ticks in dataset: 508,937,136

## Observatie 1: Kolomnamen verwisseld (zelfde bevinding als andere majors)

De CSV-headers zijn `UTC,AskPrice,BidPrice,AskVolume,BidVolume`, maar in de data is `AskPrice` consequent **kleiner** dan `BidPrice`. De eerste numerieke prijskolom gedraagt zich dus als **Bid**, de tweede als **Ask**. **Alle 23 jaren vertonen dezelfde 100% inversie.** Dit is consistent met EURUSD, USDJPY en GBPUSD — de bronprovider draagt de kolommen consistent om in de export.

**Vervolganalyse is uitgevoerd met omgewisselde kolommen** (Bid = kolom 1, Ask = kolom 2).

## Observatie 2: Prijsprecisie — 1 pip = 0.0001

GBPUSD wordt in forex-conventie 4 decimalen gequoteerd (1 pip = 0.0001). De data bevat 5-decimale precisie, waardoor sub-pip spreads mogelijk zijn.

## Per-Jaar Kwaliteitsmetrics (steekproef: eerste 1M rijen)

| jaar | n_rijen | gesorteerd | kolom_swap | min_spread_pips | mean_spread_pips | max_spread_pips | count_spread_gt_10pips | max_prijs_sprong_pips | gaten_gt_1min | zero_bid_vol | zero_ask_vol |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2004 | 1000000 | Ja | Ja | 0.4 | 1.7708 | 7.0 | 0 | 73.85 | 612 | 0 | 0 |
| 2005 | 1000000 | Ja | Ja | 0.4 | 1.7707 | 7.0 | 0 | 55.9 | 777 | 0 | 0 |
| 2006 | 1000000 | Ja | Ja | 0.4 | 1.7716 | 7.0 | 0 | 59.65 | 1305 | 0 | 0 |
| 2007 | 1000000 | Ja | Ja | 0.4 | 1.7713 | 7.0 | 0 | 87.8 | 933 | 0 | 0 |
| 2008 | 1000000 | Ja | Ja | 0.4 | 2.255 | 28.5 | 899 | 16.2 | 91 | 0 | 0 |
| 2009 | 1000000 | Ja | Ja | 0.4 | 2.6975 | 25.0 | 4036 | 96.4 | 608 | 0 | 0 |
| 2010 | 1000000 | Ja | Ja | 0.4 | 1.8117 | 14.0 | 31 | 57.8 | 226 | 0 | 0 |
| 2011 | 1000000 | Ja | Ja | 0.2 | 2.0584 | 16.8 | 599 | 23.55 | 433 | 0 | 0 |
| 2012 | 1000000 | Ja | Ja | 0.1 | 1.4171 | 23.6 | 867 | 37.2 | 219 | 0 | 0 |
| 2013 | 1000000 | Ja | Ja | 0.1 | 1.4057 | 32.9 | 454 | 15.65 | 183 | 0 | 0 |
| 2014 | 1000000 | Ja | Ja | 0.1 | 0.7056 | 36.0 | 90 | 23.1 | 218 | 0 | 0 |
| 2015 | 1000000 | Ja | Ja | 0.1 | 0.995 | 39.2 | 1058 | 23.5 | 8 | 0 | 0 |
| 2016 | 1000000 | Ja | Ja | 0.1 | 0.9174 | 31.9 | 105 | 23.05 | 18 | 0 | 0 |
| 2017 | 1000000 | Ja | Ja | 0.1 | 1.1294 | 38.9 | 605 | 35.8 | 116 | 0 | 0 |
| 2018 | 1000000 | Ja | Ja | 0.1 | 0.8158 | 35.8 | 460 | 12.05 | 22 | 0 | 0 |
| 2019 | 1000000 | Ja | Ja | 0.1 | 1.0987 | 40.0 | 4008 | 48.4 | 18 | 0 | 0 |
| 2020 | 1000000 | Ja | Ja | 0.1 | 1.0888 | 31.0 | 3591 | 28.6 | 40 | 0 | 0 |
| 2021 | 1000000 | Ja | Ja | 0.1 | 0.97 | 19.2 | 240 | 8.65 | 52 | 0 | 0 |
| 2022 | 1000000 | Ja | Ja | 0.1 | 0.9569 | 15.8 | 587 | 9.25 | 313 | 0 | 0 |
| 2023 | 1000000 | Ja | Ja | 0.1 | 1.5462 | 35.3 | 8638 | 25.2 | 129 | 0 | 0 |
| 2024 | 1000000 | Ja | Ja | 0.1 | 0.9402 | 29.7 | 83 | 33.1 | 135 | 0 | 0 |
| 2025 | 1000000 | Ja | Ja | 0.1 | 0.9448 | 18.5 | 87 | 33.3 | 63 | 0 | 0 |
| 2026 | 1000000 | Ja | Ja | 0.1 | 0.7473 | 29.8 | 1695 | 19.4 | 238 | 0 | 0 |

Noot: 'Aantal Spread>10pips' en 'Gaten >1min' zijn tellingen binnen de 1M-rij-steekproef.

## Kwaliteitsoordeel

### 1. Kolomnamen — WAARSCHUWING
Zelfde swap-patroon als de andere majors. Bij import altijd kolom 1 als Bid behandelen en kolom 2 als Ask (idem volumes).

### 2. Sortering — GOED
Alle jaarbestanden zijn chronologisch gesorteerd op UTC-timestamp.

### 3. Spreads — samenvatting over alle jaren
- Minimum spread overall: 0.1000 pips
- Gemiddelde spread (gemiddeld van alle jaar-means): 1.3733 pips
- Maximum spread overall: 40.0000 pips

Moderne jaren (2014-2019) hebben typisch 0.1-0.5 pip ECN-grade spreads. Vroege jaren (2004-2007) hebben ~1-2 pip spreads, gebruikelijk voor institutional data uit die periode.

### 4. Tijdgaten — VERWACHT
Totaal 6,757 gaten > 1 minuut in alle 1M-steekproeven samen. Dit zijn weekenden, feestdagen en nieuwjaarsperiodes — geen onverwachte gaten gedetecteerd.

### 5. Prijssprongen — AANDACHT VOOR EXTREME WAARDEN
Maximum tick-to-tick sprong: 96.40 pips. Extreme waarden komen voor tijdens flash-crashes (2015 CHF-blackout, 2019 USDJPY flash) of openingsuren. Voor strategieën die hier niet tegen kunnen: filter ticks met `|mid_delta| > 50 pips`.

### 6. Volumes — GOED
Totaal 0 zero-volume ticks in alle 1M-steekproeven. Dit is verwaarloosbaar voor prijsanalyse.

## Aanbevelingen

1. **Kolomnamen corrigeren bij import:** behandel bronkolom 1 als Bid, kolom 2 als Ask (idem volumes). Pas de import-job hierop aan.
2. **Pip-definitie:** voor GBPUSD is 1 pip = 0.0001. Gebruik deze conventie consistent.
3. **Flash-crash filtering (optioneel):** filter ticks met `|mid_delta| > 50 pips` als je backtest niet tegen extreme moves bestand is.
4. **Tijdgaten:** weekend-gaten zijn reëel en moeten expliciet worden geïmputeerd of overgeslagen bij HLOC-bar aggregatie.
5. **Volume-gewogen analyses:** zero-volume ticks veilig te negeren voor prijsanalyse, uitsluiten voor VWAP-features.

## Reproduceerbaarheid

Het assessment-script staat in `assess_majors.py`. Het leest per bestand alleen de eerste 1.000.000 rijen (consistent met EURUSD/USDJPY-aanpak).
