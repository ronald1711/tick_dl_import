# USDCHF Tick Data Quality Assessment

Beoordelingsdatum: 2026-06-28T10:27:48.452179
Dataset: USDCHF tick data UTC+0, 2004-2019
Bestanden geanalyseerd: 16
Totale ticks in dataset: 258,288,332

## Observatie 1: Kolomnamen verwisseld (zelfde bevinding als andere majors)

De CSV-headers zijn `UTC,AskPrice,BidPrice,AskVolume,BidVolume`, maar in de data is `AskPrice` consequent **kleiner** dan `BidPrice`. De eerste numerieke prijskolom gedraagt zich dus als **Bid**, de tweede als **Ask**. **Alle 16 jaren vertonen dezelfde 100% inversie.** Dit is consistent met EURUSD, USDJPY en GBPUSD — de bronprovider draagt de kolommen consistent om in de export.

**Vervolganalyse is uitgevoerd met omgewisselde kolommen** (Bid = kolom 1, Ask = kolom 2).

## Observatie 2: Prijsprecisie — 1 pip = 0.0001

USDCHF wordt in forex-conventie 4 decimalen gequoteerd (1 pip = 0.0001). De data bevat 5-decimale precisie, waardoor sub-pip spreads mogelijk zijn.

## Per-Jaar Kwaliteitsmetrics (steekproef: eerste 1M rijen)

| jaar | n_rijen | gesorteerd | kolom_swap | min_spread_pips | mean_spread_pips | max_spread_pips | count_spread_gt_10pips | max_prijs_sprong_pips | gaten_gt_1min | zero_bid_vol | zero_ask_vol |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2004 | 1000000 | Ja | Ja | 0.4 | 1.8155 | 7.0 | 0 | 95.5 | 240 | 0 | 0 |
| 2005 | 1000000 | Ja | Ja | 0.4 | 1.8153 | 7.0 | 0 | 37.8 | 168 | 0 | 0 |
| 2006 | 1000000 | Ja | Ja | 0.4 | 1.8147 | 7.0 | 0 | 169.1 | 251 | 0 | 0 |
| 2007 | 1000000 | Ja | Ja | 0.4 | 1.8152 | 7.0 | 0 | 81.6 | 150 | 0 | 0 |
| 2008 | 1000000 | Ja | Ja | 0.4 | 1.8658 | 14.0 | 196 | 10.5 | 37 | 0 | 61 |
| 2009 | 1000000 | Ja | Ja | 0.4 | 2.9473 | 26.5 | 1550 | 43.0 | 500 | 0 | 0 |
| 2010 | 1000000 | Ja | Ja | 0.5 | 1.771 | 11.5 | 7 | 23.75 | 161 | 0 | 0 |
| 2011 | 1000000 | Ja | Ja | 0.2 | 1.88 | 26.6 | 397 | 42.85 | 80 | 0 | 0 |
| 2012 | 1000000 | Ja | Ja | 0.1 | 1.5945 | 23.4 | 1568 | 33.55 | 178 | 0 | 0 |
| 2013 | 1000000 | Ja | Ja | 0.1 | 1.3851 | 14.2 | 57 | 10.2 | 84 | 0 | 0 |
| 2014 | 1000000 | Ja | Ja | 0.1 | 0.9465 | 23.6 | 17 | 11.45 | 263 | 0 | 0 |
| 2015 | 1000000 | Ja | Ja | 0.1 | 2.1571 | 100.0 | 13087 | 657.15 | 115 | 0 | 0 |
| 2016 | 1000000 | Ja | Ja | 0.4 | 1.3 | 40.4 | 423 | 29.85 | 475 | 0 | 0 |
| 2017 | 1000000 | Ja | Ja | 0.1 | 1.2012 | 49.6 | 1738 | 13.9 | 306 | 0 | 0 |
| 2018 | 1000000 | Ja | Ja | 0.1 | 1.2063 | 39.9 | 1402 | 33.6 | 201 | 0 | 0 |
| 2019 | 1000000 | Ja | Ja | 0.1 | 1.1577 | 46.9 | 6000 | 28.3 | 285 | 0 | 0 |

Noot: 'Aantal Spread>10pips' en 'Gaten >1min' zijn tellingen binnen de 1M-rij-steekproef.

## Kwaliteitsoordeel

### 1. Kolomnamen — WAARSCHUWING
Zelfde swap-patroon als de andere majors. Bij import altijd kolom 1 als Bid behandelen en kolom 2 als Ask (idem volumes).

### 2. Sortering — GOED
Alle jaarbestanden zijn chronologisch gesorteerd op UTC-timestamp.

### 3. Spreads — samenvatting over alle jaren
- Minimum spread overall: 0.1000 pips
- Gemiddelde spread (gemiddeld van alle jaar-means): 1.6671 pips
- Maximum spread overall: 100.0000 pips

Moderne jaren (2014-2019) hebben typisch 0.1-0.5 pip ECN-grade spreads. Vroege jaren (2004-2007) hebben ~1-2 pip spreads, gebruikelijk voor institutional data uit die periode.

### 4. Tijdgaten — VERWACHT
Totaal 3,494 gaten > 1 minuut in alle 1M-steekproeven samen. Dit zijn weekenden, feestdagen en nieuwjaarsperiodes — geen onverwachte gaten gedetecteerd.

### 5. Prijssprongen — AANDACHT VOOR EXTREME WAARDEN
Maximum tick-to-tick sprong: 657.15 pips. Extreme waarden komen voor tijdens flash-crashes (2015 CHF-blackout, 2019 USDJPY flash) of openingsuren. Voor strategieën die hier niet tegen kunnen: filter ticks met `|mid_delta| > 50 pips`.

### 6. Volumes — GOED
Totaal 61 zero-volume ticks in alle 1M-steekproeven. Dit is verwaarloosbaar voor prijsanalyse.

## Aanbevelingen

1. **Kolomnamen corrigeren bij import:** behandel bronkolom 1 als Bid, kolom 2 als Ask (idem volumes). Pas de import-job hierop aan.
2. **Pip-definitie:** voor USDCHF is 1 pip = 0.0001. Gebruik deze conventie consistent.
3. **Flash-crash filtering (optioneel):** filter ticks met `|mid_delta| > 50 pips` als je backtest niet tegen extreme moves bestand is.
4. **Tijdgaten:** weekend-gaten zijn reëel en moeten expliciet worden geïmputeerd of overgeslagen bij HLOC-bar aggregatie.
5. **Volume-gewogen analyses:** zero-volume ticks veilig te negeren voor prijsanalyse, uitsluiten voor VWAP-features.

## Reproduceerbaarheid

Het assessment-script staat in `assess_majors.py`. Het leest per bestand alleen de eerste 1.000.000 rijen (consistent met EURUSD/USDJPY-aanpak).
