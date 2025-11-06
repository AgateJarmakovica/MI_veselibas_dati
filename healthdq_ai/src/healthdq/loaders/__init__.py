"""
healthdq.loaders
================

Šis modulis nodrošina datu ielādes (ingestion) komponentes prototipam *healthdq-ai*,
kas ir daļa no promocijas darba “Mākslīgā intelekta balstītas pieejas veselības datu
kvalitātes uzlabošanai atvērtās zinātnes iniciatīvās”.

Mērķis:
--------
Nodrošināt dažādu datu formātu drošu un standartizētu ielādi,
saskaņā ar **FAIR datu principiem** un **Data-Centric AI** paradigmu:
- **Findable** – atbalsta strukturētus, marķētus datu formātus (CSV, JSON, FHIR)
- **Accessible** – vienota API ielādei neatkarīgi no formāta
- **Interoperable** – FHIR balstīta datu struktūra pacientu ierakstiem
- **Reusable** – reproducējama datu ielādes loģika ar metadatiem

Komponentes:
-------------
- `load_csv()` – ielādē lokālos vai attālos CSV failus ar datu validāciju
- `load_json_records()` – apstrādā JSON formāta ierakstus (piem., API dati)
- `load_fhir_patient_bundle()` – parsē un ielādē FHIR `Patient` resursu komplektus

Šie ielādes moduli tiek izmantoti kā sākotnējais posms datu kvalitātes novērtēšanas
cauruļvadā (`pipeline.py`), pirms precizitātes, pilnīguma un atkārtotas izmantojamības
aģentu (Precision, Completeness, Reusability) izsaukšanas.

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

from .csv_loader import load_csv
from .json_loader import load_json_records
from .fhir_loader import load_fhir_patient_bundle

__all__ = [
    "load_csv",
    "load_json_records",
    "load_fhir_patient_bundle"
]
