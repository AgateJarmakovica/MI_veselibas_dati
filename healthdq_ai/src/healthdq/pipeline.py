"""
pipeline.py — MI datu kvalitātes cauruļvads (pipeline)
=======================================================

Šis modulis īsteno galveno izpildes ciklu (pipeline) veselības datu kvalitātes
novērtēšanai un uzlabošanai prototipā *healthdq-ai*.

Tagad iekļauj arī MI komponenti — SchemaLearner,
kas spēj mācīties no datu struktūrām un automātiski noteikt kolonnu semantiku.

Mērķis:
--------
Izstrādāt reproducējamu un MI-atbalstītu datu kvalitātes novērtēšanas procesu,
kas fokusējas uz trim galvenajām dimensijām:
  - Precizitāte (Precision) — loģiskā un semantiskā korektība
  - Pilnīgums (Completeness) — trūkstošo vērtību noteikšana un imputācija
  - Atkārtota izmantojamība (Reusability) — semantiskā harmonizācija un vienību saskaņošana

Papildināts ar:
---------------
  - SchemaLearner: MI modelis, kas analizē kolonnu nozīmi un strukturālo lomu
  - MI ieteikumu ģenerēšana un saglabāšana
  - HITL (cilvēka atgriezeniskās saites) iespēja noteikumu precizēšanai

Atbilst FAIR un Data-Centric AI principiem.

Autore: Agate Jarmakoviča
Versija: 1.3
Datums: 2025-10-30
"""

import os
import json
import importlib.util
from types import ModuleType
from datetime import datetime

from .loaders import load_csv, load_json_records, load_fhir_patient_bundle
from .agents import PrecisionAgent, CompletenessAgent, ReusabilityAgent
from .metrics import compute_metrics
from .rules import run_checks
from .schema_learner import SchemaLearner


_YAML_MODULE: ModuleType | None = None


def _get_yaml_module() -> ModuleType:
    """Atrod un ielādē PyYAML ar skaidru kļūdas ziņojumu, ja tas nav pieejams."""
    global _YAML_MODULE
    if _YAML_MODULE is not None:
        return _YAML_MODULE

    spec = importlib.util.find_spec("yaml")
    if spec is None:
        raise ModuleNotFoundError(
            "PyYAML nav instalēts. Lūdzu pievienojiet `pyyaml` atkarībām vai "
            "instalējiet to ar `pip install pyyaml`, lai ielādētu rules.yml konfigurācijas."
        )

    module = importlib.util.module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        raise ImportError("Neizdevās inicializēt PyYAML moduļa ielādi.")
    loader.exec_module(module)  # type: ignore[attr-defined]
    _YAML_MODULE = module
    return module


LOADERS = {
    "csv": load_csv,
    "json": load_json_records,
    "fhir": load_fhir_patient_bundle,
}


def load_config(path: str) -> dict:
    """Ielādē YAML konfigurācijas failu (rules.yml)."""
    yaml = _get_yaml_module()
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_pipeline(input_path: str, kind: str, config_path: str, out_dir: str):
    """
    Izpilda pilnu datu kvalitātes novērtēšanas ciklu (pipeline).

    Parametri:
        input_path : str  — ievades datu fails (CSV, JSON, FHIR)
        kind : str        — datu formāts ("csv", "json" vai "fhir")
        config_path : str — konfigurācijas fails (rules.yml)
        out_dir : str     — izvades direktorija

    Atgriež:
        (df_cleaned, issues_df, metrics_dict)
    """
    start_time = datetime.now()

    # 1. Konfigurācijas ielāde un datu avota izvēle
    cfg = load_config(config_path)
    loader = LOADERS.get(kind)
    if not loader:
        raise ValueError(f"Neatbalstīts formāts: {kind}")

    df_raw = loader(input_path)
    if df_raw.empty:
        raise ValueError("Datu kopa ir tukša vai netika pareizi ielādēta.")

    os.makedirs(out_dir, exist_ok=True)

    # 2. MI Schema Learning (ja iespējots konfigurācijā)
    learned_schema = {}
    if cfg.get("ai_schema_learning", {}).get("enabled", False):
        print("Palaiž SchemaLearner datu struktūras analīzei...")
        learner_cfg = cfg["ai_schema_learning"]
        learner = SchemaLearner(model_name=learner_cfg["model_name"])
        learned_schema = learner.infer_roles(df_raw)
        learner.save_results(learned_schema, learner_cfg["outputs"]["learned_schema"])
        print(f"SchemaLearner rezultāti saglabāti: {learner_cfg['outputs']['learned_schema']}")

    # 3. Sākotnējās metriku bāzes (pirms apstrādes)
    metrics_before_df = df_raw.copy()

    # 4. AI-atbalstītā datu kvalitātes apstrādes plūsma
    df_r = ReusabilityAgent(cfg).run(df_raw)
    df_c = CompletenessAgent(cfg).run(df_r)
    issues = PrecisionAgent(cfg).run(df_c)

    # 5. Metriku aprēķins pēc apstrādes
    metrics = compute_metrics(metrics_before_df, df_c, cfg)
    metrics["ai_schema_learning"] = {
        "enabled": cfg.get("ai_schema_learning", {}).get("enabled", False),
        "columns_learned": len(learned_schema),
    }

    # 6. Rezultātu saglabāšana
    df_c.to_csv(f"{out_dir}/cleaned.csv", index=False)
    issues.to_csv(f"{out_dir}/issues.csv", index=False)
    with open(f"{out_dir}/metrics_before_after.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    # 7. FAIR reproducējamības metadati
    meta = {
        "timestamp": datetime.now().isoformat(),
        "input_path": input_path,
        "config_used": config_path,
        "records_processed": len(df_c),
        "issues_detected": len(issues),
        "metrics_available": list(metrics.keys()),
        "ai_learning": "enabled" if learned_schema else "disabled",
        "run_duration_sec": (datetime.now() - start_time).total_seconds(),
    }
    with open(f"{out_dir}/meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    # 8. Kopsavilkums
    print("healthdq-ai pipeline pabeigts!")
    print(f"Ierakstu skaits: {len(df_c)}")
    print(f"Atrasti pārkāpumi: {len(issues)}")
    if learned_schema:
        print(f"MI atpazītas kolonnas: {len(learned_schema)}")
    print(f"Rezultāti saglabāti: {out_dir}/")

    return df_c, issues, metrics
