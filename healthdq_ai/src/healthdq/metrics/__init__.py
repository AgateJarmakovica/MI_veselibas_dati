"""
healthdq.metrics
================

Šis modulis nodrošina veselības datu kvalitātes rādītāju (metrics) aprēķinus
prototipam *healthdq-ai*, kas ir daļa no promocijas darba
“Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes uzlabošanai
atvērtās zinātnes iniciatīvās”.

Mērķis:
--------
Definēt un aprēķināt datu kvalitātes metriku trīs galvenajās dimensijās:
  - **Precizitāte (Precision)** – loģiskā un formālā korektuma novērtējums;
  - **Pilnīgums (Completeness)** – trūkstošo vērtību apjoms un aizpildījuma līmenis;
  - **Atkārtota izmantojamība (Reusability)** – semantiskās harmonizācijas un
    vienotības pakāpe pēc AI balstītas transformācijas.

Visi mērījumi tiek saglabāti FAIR reproducējamā formā ar metadatiem:
  - `metric_name`, `value`, `timestamp`, `columns`, `source_stage` u.c.

Šis modulis tiek izmantots pipeline beigās, lai salīdzinātu datu kvalitāti
pirms un pēc apstrādes (“Before vs After”) un demonstrētu AI pieejas ietekmi.

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

from .completeness_metrics import compute_completeness_metrics
from .precision_metrics import compute_precision_metrics
from .reusability_metrics import compute_reusability_metrics

__all__ = [
    "compute_completeness_metrics",
    "compute_precision_metrics",
    "compute_reusability_metrics"
]
