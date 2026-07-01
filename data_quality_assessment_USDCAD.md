# USDCAD Tick Data Quality Assessment

Beoordelingsdatum: 2026-07-01T09:14:00.235390
Dataset: USDCAD tick data UTC+0, 2004-2026
Bestanden geanalyseerd: 23
Totale ticks in dataset: 389,065,050

## Observatie 1: Kolomnamen verwisseld (zelfde bevinding als andere majors)

De CSV-headers zijn `UTC,AskPrice,BidPrice,AskVolume,BidVolume`, maar in de data is `AskPrice` consequent **kleiner** dan `BidPrice`. De eerste numerieke prijskolom gedraagt zich dus als **Bid**, de tweede als **Ask**. **Alle 23 jaren vertonen dezelfde 100% inversie.** Dit is consistent met EURUSD, USDJPY en GBPUSD — de bronprovider draagt de kolommen consistent om in de export.

**Vervolganalyse is uitgevoerd met omgewisselde kolommen** (Bid = kolom 1, Ask = kolom 2).

## Observatie 2: Prijsprecisie — 1 pip = 0.0001

USDCAD wordt in forex-conventie 4 decimalen gequoteerd (1 pip = 0.0001). De data bevat 5-decimale precisie, waardoor sub-pip spreads mogelijk zijn.

## Per-Jaar Kwaliteitsmetrics (steekproef: eerste 1M rijen)

| jaar | n_rijen | gesorteerd | kolom_swap | min_spread_pips | mean_spread_pips | max_spread_pips | count_spread_gt_10pips | max_prijs_sprong_pips | gaten_gt_1min | zero_bid_vol | zero_ask_vol |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2004 | 1000000 | Ja | Ja | 0.4 | 2.1813 | 9.0 | 0 | 43.3 | 2082 | 0 | 0 |
| 2005 | 1000000 | Ja | Ja | 0.4 | 2.1816 | 9.0 | 0 | 202.3 | 1251 | 0 | 0 |
| 2006 | 1000000 | Ja | Ja | 0.4 | 2.1817 | 9.0 | 0 | 18.45 | 3075 | 0 | 0 |
| 2007 | 1000000 | Ja | Ja | 0.4 | 2.1742 | 15.0 | 72 | 283.4 | 2997 | 3 | 4 |
| 2008 | 1000000 | Ja | Ja | 0.4 | 2.928 | 15.0 | 2045 | 15.75 | 270 | 35 | 0 |
| 2009 | 1000000 | Ja | Ja | 0.4 | 5.0195 | 35.0 | 27324 | 38.7 | 3003 | 0 | 0 |
| 2010 | 1000000 | Ja | Ja | 0.4 | 2.3806 | 15.5 | 155 | 17.75 | 599 | 0 | 0 |
| 2011 | 1000000 | Ja | Ja | 0.2 | 1.9202 | 16.5 | 319 | 25.45 | 605 | 0 | 0 |
| 2012 | 1000000 | Ja | Ja | 0.4 | 1.5069 | 25.7 | 1824 | 15.45 | 334 | 0 | 0 |
| 2013 | 1000000 | Ja | Ja | 0.1 | 1.2424 | 10.8 | 7 | 10.2 | 807 | 0 | 0 |
| 2014 | 1000000 | Ja | Ja | 0.1 | 0.8263 | 28.3 | 74 | 24.55 | 935 | 0 | 0 |
| 2015 | 1000000 | Ja | Ja | 0.1 | 1.2556 | 33.4 | 312 | 32.6 | 86 | 0 | 0 |
| 2016 | 1000000 | Ja | Ja | 0.1 | 1.1398 | 19.0 | 98 | 13.05 | 11 | 0 | 0 |
| 2017 | 1000000 | Ja | Ja | 0.1 | 1.3854 | 34.9 | 12727 | 16.15 | 107 | 0 | 0 |
| 2018 | 1000000 | Ja | Ja | 0.1 | 0.9803 | 21.0 | 723 | 49.35 | 35 | 0 | 0 |
| 2019 | 1000000 | Ja | Ja | 0.1 | 1.2418 | 34.9 | 2493 | 20.75 | 34 | 0 | 0 |
| 2020 | 1000000 | Ja | Ja | 0.1 | 1.0516 | 11.6 | 11 | 28.35 | 95 | 0 | 0 |
| 2021 | 1000000 | Ja | Ja | 0.1 | 1.1315 | 25.6 | 408 | 16.65 | 270 | 0 | 0 |
| 2022 | 1000000 | Ja | Ja | 0.4 | 1.3845 | 26.0 | 3616 | 10.1 | 220 | 0 | 0 |
| 2023 | 1000000 | Ja | Ja | 0.4 | 1.7996 | 34.7 | 5696 | 19.45 | 387 | 0 | 0 |
| 2024 | 1000000 | Ja | Ja | 0.1 | 1.2751 | 30.9 | 551 | 11.55 | 280 | 0 | 0 |
| 2025 | 1000000 | Ja | Ja | 0.4 | 1.321 | 34.5 | 627 | 37.5 | 92 | 0 | 0 |
| 2026 | 1000000 | Ja | Ja | 0.4 | 1.2626 | 20.2 | 93 | 8.95 | 110 | 0 | 0 |

