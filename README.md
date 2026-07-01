# Dukascopy Forex Tick Data Importer & Quality Assessor

Dit project bevat een verzameling Python- en batch-scripts voor het downloaden, decompresseren, analyseren (kwaliteitscontrole) en importeren van historische Forex tick-data (2004 t/m 2026) van Dukascopy naar een **QuestDB** database.

## 📋 Project Overzicht

De tools zijn ontworpen om grote hoeveelheden tick-data (tot honderden miljoenen ticks per bestand) efficiënt te verwerken met een minimale geheugenvoetafdruk.

### Ondersteunde Valutaparen
* AUDUSD
* EURUSD
* GBPUSD
* NZDUSD
* USDCAD
* USDCHF
* USDJPY

---

## 📁 Bestandsstructuur

| Bestand / Map | Doel |
| :--- | :--- |
| [download_majors.py](file:///c:/projecten/forexdata/download_majors.py) | Downloadt ontbrekende tick-data (2020-2026) van Dukascopy. |
| [decompress_majors.py](file:///c:/projecten/forexdata/decompress_majors.py) | Decomprimeert de ruwe Dukascopy `.bin` bestanden naar `.csv`. |
| [assess_majors.py](file:///c:/projecten/forexdata/assess_majors.py) | Voert een algehele kwaliteitscontrole uit op de CSV-bestanden van alle paren. |
| [assess_usdjpy.py](file:///c:/projecten/forexdata/assess_usdjpy.py) | Specifiek kwaliteitscontrole-script voor USDJPY. |
| [questdb_diagnose.py](file:///c:/projecten/forexdata/questdb_diagnose.py) | Controleert de status en data-aantallen in de QuestDB database. |
| [questdb_import.py](file:///c:/projecten/forexdata/questdb_import.py) | Formatteert de CSV-bestanden en importeert ze in QuestDB. |
| [questdb_import_local.py](file:///c:/projecten/forexdata/questdb_import_local.py) | Geoptimaliseerd import-script voor uitvoering direct op de server (9x snellere datum-conversie). |
| [download_local.py](file:///c:/projecten/forexdata/download_local.py) | Downloadt ticks of 1m bars voor willekeurige symbolen direct op de server. |
| [compress_existing_data.py](file:///c:/projecten/forexdata/compress_existing_data.py) | Comprimeert bestaande CSV-bestanden naar .csv.gz om ~80% schijfruimte te besparen. |
| [START_IMPORT.bat](file:///c:/projecten/forexdata/START_IMPORT.bat) | Batch-bestand om de import op te starten. |
| [QUESTDB_IMPORT_README.md](file:///c:/projecten/forexdata/QUESTDB_IMPORT_README.md) | Gedetailleerde handleiding voor het opzetten en importeren naar QuestDB. |

---

## 🔍 Kwaliteitsrapporten (Quality Assessments)

Tijdens de kwaliteitscontrole is ontdekt dat de bronbestanden van Dukascopy de kolomnamen consistent verwisseld hebben (`AskPrice` bevat in werkelijkheid de Bid-prijs en vice versa). De import- en assessment-scripts corrigeren dit automatisch.

Gedetailleerde kwaliteitsrapportages per valutapaar zijn hier te vinden:
* [USDJPY Kwaliteitsrapport](file:///c:/projecten/forexdata/data_quality_assessment_USDJPY.md)
* [EURUSD Kwaliteitsrapport](file:///c:/projecten/forexdata/data_quality_assessment_EURUSD.md)
* [GBPUSD Kwaliteitsrapport](file:///c:/projecten/forexdata/data_quality_assessment_GBPUSD.md)
* [AUDUSD Kwaliteitsrapport](file:///c:/projecten/forexdata/data_quality_assessment_AUDUSD.md)
* [NZDUSD Kwaliteitsrapport](file:///c:/projecten/forexdata/data_quality_assessment_NZDUSD.md)
* [USDCAD Kwaliteitsrapport](file:///c:/projecten/forexdata/data_quality_assessment_USDCAD.md)
* [USDCHF Kwaliteitsrapport](file:///c:/projecten/forexdata/data_quality_assessment_USDCHF.md)

---

## 🖥️ Server Scripts (Linux / Local Execution)

Voor uitvoering direct op de Linux server (bijvoorbeeld met data gemonteerd op `/mnt/ssd/forexdata`) zijn er twee specifieke scripts beschikbaar:

### 1. download_local.py
Dit script downloadt data van Dukascopy voor elk gewenst symbool (majors, minors, goud/zilver, indexen of commodities) en ondersteunt directe conversie naar 1-minuut bars.

* **Ticks downloaden (standaard laatste 2 jaar)**:
  ```bash
  python download_local.py --symbols USDCAD,XAUUSD --freq tick
  ```
* **1-minuut bars downloaden (standaard laatste 5 jaar)**:
  *Het script downloadt per maand tick-data, resamplet dit in-memory naar 1m bars en verwijdert de grote tick-bestanden automatisch om schijfruimte te besparen.*
  ```bash
  python download_local.py --symbols GBPUSD,EURUSD,BRENTUSD --freq 1m
  ```
* **Specifieke jaren / periodes opgeven**:
  ```bash
  python download_local.py --symbols EURUSD --freq 1m --start-year 2020 --end-year 2025
  ```

### 2. questdb_import_local.py
Dit script importeert de geformatteerde CSV-bestanden direct in QuestDB vanaf de lokale server disk (`127.0.0.1:9000`). Het bevat een geoptimaliseerde methode voor datum-conversie waardoor het importeren **9x sneller** gaat dan voorheen.

* **Importeren van ontbrekende jaren voor een paar**:
  ```bash
  python questdb_import_local.py GBPUSD
  ```
* **Importeren van alle jaren (overschrijf database check)**:
  ```bash
  python questdb_import_local.py GBPUSD --all
  ```

---

## 📦 Schijfruimte & Gzip-compressie (.csv.gz)

Omdat de ruwe tick-bestanden erg groot zijn (tot meer dan 2 GB per jaar), ondersteunen alle scripts nu **natively `.csv.gz` compressie**. Pandas decomprimeert deze bestanden in-memory tijdens het inlezen, waardoor ze ca. **5x kleiner** zijn op schijf zonder verlies van prestaties.

* **Bestaande data comprimeren**:
  Als je al onbewerkte CSV-bestanden hebt gedownload, kun je ze comprimeren met:
  ```bash
  python compress_existing_data.py
  ```
  *Dit script converteert alle `.csv` bestanden naar `.csv.gz` en verwijdert de originele bestanden na succesvolle verificatie.*

* **Nieuwe downloads**:
  Zowel `download_majors.py` als `download_local.py` slaan de data vanaf nu direct op als `.csv.gz`.
  
* **Import & Kwaliteitscontrole**:
  De scripts `questdb_import.py`, `questdb_import_local.py` en `assess_majors.py` herkennen automatisch zowel `.csv` als `.csv.gz` bestanden en verwerken ze transparant.

---

## 🚀 Snel Aan de Slag

Voor gedetailleerde instructies over het opzetten van QuestDB en het uitvoeren van de import-pipeline op Windows, raadpleeg de **[QuestDB Forex Tick Data Project Handleiding](file:///c:/projecten/forexdata/QUESTDB_IMPORT_README.md)**.

