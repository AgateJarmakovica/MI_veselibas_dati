"""
fhir_loader.py — FHIR (HL7) veselības datu ielādes modulis

Šis modulis nodrošina FHIR (Fast Healthcare Interoperability Resources)
standarta datu ielādi no JSON vai NDJSON formāta failiem un to konvertēšanu
struktūrētā DataFrame formā, kas izmantojama MI datu kvalitātes novērtēšanai.

Funkcionālais mērķis:
1. Ielādēt un pārveidot FHIR Bundle (Patient, Observation, Encounter, u.c.) uz tabulveida formātu.
2. Nodrošināt automātisku shēmas atpazīšanu (Schema Discovery).
3. Nodrošināt atbilstību FAIR un Data-Centric AI principiem.

Akadēmiskais pamats:
- HL7 FHIR R4 (https://hl7.org/FHIR/)
- Wilkinson, M. et al. (2016). “The FAIR Guiding Principles for scientific data management.”
- Jansen, A. et al. (2021). “Using FHIR to improve interoperability in healthcare AI.”
"""

import json
import pandas as pd
import os
from typing import Dict, Any, List


def extract_patient_data(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Ekstrahē būtiskos laukus no FHIR 'Patient' resursa."""
    resource = entry.get("resource", {})
    if resource.get("resourceType") != "Patient":
        return {}

    patient = {
        "patient_id": resource.get("id"),
        "family_name": None,
        "given_name": None,
        "birth_date": resource.get("birthDate"),
        "sex_at_birth": resource.get("gender"),
    }

    name_data = resource.get("name", [])
    if name_data:
        patient["family_name"] = name_data[0].get("family")
        given = name_data[0].get("given", [])
        patient["given_name"] = given[0] if given else None

    return patient


def load_fhir_patient_bundle(file_path: str) -> pd.DataFrame:
    """
    Ielādē FHIR Patient Bundle (JSON) un konvertē to DataFrame formātā.

    Parametri:
    -----------
    file_path : str
        Ceļš uz FHIR Bundle failu (.json vai .ndjson)

    Atgriež:
    --------
    pd.DataFrame — ielādētie pacientu dati
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Failu '{file_path}' nevar atrast.")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data.get("entry", [])
    if not entries:
        raise ValueError("FHIR Bundle nesatur 'entry' laukus.")

    patients = [extract_patient_data(e) for e in entries if e.get("resource", {}).get("resourceType") == "Patient"]
    df = pd.DataFrame([p for p in patients if p])

    if df.empty:
        raise ValueError("Nav atrasti derīgi 'Patient' ieraksti FHIR Bundle datnē.")

    print(f"Ielādēti {len(df)} FHIR pacientu ieraksti no {file_path}")

    return df
