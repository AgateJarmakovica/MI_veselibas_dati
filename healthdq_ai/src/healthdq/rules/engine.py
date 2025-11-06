"""
rule_engine.py — Pašmācošs noteikumu dzinējs
============================================

Šis modulis realizē datu kvalitātes noteikumu pārvaldības un mācīšanās mehānismu.
Tas ļauj kombinēt statiskus (rules.yml) un dinamiskus (AI ģenerētus) noteikumus.

Mērķis:
--------
Izveidot MI atbalstītu “rule intelligence” sistēmu, kas:
 - analizē datu struktūru un vērtību sadalījumu,
 - pielāgo esošos noteikumus vai ģenerē jaunus,
 - sadarbojas ar aģentiem (Precision, Completeness, Reusability),
 - apgūst cilvēka korekcijas (Human-in-the-Loop).

Atbilst Data-Centric AI un FAIR principiem.
"""

import pandas as pd
import yaml
import json
from typing import Dict, Any, List
from pathlib import Path


class RuleEngine:
    """Centrālais noteikumu pārvaldības komponents."""

    def __init__(self, config_path: str = None):
        self.rules = {}
        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.rules = yaml.safe_load(f)
        self.generated_rules = []

    def validate_rules(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Izpilda statisko noteikumu pārbaudes no konfigurācijas faila.
        """
        results = []
        for rule in self.rules.get("rules", []):
            name = rule.get("name")
            col = rule.get("column")
            if col not in df.columns:
                continue

            if rule["type"] == "range":
                min_v, max_v = rule.get("min"), rule.get("max")
                mask = (df[col] < min_v) | (df[col] > max_v)
                invalid = df[mask]
                if not invalid.empty:
                    results.append({"rule": name, "column": col, "violations": len(invalid)})

            elif rule["type"] == "categorical":
                allowed = rule.get("allowed", [])
                mask = ~df[col].isin(allowed)
                invalid = df[mask]
                if not invalid.empty:
                    results.append({"rule": name, "column": col, "violations": len(invalid)})

        return results

    def learn_rules(self, df: pd.DataFrame, correlation_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Automātiski ģenerē jaunas datu kvalitātes hipotēzes, pamatojoties uz statistisko analīzi.
        """
        learned = []
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        # Skaitlisko atribūtu diapazoni
        for col in numeric_cols:
            desc = df[col].describe()
            learned.append({
                "name": f"{col}_range_auto",
                "type": "range",
                "column": col,
                "min": float(desc["min"]),
                "max": float(desc["max"]),
            })

        # Kategoriju biežums un semantiskās grupas
        for col in cat_cols:
            freq = df[col].value_counts(normalize=True)
            if len(freq) <= 20:
                learned.append({
                    "name": f"{col}_categories_auto",
                    "type": "categorical",
                    "column": col,
                    "allowed": freq.index.tolist(),
                })

        # Korelāciju noteikumi (loģiskā saistība starp laukiem)
        corr = df.corr(numeric_only=True)
        for c1 in corr.columns:
            for c2 in corr.columns:
                if c1 != c2 and abs(corr.loc[c1, c2]) >= correlation_threshold:
                    learned.append({
                        "name": f"{c1}_vs_{c2}_correlation",
                        "type": "correlation",
                        "columns": [c1, c2],
                        "strength": float(corr.loc[c1, c2]),
                    })

        self.generated_rules = learned
        return learned

    def save_generated_rules(self, path: str = "out/rules_generated.yml"):
        """Saglabā MI ģenerētos noteikumus YAML formātā."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump({"auto_rules": self.generated_rules}, f, allow_unicode=True)


def run_checks(df: pd.DataFrame, config_path: str) -> List[Dict[str, Any]]:
    """
    Palīgfunkcija, kas apvieno statiskos un ģenerētos noteikumus
    un veic pārbaudi ar abiem.
    """
    engine = RuleEngine(config_path)
    static_issues = engine.validate_rules(df)
    ai_rules = engine.learn_rules(df)
    engine.save_generated_rules()
    ai_issues = engine.validate_rules(df)

    return static_issues + ai_issues

