"""
pipeline.py — AI datu kvalitātes cauruļvads (pipeline)
=======================================================

Šis modulis īsteno galveno izpildes ciklu (pipeline) veselības datu kvalitātes
novērtēšanai un uzlabošanai prototipā *healthdq-ai*.

Mērķis:
--------
Izstrādāt reproducējamu un AI-atbalstītu datu kvalitātes novērtēšanas procesu,
kas fokusējas uz trim galvenajām dimensijām:
  - **Precizitāte (Precision)** — loģiskā un semantiskā korektība
  - **Pilnīgums (Completeness)** — trūkstošo vērtību noteikšana un imputācija
  - **Atkārtota izmantojamība (Reusability)** — semantiskā harmonizācija un vienību saskaņošana

Plūsmas secība:
----------------
1. **Datu ielāde** → CSV / JSON / FHIR  
2. **ReusabilityAgent** → semantiskā harmonizācija  
3. **CompletenessAgent** → imputācija (trūkstošo vērtību aizpildīšana)  
4. **PrecisionAgent** → noteikumu pārbaude (rules.yml)  
5. **Metriku aprēķins pirms/pēc**  
6. **Rezultātu saglabāšana** → tīrītie dati, problēmas, metrikas, metadati

Atbilst **FAIR principiem** (Findable, Accessible, Interoperable, Reusable)
un **Data-Centric AI** paradigmai.

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

import os
import json
import yaml
import pandas as pd
from datetime import datetime

# Importē komponentes
from .loaders import load_csv, load_json_records, load_fhir_patient_bundle
from .agents import PrecisionAgent, CompletenessAgent, ReusabilityAgent
from .metrics import compute_metrics
from .rules import run_checks


# ---------------------------------------------------------------------
# Pieejamie datu ielādes adapteri
# ---------------------------------------------------------------------
LOADERS = {
    "csv": load_csv,
    "json": load_json_records,
    "fhir": load_fhir_patient_bundle,
}


# ---------------------------------------------------------------------
# Konfigurācijas ielāde
# ---------------------------------------------------------------------
def load_config(path: str) -> dict:
    """Droši ielādē YAML konfigurācijas failu (rules.yml)."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------
# Galvenā pipeline funkcija
# ---------------------------------------------------------------------
def run_pipeline(input_path: str, kind: str, config_path: str, out_dir: str):
    """
    Izpilda pilnu datu kvalitātes ciklu (pipeline).

    Parametri:
    -----------
    input_path : str
        Ceļš uz ievades datu failu (CSV, JSON, FHIR)
    kind : str
        Datu formāts (“csv”, “json” vai “fhir”)
    config_path : str
        Ceļš uz noteikumu konfigurācijas failu (rules.yml)
    out_dir : str
        Izvades mape, kur saglabāt rezultātus

    Atgriež:
    --------
    (df_cleaned, issues_df, metrics_dict)
        - df_cleaned: tīrītie dati pēc visām transformācijām
        - issues_df: datu kvalitātes pārkāpumu saraksts
        - metrics_dict: pirms/pēc metrikas salīdzinājums
    """

    start_time = datetime.now()

    # ------------------------------------------------------------
    # 1️⃣ Konfigurācijas ielāde un datu avota izvēle
    # ------------------------------------------------------------
    cfg = load_config(config_path)
    loader = LOADERS.get(kind)
    if not loader:
        raise ValueError(f"❌ Neatbalstīts formāts: {kind}")

    df_raw = loader(input_path)
    if df_raw.empty:
        raise ValueError("❌ Datu kopa ir tukša vai netika pareizi ielādēta.")

    # ------------------------------------------------------------
    # 2️⃣ Sākotnējās metriku bāzes (pirms AI apstrādes)
    # ------------------------------------------------------------
    metrics_before_df = df_raw.copy()

    # ------------------------------------------------------------
    # 3️⃣ AI-atbalstītā datu kvalitātes apstrādes plūsma
    # ------------------------------------------------------------
    df_r = ReusabilityAgent(cfg).run(df_raw)
    df_c = CompletenessAgent(cfg).run(df_r)
    issues = PrecisionAgent(cfg).run(df_c)

    # ------------------------------------------------------------
    # 4️⃣ Metriku aprēķins pēc apstrādes
    # ------------------------------------------------------------
    metrics = compute_metrics(metrics_before_df, df_c, cfg)

    # ------------------------------------------------------------
    # 5️⃣ Rezultātu saglabāšana
    # ------------------------------------------------------------
    os.makedirs(out_dir, exist_ok=True)
    df_c.to_csv(f"{out_dir}/cleaned.csv", index=False)
    issues.to_csv(f"{out_dir}/issues.csv", index=False)
    with open(f"{out_dir}/metrics_before_after.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------
    # 6️⃣ FAIR reproducējamības metadati
    # ------------------------------------------------------------
    meta = {
        "timestamp": datetime.now().isoformat(),
        "input_path": input_path,
        "config_used": config_path,
        "records_processed": len(df_c),
        "issues_detected": len(issues),
        "metrics_available": list(metrics.keys()),
        "run_duration_sec": (datetime.now() - start_time).total_seconds(),
    }
    with open(f"{out_dir}/meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------
    # 7️⃣ Izvades kopsavilkums
    # ------------------------------------------------------------
    print(" healthdq-ai pipeline pabeigts!")
    print(f"   • Ierakstu skaits: {len(df_c)}")
    print(f"   • Atrasti pārkāpumi: {len(issues)}")
    print(f"   • Rezultāti saglabāti: {out_dir}/")

    return df_c, issues, metrics
