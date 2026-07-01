# QuestDB Forex Tick Data Project Handleiding

Dit project bevat tools voor het downloaden, formatteren en importeren van historische Forex tick-data (2004 t/m 2026) voor de 7 major valutaparen naar een QuestDB database op de HP server (`192.168.10.33`).

## 📋 Ondersteunde Valutaparen
* **AUDUSD**
* **EURUSD**
* **GBPUSD**
* **NZDUSD**
* **USDCAD**
* **USDCHF** (Let op: bevat SNB Black Swan in 2015 en out-of-order data in 2010 die gesorteerd moet worden)
* **USDJPY**

---

## 🔧 QuestDB Tabel Schema (`ticks`)
Alle data wordt opgeslagen in een centrale, gepartitioneerde tabel (`ticks`):
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
*Opmerking: De kolommen in de ruwe CSV-bestanden van Dukascopy zijn verwisseld (`AskPrice` = Bid en `BidPrice` = Ask). De import-tool corrigeert dit automatisch en berekent de spread en het totale volume.*

---

## 🚀 Handleiding in 3 Stappen

### Stap 1: Valutadata downloaden (optioneel)
De download-tool haalt data op via Dukascopy voor de jaren **2020 t/m 2026** (oudere jaren zijn al lokaal aanwezig). De downloads zijn volledig hervatbaar (reeds gedownloade maanden worden overgeslagen).

* **Specifiek paar downloaden (bijv. GBPUSD):**
  ```bash
  python download_majors.py GBPUSD
  ```
* **Alle paren achter elkaar downloaden:**
  ```bash
  python download_majors.py
  ```

### Stap 2: Database status controleren
Met de diagnose-tool kun je controleren welke paren en jaren al in QuestDB staan en hoeveel rijen er zijn opgeslagen:
```bash
python questdb_diagnose.py
```

### Stap 3: Data importeren in QuestDB
De import-tool leest de CSV-bestanden chunk-by-chunk in (geheugenefficiënt), formatteert ze en uploadt ze via één enkele HTTP `/imp` POST-verbinding per jaar. Het script slaat jaren die al in de database staan standaard over.

* **Importeer ontbrekende jaren voor een specifiek paar (bijv. EURUSD):**
  ```bash
  python questdb_import.py EURUSD
  ```
* **Importeer ALLE jaren voor een paar (overschrijft nooit bestaande data):**
  ```bash
  python questdb_import.py EURUSD --all
  ```
* **Importeer specifieke jaren voor een paar:**
  ```bash
  python questdb_import.py EURUSD 2015 2016
  ```

---

## 🛡️ Tips & Problemen oplossen

### 1. Waarom importeren we per paar/jaar?
Elk jaar bevat tussen de 100 miljoen en 300 miljoen rijen. Door dit per jaar te doen, houden we de tijdelijke bestanden handzaam en kunnen we bij eventuele netwerkonderbrekingen eenvoudig de import hervatten vanaf het mislukte jaar.

### 2. "Kan QuestDB niet bereiken"
* Controleer of de QuestDB web-console bereikbaar is op: `http://192.168.10.33:9000`
* Controleer of je netwerkverbinding stabiel is (bij voorkeur bekabeld gigabit i.v.m. de uploadgrootte van ~800MB per jaar).

### 3. "UnicodeEncodeError" op Windows
De scripts zijn geoptimaliseerd om zonder emojis te printen, waardoor ze probleemloos werken op standaard Windows CMD en PowerShell zonder dat je `PYTHONIOENCODING` hoeft aan te passen.

### 4. Let op bij `--all`: geen dubbele-import-check
`--all` importeert altijd *alle* lokaal beschikbare jaren, ongeacht wat al in de database staat (in tegenstelling tot de default modus, die ontbrekende jaren berekent). QuestDB heeft geen `DELETE`-ondersteuning (ook niet in nieuwere versies — dit is een bewuste architecturale keuze, geen ontbrekende feature) en `overwrite=false` voorkomt geen dubbele rijen, dus een jaar dat al (deels) geïmporteerd is opnieuw met `--all` draaien resulteert in duplicaten. Controleer met `questdb_diagnose.py` of losse `SELECT count() FROM ticks WHERE symbol='<PAIR>' AND ts IN '<jaar>'`-queries welke jaren al aanwezig zijn vóórdat je `--all` gebruikt.

