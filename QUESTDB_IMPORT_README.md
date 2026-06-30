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

---

## 📁 Project Bestanden

| Bestand | Doel |
|---------|------|
| `download_majors.py` | Downloadt ontbrekende 2020-2026 data van Dukascopy |
| `questdb_diagnose.py` | Toont de huidige databasevulling en ontbrekende jaren |
| `questdb_import.py` | Formatteert en importeert de data naar QuestDB |
| `QUESTDB_IMPORT_README.md` | Deze handleiding |
| `data_quality_assessment.md` | Kwaliteitsrapport van de historische data (2004-2019) |
