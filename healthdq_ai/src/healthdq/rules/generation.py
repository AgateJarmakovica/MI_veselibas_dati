"""
rule_generation.py — automātiska noteikumu ģenerēšana no pašmācības rezultātiem
===============================================================================

Šis modulis pārvērš iemācīto datu struktūru (no UniversalSchemaLearner)
par vispārīgu YAML konfigurāciju, ko var izmantot noteikumu dzinējs (engine.py).

Mērķis:
--------
- Atbalstīt jebkuras datu kopas struktūru
- Nodrošināt reproducējamu, AI ģenerētu noteikumu konfigurāciju
- Atbalstīt Data-Centric AI principus: reproducējamība, caurredzamība, adaptīva mācīšanās

Izvade:
--------
Izveido failu "out/rules_generated.yml", kas satur:
  - pamata metadatus,
  - ieteiktos noteikumus,
  - automātiski noteiktas kvalitātes dimensijas
"""

import yaml
import json
from pathlib import Path
import datetime


def generate_yaml_from_learned_rules(
    learned_rules_path="out/rules_generated.json",
    ontology_path="out/ontology.json",
    out_path="out/rules_generated.yml"
):
    """Izveido YAML konfigurāciju no AI iemācītajiem noteikumiem."""

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    # Ielādē mācītos datus
    try:
        with open(learned_rules_path, "r", encoding="utf-8") as f:
            learned = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("Nav atrasti iemācītie noteikumi. Vispirms palaid SchemaLearner vai UniversalSchemaLearner.")

    ontology = {}
    if Path(ontology_path).exists():
        with open(ontology_path, "r", encoding="utf-8") as f:
            ontology = json.load(f)

    # Izveido YAML struktūru
    config = {
        "metadata": {
            "title": "AI-generated Data Quality Rules",
            "description": "Automatically generated rule configuration from UniversalSchemaLearner",
            "generated_at": datetime.datetime.now().isoformat(),
            "source_files": {
                "learned_rules": learned_rules_path,
                "ontology": ontology_path,
            },
            "model_type": "unsupervised-schema-learning",
            "fair_principles": ["Findable", "Accessible", "Interoperable", "Reusable"],
        },
        "quality_dimensions": {
            "precision": [],
            "completeness": [],
            "reusability": []
        },
        "rules": [],
    }

    # --- Noteikumu ģenerēšana ---
    for entry in learned:
        if not isinstance(entry, dict):
            continue

        col = entry.get("column", "unknown_column")
        dtype = entry.get("dtype", "unknown")
        summary = entry.get("summary", {})

        # Numeriskās kolonnas -> precision / range
        if "float" in dtype or "int" in dtype:
            config["quality_dimensions"]["precision"].append({
                "column": col,
                "type": "range_check",
                "min": summary.get("min"),
                "max": summary.get("max"),
                "mean": summary.get("mean"),
                "std": summary.get("std"),
            })
            config["rules"].append({
                "name": f"{col}_range_rule",
                "type": "range",
                "column": col,
                "min": summary.get("min"),
                "max": summary.get("max"),
                "dimension": "precision"
            })

        # Teksta kolonnas -> categorical / pattern
        elif "object" in dtype:
            pattern = summary.get("pattern", "free_text")
            common = summary.get("most_common", [])
            config["quality_dimensions"]["reusability"].append({
                "column": col,
                "type": "categorical_standardization",
                "most_common": common,
                "pattern": pattern
            })
            config["rules"].append({
                "name": f"{col}_categorical_rule",
                "type": "categorical",
                "column": col,
                "allowed": common,
                "dimension": "reusability"
            })

        # Datumi
        elif "datetime" in dtype:
            config["quality_dimensions"]["precision"].append({
                "column": col,
                "type": "date_range",
                "min_date": summary.get("min_date"),
                "max_date": summary.get("max_date"),
            })
            config["rules"].append({
                "name": f"{col}_date_range_rule",
                "type": "date_range",
                "column": col,
                "min": summary.get("min_date"),
                "max": summary.get("max_date"),
                "dimension": "precision"
            })

        # Missing data info
        missing_count = summary.get("missing", 0)
        if missing_count > 0:
            config["quality_dimensions"]["completeness"].append({
                "column": col,
                "type": "missing_data_check",
                "missing": missing_count
            })
            config["rules"].append({
                "name": f"{col}_missing_rule",
                "type": "completeness",
                "column": col,
                "missing": missing_count,
                "dimension": "completeness"
            })

    # Pievieno semantisko informāciju, ja pieejama
    if ontology.get("terms"):
        config["semantic_model"] = {
            "learned_terms": ontology["terms"][:20],  # tikai pirmie 20 vispārīgie jēdzieni
            "embedding_size": len(ontology.get("embeddings", []))
        }

    # Saglabā YAML failu
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)

    print(f"Noteikumu konfigurācija veiksmīgi izveidota: {out_path}")
    return config


# ----------------------------------------------------------
# CLI vai pipeline izmantošanai
# ----------------------------------------------------------
if __name__ == "__main__":
    cfg = generate_yaml_from_learned_rules()