---

## ⚠️ Bekende dataproblemen

### USDCAD 2005: gedupliceerde rijen
Door een test-import gevolgd door een `--all`-run zonder voorafgaande check staan de rijen voor **USDCAD, jaar 2005** dubbel in de `ticks`-tabel (elke tick exact 2x). Geverifieerd effect op 1-minuut OHLC-candles:
* **Open/high/low/close: niet aangetast** (duplicaat heeft identieke prijzen, dus min/max/eerste/laatste waarde blijft gelijk).
* **Volume en tick-count per candle: exact 2x te hoog** voor USDCAD 2005.

Niet opgelost omdat QuestDB geen `DELETE` ondersteunt en de enige generieke workaround (hele tabel exporteren, dedupliceren, opnieuw aanmaken) een te groot risico/impact heeft t.o.v. dit geïsoleerde probleem (~0,15% van de tabel). Houd hier rekening mee bij volume- of tick-count-gebaseerde analyses (bv. VWAP, liquiditeitsanalyse) op USDCAD 2005.

### Live-feed overlap voor het lopende jaar
De `ticks`-tabel wordt náást deze batch-import ook door een aparte, waarschijnlijk realtime data-feed gevuld (herkenbaar aan symbolen als `XAUUSD` en `EURGBP`, die niet in dit project voorkomen). Voor het lopende kalenderjaar (bv. 2026) bevat de tabel dus zowel de historische Dukascopy-ticks uit deze pipeline als losse, niet-gerelateerde live ticks voor dezelfde periode — reken bij analyses over het huidige jaar niet blind op de rijcount uit deze import-scripts.

### AUDUSD 2026: ~3 miljoen extra gedupliceerde rijen
`questdb_import_ilp_local.py` had een fail-open bug in `get_existing_years()`: als de per-jaar `SELECT count()`-check op timeout liep (kwam voor bij 2026, doordat die partitie door de live-feed-overlap hierboven al 70+ miljoen rijen bevat en dus trager is), werd dat jaar stilzwijgend als "nog niet geïmporteerd" behandeld. Bij een `AUDUSD`-run zonder `--all` (dus juist de veilige default-modus) leidde dit alsnog tot een gedeeltelijke herimport van 2026 voordat het op tijd werd afgebroken — ongeveer 3 miljoen extra AUDUSD-rijen voor 2026, bovenop de al bestaande live-feed-overlap. Gefixt door de timeout te verhogen (15s → 30s) en de foutafhandeling om te draaien: een query die niet binnen de timeout antwoordt, laat het jaar nu **overslaan** (fail-safe) in plaats van importeren (fail-open) — een gemiste import is met een expliciete jaaropgave te herstellen, een dubbele import niet (geen `DELETE`).

---

## 📁 Project Bestanden

| Bestand | Doel |
|---------|------|
| `download_majors.py` | Downloadt ontbrekende 2020-2026 data van Dukascopy |
| `questdb_diagnose.py` | Toont de huidige databasevulling en ontbrekende jaren |
| `questdb_import.py` | Formatteert en importeert de data naar QuestDB (remote server) |
| `questdb_import_local.py` | Zelfde als hierboven, maar voor lokaal draaien op de QuestDB-server (`127.0.0.1`, `/mnt/ssd/forexdata`) |
| `questdb_import_ilp_local.py` | Lokale variant die QuestDB's ILP-protocol gebruikt i.p.v. `/imp` HTTP CSV-upload — ~60% sneller lokaal (geen tijdelijk CSV-bestand, geen dubbele schijf-I/O). Alleen zinvol op dezelfde machine als QuestDB. |
| `QUESTDB_IMPORT_README.md` | Deze handleiding |
| `data_quality_assessment.md` | Kwaliteitsrapport van de historische data (2004-2019) |
