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

## 🚀 Snel Aan de Slag

Voor gedetailleerde instructies over het opzetten van QuestDB en het uitvoeren van de import-pipeline, raadpleeg de **[QuestDB Forex Tick Data Project Handleiding](file:///c:/projecten/forexdata/QUESTDB_IMPORT_README.md)**.
