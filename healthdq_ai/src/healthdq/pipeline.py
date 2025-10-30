import yaml, pandas as pd
from .loaders import load_csv, load_json_records, load_fhir_patient_bundle
from .agents import PrecisionAgent, CompletenessAgent, ReusabilityAgent
from .metrics import compute_metrics
from .rules import run_checks

LOADERS = {"csv": load_csv, "json": load_json_records, "fhir": load_fhir_patient_bundle}

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f: return yaml.safe_load(f)

def run_pipeline(input_path: str, kind: str, config_path: str, out_dir: str):
    cfg = load_config(config_path)
    df_raw = LOADERS[kind](input_path)

    # BEFORE metrics baseline
    metrics_before_df = df_raw.copy()

    # Reusability -> Completeness -> Precision (user diagram flow)
    df_r = ReusabilityAgent(cfg).run(df_raw)
    df_c = CompletenessAgent(cfg).run(df_r)
    issues = PrecisionAgent(cfg).run(df_c)

    # AFTER metrics
    metrics = compute_metrics(metrics_before_df, df_c, cfg)

    # Save outputs
    import os, json
    os.makedirs(out_dir, exist_ok=True)
    df_c.to_csv(f"{out_dir}/cleaned.csv", index=False)
    issues.to_csv(f"{out_dir}/issues.csv", index=False)
    with open(f"{out_dir}/metrics_before_after.json","w",encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return df_c, issues, metrics
