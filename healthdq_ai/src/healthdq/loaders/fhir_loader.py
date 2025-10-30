import json, pandas as pd
def load_fhir_patient_bundle(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as f:
        bundle = json.load(f)
    rows = []
    for e in bundle.get("entry", []):
        r = e.get("resource", {})
        if r.get("resourceType") == "Patient":
            rows.append({
                "patient_id": r.get("id"),
                "sex_at_birth": r.get("gender"),
                "birth_date": r.get("birthDate")
            })
    return pd.DataFrame(rows)
