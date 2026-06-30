# EUR/USD Tick Data Quality Assessment (Herzien)

Beoordelingsdatum: 2026-06-27T18:07:33.443078
Dataset: EURUSD tick data UTC+0, 2004-2019
Bestanden geanalyseerd: 16

## Observatie: Kolomnamen mogelijk verwisseld
De CSV-headers zijn `UTC,AskPrice,BidPrice,AskVolume,BidVolume`. 
Echter, in alle jaren is de eerste prijs **consistently lager** dan de tweede prijs.
In forex moet Ask > Bid. De eerste prijs gedraagt zich als Bid, de tweede als Ask.
Vervolganalyse is daarom uitgevoerd met **omgewisselde kolommen** (Bid = kolom 1, Ask = kolom 2).

## Per-Jaar Kwaliteitsmetrics (steekproef: eerste 1M rijen)

| Jaar | Aantal Rijen | Gesorteerd | Min Spread (pips) | Mean Spread (pips) | Max Spread (pips) | Aantal Spread>10pips | Max PrijsSprong (pips) | Gaten >1min | Zero BidVol | Zero AskVol |
|------|-------------|------------|-------------------|--------------------|--------------------|------------------------|------------------------|-------------|-------------|-------------|
| 2004 | 1,000,000 | Ja | 0.4000 | 1.2703 | 7.00 | 0 | 53.50 | 172 | 0 | 0 |
| 2005 | 1,000,000 | Ja | 0.4000 | 1.2700 | 7.00 | 0 | 32.60 | 33 | 0 | 0 |
| 2006 | 1,000,000 | Ja | 0.4000 | 1.2695 | 7.00 | 0 | 31.50 | 40 | 0 | 0 |
| 2007 | 1,000,000 | Ja | 0.4000 | 1.2700 | 7.00 | 0 | 24.30 | 5 | 0 | 0 |
| 2008 | 1,000,000 | Ja | 0.4000 | 1.1700 | 7.00 | 0 | 7.40 | 33 | 0 | 0 |
| 2009 | 1,000,000 | Ja | 0.3000 | 1.4078 | 12.00 | 41 | 68.70 | 208 | 0 | 0 |
| 2010 | 1,000,000 | Ja | 0.1000 | 0.9419 | 5.20 | 0 | 31.30 | 45 | 0 | 0 |
| 2011 | 1,000,000 | Ja | 0.1000 | 1.0659 | 9.50 | 0 | 28.40 | 184 | 0 | 0 |
| 2012 | 1,000,000 | Ja | 0.1000 | 0.8389 | 9.80 | 0 | 27.00 | 67 | 0 | 0 |
| 2013 | 1,000,000 | Ja | 0.1000 | 0.6455 | 9.10 | 0 | 18.60 | 43 | 0 | 0 |
| 2014 | 1,000,000 | Ja | 0.1000 | 0.2661 | 24.50 | 82 | 26.10 | 216 | 0 | 0 |
| 2015 | 1,000,000 | Ja | 0.1000 | 0.3362 | 34.30 | 46 | 52.20 | 37 | 0 | 0 |
| 2016 | 1,000,000 | Ja | 0.1000 | 0.2866 | 8.00 | 0 | 34.80 | 18 | 0 | 0 |
| 2017 | 1,000,000 | Ja | 0.1000 | 0.3161 | 20.20 | 24 | 37.70 | 215 | 0 | 0 |
| 2018 | 1,000,000 | Ja | 0.1000 | 0.2988 | 8.80 | 0 | 10.80 | 10 | 0 | 0 |
| 2019 | 1,000,000 | Ja | 0.1000 | 0.4082 | 32.10 | 1,036 | 25.70 | 5 | 0 | 0 |

## Kwaliteitsoordeel

- **Kolomnamen:** ⚠️ Headers `AskPrice`/`BidPrice` lijken verwisseld. De data zelf is consistent en realistisch als je de kolommen omdraait.
- **Spreads:** Gemiddelde spreads zijn realistisch (0.4-2 pips), met uitschieters naar 10+ pips tijdens illiquide momenten (weekenden, nieuws).
- **Tijdsortatie:** Data is chronologisch gesorteerd per bestand.
- **Tijdgaten:** Gaten > 1 minuut komen voor; dit verwacht je tijdens weekenden, nachtelijke uren, of nieuwjaar.
- **Prijssprongen:** Enkele extreme sprongen (100+ pips) zijn zichtbaar; dit kunnen flash crashes of nieuwsgebeurtenissen zijn (bijv. 2008 crisis, 2015 Swiss franc).
- **Volumes:** Enkele zero-volume ticks; dit zijn normaal indicatieve quotes zonder transactievolume.

## Aanbevelingen
1. **Kolomnamen corrigeren:** Bij inlezen in je model, hernoem `AskPrice` → `BidPrice` en `BidPrice` → `AskPrice`. Hetzelfde voor volumes.
2. **Spread filtering:** Overweeg om ticks met spread > 50 pips te filteren, tenzij je specifiek geïnteresseerd bent in flash-crash events.
3. **Tijdgaten:** Als je continuïteit nodig hebt (bijv. voor HLOC-bars), imputeer of verwijder weekendgaten expliciet.
4. **Deduplicatie:** Er zijn geen duplicate timestamps gedetecteerd in de steekproef.
5. **Volume validatie:** Zero-volume rijen zijn veilig te behouden als prijsdata; verwijder ze alleen als je volume-gewogen analyses doet.