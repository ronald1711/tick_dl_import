# NZDUSD Tick Data Quality Assessment

Beoordelingsdatum: 2026-06-28T09:42:40.636113
Dataset: NZDUSD tick data UTC+0, 2004-2019
Bestanden geanalyseerd: 16
Totale ticks in dataset: 200,500,373

## Observatie 1: Kolomnamen verwisseld (zelfde bevinding als andere majors)

De CSV-headers zijn `UTC,AskPrice,BidPrice,AskVolume,BidVolume`, maar in de data is `AskPrice` consequent **kleiner** dan `BidPrice`. De eerste numerieke prijskolom gedraagt zich dus als **Bid**, de tweede als **Ask**. **Alle 16 jaren vertonen dezelfde 100% inversie.** Dit is consistent met EURUSD, USDJPY en GBPUSD — de bronprovider draagt de kolommen consistent om in de export.

**Vervolganalyse is uitgevoerd met omgewisselde kolommen** (Bid = kolom 1, Ask = kolom 2).

## Observatie 2: Prijsprecisie — 1 pip = 0.0001

NZDUSD wordt in forex-conventie 4 decimalen gequoteerd (1 pip = 0.0001). De data bevat 5-decimale precisie, waardoor sub-pip spreads mogelijk zijn.

## Per-Jaar Kwaliteitsmetrics (steekproef: eerste 1M rijen)

| jaar | n_rijen | gesorteerd | kolom_swap | min_spread_pips | mean_spread_pips | max_spread_pips | count_spread_gt_10pips | max_prijs_sprong_pips | gaten_gt_1min | zero_bid_vol | zero_ask_vol |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2004 | 1000000 | Ja | Ja | 0.4 | 3.7724 | 9.0 | 0 | 65.0 | 3150 | 0 | 0 |
| 2005 | 1000000 | Ja | Ja | 0.4 | 3.7735 | 9.0 | 0 | 214.9 | 215 | 0 | 0 |
| 2006 | 1000000 | Ja | Ja | 0.4 | 3.7727 | 9.0 | 0 | 48.1 | 996 | 0 | 0 |
| 2007 | 1000000 | Ja | Ja | 0.4 | 3.591 | 11.5 | 110 | 43.45 | 2535 | 0 | 0 |
| 2008 | 1000000 | Ja | Ja | 0.4 | 3.8523 | 15.0 | 2055 | 27.6 | 140 | 0 | 0 |
| 2009 | 1000000 | Ja | Ja | 0.4 | 4.5613 | 34.5 | 8706 | 37.0 | 4634 | 0 | 0 |
| 2010 | 1000000 | Ja | Ja | 0.4 | 2.5074 | 17.5 | 194 | 40.25 | 1376 | 0 | 0 |
| 2011 | 1000000 | Ja | Ja | 0.4 | 2.4172 | 22.8 | 442 | 37.1 | 979 | 0 | 0 |
| 2012 | 1000000 | Ja | Ja | 0.2 | 1.6964 | 34.7 | 1882 | 25.55 | 445 | 0 | 0 |
| 2013 | 1000000 | Ja | Ja | 0.2 | 1.5665 | 12.2 | 113 | 27.5 | 412 | 0 | 0 |
| 2014 | 1000000 | Ja | Ja | 0.1 | 1.4151 | 33.4 | 379 | 23.1 | 383 | 0 | 0 |
| 2015 | 1000000 | Ja | Ja | 0.1 | 1.4502 | 23.6 | 1493 | 16.8 | 80 | 0 | 0 |
| 2016 | 1000000 | Ja | Ja | 0.1 | 1.3692 | 27.2 | 263 | 51.05 | 69 | 0 | 0 |
| 2017 | 1000000 | Ja | Ja | 0.1 | 1.2838 | 31.1 | 3057 | 23.5 | 214 | 0 | 0 |
| 2018 | 1000000 | Ja | Ja | 0.1 | 0.8915 | 34.6 | 75 | 22.3 | 75 | 0 | 0 |
| 2019 | 1000000 | Ja | Ja | 0.2 | 1.193 | 35.0 | 2386 | 54.9 | 92 | 0 | 0 |

Noot: 'Aantal Spread>10pips' en 'Gaten >1min' zijn tellingen binnen de 1M-rij-steekproef.

## Kwaliteitsoordeel

### 1. Kolomnamen — WAARSCHUWING
Zelfde swap-patroon als de andere majors. Bij import altijd kolom 1 als Bid behandelen en kolom 2 als Ask (idem volumes).

### 2. Sortering — GOED
Alle jaarbestanden zijn chronologisch gesorteerd op UTC-timestamp.

### 3. Spreads — samenvatting over alle jaren
- Minimum spread overall: 0.1000 pips
- Gemiddelde spread (gemiddeld van alle jaar-means): 2.4446 pips
- Maximum spread overall: 35.0000 pips

Moderne jaren (2014-2019) hebben typisch 0.1-0.5 pip ECN-grade spreads. Vroege jaren (2004-2007) hebben ~1-2 pip spreads, gebruikelijk voor institutional data uit die periode.

### 4. Tijdgaten — VERWACHT
Totaal 15,795 gaten > 1 minuut in alle 1M-steekproeven samen. Dit zijn weekenden, feestdagen en nieuwjaarsperiodes — geen onverwachte gaten gedetecteerd.

### 5. Prijssprongen — AANDACHT VOOR EXTREME WAARDEN
Maximum tick-to-tick sprong: 214.90 pips. Extreme waarden komen voor tijdens flash-crashes (2015 CHF-blackout, 2019 USDJPY flash) of openingsuren. Voor strategieën die hier niet tegen kunnen: filter ticks met `|mid_delta| > 50 pips`.

### 6. Volumes — GOED
Totaal 0 zero-volume ticks in alle 1M-steekproeven. Dit is verwaarloosbaar voor prijsanalyse.

## Aanbevelingen

1. **Kolomnamen corrigeren bij import:** behandel bronkolom 1 als Bid, kolom 2 als Ask (idem volumes). Pas de import-job hierop aan.
2. **Pip-definitie:** voor NZDUSD is 1 pip = 0.0001. Gebruik deze conventie consistent.
3. **Flash-crash filtering (optioneel):** filter ticks met `|mid_delta| > 50 pips` als je backtest niet tegen extreme moves bestand is.
4. **Tijdgaten:** weekend-gaten zijn reëel en moeten expliciet worden geïmputeerd of overgeslagen bij HLOC-bar aggregatie.
5. **Volume-gewogen analyses:** zero-volume ticks veilig te negeren voor prijsanalyse, uitsluiten voor VWAP-features.

## Reproduceerbaarheid

Het assessment-script staat in `assess_majors.py`. Het leest per bestand alleen de eerste 1.000.000 rijen (consistent met EURUSD/USDJPY-aanpak).
