"""
fhir_loader
===========

Šis modulis īsteno FHIR (Fast Healthcare Interoperability Resources) formāta datu
ielādi veselības datu kvalitātes prototipam *healthdq-ai*, kas ir daļa no
promocijas darba “Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes uzlabošanai
atvērtās zinātnes iniciatīvās”.

Mērķis:
--------
Nodrošināt drošu, strukturētu un reproducējamu FHIR datu (`Patient` resursu) ielādi
no JSON formāta failiem, pārveidojot tos uz pandas DataFrame formātu tālākai
kvalitātes analīzei (precizitāte, pilnīgums, atkārtota izmantojamība).

Funkcionalitāte:
----------------
- Nolasa FHIR `Bundle` objektu (`entry[]`)
- Ekstrahē `Patient` resursus (id, gender, birthDate)
- Nodrošina datu standartizāciju un metadatu reproducējamību
- Atbilst **FAIR principiem** (Findable, Accessible, Interoperable, Reusable)

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

import json
import os
import pandas as pd
import datetime


def load_fhir_patient_bundle(path: str) -> pd.DataFrame:
    """
    Ielādē FHIR `Patient` resursus no JSON formāta `Bundle` faila.

    Parametri:
    -----------
    path : str
        Ceļš uz FHIR JSON failu (piem., "data/fhir_bundle.json")

    Atgriež:
    --------
    df : pd.DataFrame
        Datu ietvars ar `patient_id`, `sex_at_birth` un `birth_date` kolonnām,
        papildināts ar reproducējamības metadatiem (`attrs["meta"]`).
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ FHIR fails nav atrasts: {path}")

    # Ielādē JSON datus
    try:
        with open(path, "r", encoding="utf-8") as f:
            bundle = json.load(f)
    except Exception as e:
        raise RuntimeError(f"❌ Neizdevās nolasīt FHIR JSON failu: {e}")

    # Apstrādā FHIR ierakstus
    rows = []
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") == "Patient":
            rows.append({
                "patient_id": resource.get("id"),
                "sex_at_birth": resource.get("gender"),
                "birth_date": resource.get("birthDate")
            })

    if not rows:
        raise ValueError("⚠️ FHIR bundle nesatur nevienu 'Patient' resursu.")

    df = pd.DataFrame(rows)

    # Pievieno reproducējamības metadatus (FAIR atbilstībai)
    meta = {
        "loader": "FHIR",
        "path": os.path.abspath(path),
        "timestamp": datetime.datetime.now().isoformat(),
        "row_count": len(df),
        "columns": list(df.columns),
        "fhir_version": bundle.get("meta", {}).get("versionId", "unknown"),
        "resourceType": "Patient",
        "fhir_profile": "https://hl7.org/fhir/patient.html",
    }

    df.attrs["meta"] = meta
    return df
