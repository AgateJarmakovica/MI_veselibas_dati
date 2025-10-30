"""
healthdq.rules
==============

Šis modulis definē datu kvalitātes noteikumus, validācijas loģiku un
transformācijas veselības datu prototipam *healthdq-ai*, kas ir daļa no
promocijas darba
“Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes uzlabošanai
atvērtās zinātnes iniciatīvās”.

Mērķis:
--------
Nodrošināt vienotu un reproducējamu datu validācijas un transformācijas mehānismu,
balstītu uz “Data-Centric AI” pieeju un FAIR datu principiem.

Komponentes:
-------------
- **run_checks()** – izpilda validācijas noteikumus (precizitāte, datumi, regex, diapazoni)
- **impute_simple()** – trūkstošo vērtību aizpildīšana pēc noteikumiem (`rules.yml`)
- **harmonize_semantics()** – semantiskā harmonizācija (piem., “female”, “woman” → “F”)
- **compute_bmi()** – atvasināto laukumu aprēķins (piem., BMI no auguma un svara)

Šie moduļi darbojas kopā, lai:
- Validētu datu precizitāti (PrecisionAgent),
- Uzlabotu datu pilnīgumu (CompletenessAgent),
- Harmonizētu semantiku un atkārtotu izmantojamību (ReusabilityAgent).

Visi noteikumi un stratēģijas tiek definētas YAML konfigurācijas failā `rules.yml`
un interpretētas šajā modulī, nodrošinot atvērtas zinātnes reproducējamību.

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

from .engine import run_checks
from .transform import harmonize_semantics, impute_simple, compute_bmi

__all__ = [
    "run_checks",
    "impute_simple",
    "harmonize_semantics",
    "compute_bmi"
]