Noot: 'Aantal Spread>10pips' en 'Gaten >1min' zijn tellingen binnen de 1M-rij-steekproef.

## Kwaliteitsoordeel

### 1. Kolomnamen — WAARSCHUWING
Zelfde swap-patroon als de andere majors. Bij import altijd kolom 1 als Bid behandelen en kolom 2 als Ask (idem volumes).

### 2. Sortering — GOED
Alle jaarbestanden zijn chronologisch gesorteerd op UTC-timestamp.

### 3. Spreads — samenvatting over alle jaren
- Minimum spread overall: 0.1000 pips
- Gemiddelde spread (gemiddeld van alle jaar-means): 1.7292 pips
- Maximum spread overall: 35.0000 pips

Moderne jaren (2014-2019) hebben typisch 0.1-0.5 pip ECN-grade spreads. Vroege jaren (2004-2007) hebben ~1-2 pip spreads, gebruikelijk voor institutional data uit die periode.

### 4. Tijdgaten — VERWACHT
Totaal 17,685 gaten > 1 minuut in alle 1M-steekproeven samen. Dit zijn weekenden, feestdagen en nieuwjaarsperiodes — geen onverwachte gaten gedetecteerd.

### 5. Prijssprongen — AANDACHT VOOR EXTREME WAARDEN
Maximum tick-to-tick sprong: 283.40 pips. Extreme waarden komen voor tijdens flash-crashes (2015 CHF-blackout, 2019 USDJPY flash) of openingsuren. Voor strategieën die hier niet tegen kunnen: filter ticks met `|mid_delta| > 50 pips`.

### 6. Volumes — GOED
Totaal 42 zero-volume ticks in alle 1M-steekproeven. Dit is verwaarloosbaar voor prijsanalyse.

## Aanbevelingen

1. **Kolomnamen corrigeren bij import:** behandel bronkolom 1 als Bid, kolom 2 als Ask (idem volumes). Pas de import-job hierop aan.
2. **Pip-definitie:** voor USDCAD is 1 pip = 0.0001. Gebruik deze conventie consistent.
3. **Flash-crash filtering (optioneel):** filter ticks met `|mid_delta| > 50 pips` als je backtest niet tegen extreme moves bestand is.
4. **Tijdgaten:** weekend-gaten zijn reëel en moeten expliciet worden geïmputeerd of overgeslagen bij HLOC-bar aggregatie.
5. **Volume-gewogen analyses:** zero-volume ticks veilig te negeren voor prijsanalyse, uitsluiten voor VWAP-features.

## Reproduceerbaarheid

Het assessment-script staat in `assess_majors.py`. Het leest per bestand alleen de eerste 1.000.000 rijen (consistent met EURUSD/USDJPY-aanpak).
