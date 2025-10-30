"""
healthdq — Galvenais modulis veselības datu kvalitātes novērtēšanai
===================================================================

Šis modulis apvieno visas sistēmas sastāvdaļas (*pipeline*, *agents*, *rules*, *metrics*, *ui*)
vienotā datu kvalitātes novērtēšanas ietvarā.

Projekts: healthdq-ai  
Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30

Apraksts:
----------
healthdq-ai ir mākslīgā intelekta un noteikumu balstīts prototips, kas izstrādāts
promocijas darba ietvaros “Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes
uzlabošanai atvērtās zinātnes iniciatīvās”.

Tas fokusējas uz trīs datu kvalitātes dimensijām:
  - **Precizitāti (Precision)** — loģiskā un formālā pareizība
  - **Pilnīgumu (Completeness)** — trūkstošo vērtību identificēšana un aizpildīšana
  - **Atkārtotu izmantojamību (Reusability)** — semantiskā saskaņa un vienādošana

Funkcionalitāte:
----------------
Šī pakotne nodrošina:
  - Datu ielādi no dažādiem avotiem (CSV, JSON, FHIR)
  - Kvalitātes pārbaudi un noteikumu dzinēju (`engine.py`)
  - AI-atbalstītu imputāciju un semantisko harmonizāciju (`transform.py`)
  - Kvalitātes metriku aprēķinu (`metrics`)
  - Interaktīvu lietotāja interfeisu (`ui`)
  - Vienotu cauruļvadu (`pipeline.py`)

Atbilst **FAIR datu principiem** — reproducējamība, caurspīdīgums un atkārtota izmantojamība.
"""

from .pipeline import run_pipeline

__all__ = ["run_pipeline"]

# ---------------------------------------------------------------------
# METADATA (reproducibility + FAIR documentation)
# ---------------------------------------------------------------------
__meta__ = {
    "project": "healthdq-ai",
    "author": "Agate Jarmakoviča",
    "version": "1.2",
    "created": "2025-10-30",
    "description": (
        "AI-supported, rule-based system for improving healthcare data quality "
        "with focus on precision, completeness, and reusability."
    ),
    "license": "CC-BY-NC 4.0",
    "contact": "agate.jarmakovica@university.lv"
}


def about() -> str:
    """
    Izdrukā projekta metadatus un versijas informāciju.
    Noderīgi reproducējamības dokumentācijā un demonstrācijās.
    """
    import json
    return json.dumps(__meta__, indent=2)
